import segno
from utils import Options
import numpy as np
import matplotlib.pyplot as plt

from classes.utils.Bytes import Bytes
from classes.DCTSteganography import VideoSteganography
import logging, cv2
from math import ceil

class ImageEncoder:
    
    @classmethod
    def decode(cls, frame):
        steganography = VideoSteganography()
        bytes_ = steganography.decode(frame)
        
        return bytes_

    @classmethod
    def encode(cls, bytes_, frame, frame_index):
        steganography = VideoSteganography()
        secret_data = np.array(bytes_, dtype=np.uint8)
        secret_data = np.pad(secret_data, (0, Options.WRITABLE_BYTES - len(secret_data)), "constant", constant_values=0)

        encoded_frame = steganography.encode(frame, frame_index, secret_data)
        return encoded_frame