import cv2
import numpy as np
from scipy.fft import dct, idct, dctn

from utils import Options
import math


class VideoSteganography:
    COEF_POSITIONS=[(4,4), (5,5)]

    def __init__(self):
        self.__channel_idx = 0 
        self.__block_size = Options.BLOCK_SIZE
        self.__bit_redundancy = Options.PIXEL_DENSITY
        self.__embedding_strength = Options.DCT_STRENGTH

    def dct_embed_block(self, block, bit_sequence):
        """Incorpora dati in un singolo blocco DCT"""
        coeffs = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
        
        for i, (x,y) in enumerate(self.COEF_POSITIONS):
            normalized_val = np.sign(coeffs[x,y]) * (abs(coeffs[x,y]) // self.__embedding_strength * self.__embedding_strength)
            coeffs[x,y] = self.__embedding_strength * bit_sequence[i] + normalized_val
        
        return idct(idct(coeffs, axis=1, norm='ortho'), axis=0, norm='ortho')

    def encode(self, frame, frame_idx, secret_data):
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
        channel = ycrcb_frame[:, :, self.__channel_idx].astype(np.float32)

        height, width = channel.shape

        data_index = 0

        secret_data = np.unpackbits(np.frombuffer(secret_data, dtype=np.uint8))

        reshape_dim = math.sqrt(len(secret_data))

        assert reshape_dim.is_integer()
           
        reshape_dim = int(reshape_dim)

        secret_data = secret_data.reshape(reshape_dim, reshape_dim)

        secret_data = np.repeat(np.repeat(secret_data, self.__bit_redundancy, axis=0), self.__bit_redundancy, axis=1)
        
        secret_data = secret_data.flatten()

        num_block_w, num_block_h = int(width//self.__block_size), int(height//self.__block_size) # Posso rappresentare 2 bit in un blocco
        print(f"{frame_idx} frame: {len(secret_data)} <= {(num_block_w * num_block_h * 2)}")
        assert len(secret_data) <= (num_block_w * num_block_h * 2), "Not sufficient blocks to steganography data"

        for i in range(0, height, self.__block_size):
            for j in range(0, width, self.__block_size):
                data_secret = secret_data[data_index:data_index+len(self.COEF_POSITIONS)]

                if not len(data_secret): break

                block = channel[i:i+self.__block_size, j:j+self.__block_size]
                channel[i:i+self.__block_size, j:j+self.__block_size] = self.dct_embed_block(block, data_secret)
                data_index+=len(self.COEF_POSITIONS)

        ycrcb_frame[:,:,self.__channel_idx] = np.clip(channel, 0, 255).astype(np.uint8)
        embedded_image = cv2.cvtColor(ycrcb_frame, cv2.COLOR_YCrCb2RGB)

        return embedded_image

    def decode(self, frame):
        """
        Decodifica i dati segreti dal frame video (versione ottimizzata).
        """
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
        channel = ycrcb_frame[:, :, self.__channel_idx].astype(np.float32)
        height, width = channel.shape

        Options.calculateVideoStegParams(width, height)
        
        # Calcoliamo il numero totale di blocchi e preallochiamo l'array
        num_blocks_h = height // self.__block_size
        num_blocks_w = width // self.__block_size
        total_bits = num_blocks_h * num_blocks_w * len(self.COEF_POSITIONS)
        extracted_bits = np.zeros(total_bits, dtype=np.float32)
        
        idx = 0
        for i in range(0, height, self.__block_size):
            for j in range(0, width, self.__block_size):
                block = channel[i:i+self.__block_size, j:j+self.__block_size]
                bits = self.extract_data_optimized(block)
                extracted_bits[idx:idx+len(bits)] = bits
                idx += len(bits)

        # Limita ai bit scrivibili e applica le operazioni finali
        max_bits = Options.WRITABLE_BYTES * 8 * (Options.PIXEL_DENSITY ** 2)
        extracted_bits = extracted_bits[:max_bits]
        
        side = int(math.sqrt(len(extracted_bits)) // self.__bit_redundancy)
        extracted_bits = extracted_bits.reshape(side, self.__bit_redundancy, side, -1)
        extracted_bits = extracted_bits.mean(axis=(1, 3))
        extracted_bits = np.where(extracted_bits >= 0.5, 1, 0).flatten()

        secret_data = np.packbits(extracted_bits).tobytes()
        return secret_data

    def extract_data_optimized(self, block):
        """
        Estrae i bit segreti da un blocco (versione ottimizzata).
        """
        coeffs = dctn(block, norm='ortho')  # DCT multidimensionale
        x_coords, y_coords = zip(*self.COEF_POSITIONS)
        bits = np.round(coeffs[x_coords, y_coords] / self.__embedding_strength) % 2
        return bits.astype(np.float32)