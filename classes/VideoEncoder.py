from classes.encrypter.SymmetricEncrypter import SymmetricEncrypter
from classes.utils.System import get_available_memory
from classes.ImageEncoder import ImageEncoder
from classes.FileEncoder import FileEncoder

from utils import Options
from classes.utils.System import checkMemory
from classes.utils.Bytes import Bytes
import matplotlib.pyplot as plt
import numpy as np

from itertools import islice, repeat
from alive_progress import alive_bar
from math import ceil

import cv2, hashlib, os, json
from time import time
import numpy as np
from scipy.fftpack import dct, idct
import logging

import scipy.fftpack
import zipfile

import numpy as np
import cv2
import random


class VideoEncoder:
    def __init__(self, video_name="video"):
        self.__video_name = video_name

    # ENCODING

    def zip(self, directory_path, zip_name):
        os.makedirs("temp/", exist_ok=True)

        # Compress files
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    zipf.write(file_path, relative_path)
            
        return zip_name

    def unzip(self, zip_name, extract_to):
        # Ensure the extraction directory exists
        os.makedirs(extract_to, exist_ok=True)

        # Extract files
        with zipfile.ZipFile(zip_name, 'r') as zipf:
            zipf.extractall(extract_to)

        return extract_to

    def __generateBytesFromFiles(self):
        file = self.zip("./archive", "temp/archive.zip")

        yield file

        for byte in FileEncoder.encode(file):
            yield byte

    def __crypt_files(self):
        file = self.zip("./archive", "temp/archive.zip")
        
        cipher = SymmetricEncrypter(Options.PASSWORD)
        archive_crypt = "temp/archive.zip.crypt"
        cipher.crypt(file, archive_crypt)

        yield archive_crypt

        for byte in FileEncoder.encode(archive_crypt):
            yield byte
    
    def __encode(self, _bytes, codec, filename):
        # Define the output path and codec
        output_path = f"./{self.__video_name}"

        size = os.stat(filename).st_size

        fourcc = cv2.VideoWriter_fourcc(*codec) 

        mask_video = cv2.VideoCapture(filename=Options.MASK_VIDEO)
        width  = int(mask_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(mask_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(mask_video.get(cv2.CAP_PROP_FPS)) 
        total_frames = int(mask_video.get(cv2.CAP_PROP_FRAME_COUNT))

        Options.calculateVideoStegParams(width, height)
        stegano_frames = max(size // (Options.WRITABLE_BYTES), 1)

        assert stegano_frames <= total_frames
        print("Stegano frames: {}".format(stegano_frames))

        video = cv2.VideoWriter(output_path, fourcc, fps, (width,height))

        with alive_bar(total_frames, bar='filling', title="Masking data on Frame") as bar:
            while True:
                ret, cover_frame = mask_video.read()
                if not ret: break

                embed_bytes = list(islice(_bytes, Options.WRITABLE_BYTES))
                if len(embed_bytes) > 0:
                    stegano_frame = ImageEncoder.encode(embed_bytes, cover_frame, bar.current)
                else:
                    stegano_frame = cover_frame
                
                video.write(stegano_frame)
                bar()

            video.release()
            cv2.destroyAllWindows()

    @classmethod
    def encode(cls, video_name="video", codec = "mp4v"):
        print("""
███████ ███    ██  ██████  ██████  ██████  ██ ███    ██  ██████  
██      ████   ██ ██      ██    ██ ██   ██ ██ ████   ██ ██       
█████   ██ ██  ██ ██      ██    ██ ██   ██ ██ ██ ██  ██ ██   ███ 
██      ██  ██ ██ ██      ██    ██ ██   ██ ██ ██  ██ ██ ██    ██ 
███████ ██   ████  ██████  ██████  ██████  ██ ██   ████  ██████  
                                                                 
        """)
        
        os.makedirs("temp", exist_ok=True)

        v = VideoEncoder(video_name)
        if Options.CRYPTOGRAPHY: 
            fsbytes = v.__crypt_files()
        else:
            fsbytes = v.__generateBytesFromFiles()

        filename = next(fsbytes)

        return v.__encode(fsbytes, codec=codec, filename=filename)

    def __extract_frames(self):
        cap = cv2.VideoCapture(self.__video_name)
        if not cap.isOpened():
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        buffer = []

        file_tmp_path = "./temp/file.tmp"

        total_stegano_frames = 0

        calc_total_bytes = True

        with open(file_tmp_path, "wb+") as fp:
            with alive_bar(total_frames, bar='filling', title="Extract Frame") as bar:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    bs = ImageEncoder.decode(frame)
                    if calc_total_bytes:
                        filename_size = bs[0]
                        md5_size = 32
                        content_size_idx = filename_size + md5_size
                        content_size = int.from_bytes(bs[content_size_idx+1 : content_size_idx+7])

                        total_stegano_frames = max((filename_size + md5_size + content_size) // Options.WRITABLE_BYTES, 1)

                        calc_total_bytes = False

                    buffer += bs

                    if len(buffer) >= 2000:
                        fp.write(bytearray(buffer))
                        buffer.clear()
                    
                    if bar.current >= total_stegano_frames:
                        bar(total_frames - bar.current)
                        break

                    bar()

            cap.release()
            
            if buffer:
                fp.write(bytearray(buffer))
            buffer.clear()

        with open(file_tmp_path, "rb") as fp:
            while True:
                chunk = fp.read(4096)
                if not chunk:
                    break

                for b in chunk:
                    yield b

    def __decrypt_and_unzip(self, path):
        # Data to encrypt
        zip_filename = "restore/temp.zip"
        cipher = SymmetricEncrypter(Options.PASSWORD)

        cipher.decrypt(path, zip_filename)

        self.unzip(zip_filename, "restore/")

        os.remove(zip_filename)
        os.remove(path)
        
    def __decode_video(self, bytes_extracted):
        bytes_ = list(islice(bytes_extracted, 1))
        while bytes_:
            filename_len = bytes_[0]
            if filename_len == 0: break # Abbiamo finito i byte

            filename = list(islice(bytes_extracted, filename_len))
            filename = Bytes.convertBinaryToString(filename)

            md5 = list(islice(bytes_extracted, FileEncoder.MD5_SIZE))
            md5 = Bytes.convertBinaryToString(md5)
            
            content_len = list(islice(bytes_extracted, 6))
            content_len = Bytes.convertBinaryStringToInt(
                Bytes.join(
                    [Bytes.convertIntToByteString(num) for num in content_len]
                )
            )

            path = "./restore/restore_{}".format(filename)
            batch_size = 4096

            with alive_bar(content_len, bar='filling', title="Restoring zip") as bar, open(path, "wb+") as fp: 
                buffer = bytearray()
                for byte in islice(bytes_extracted, content_len):
                    byte: int
                    buffer.extend(byte.to_bytes())
                    bar()
                    
                    if len(buffer) >= batch_size:
                        fp.write(buffer)
                        buffer.clear()

                if buffer:  # Write any remaining bytes
                    fp.write(buffer)

            if md5 != hashlib.md5(open(path,'rb').read()).hexdigest(): 
                print("Il file {} non è stato ripristinato correttamente.".format(path))
                os.remove(path)
            else:
                print("Il file {} è stato ripristinato con successo!".format(path))
                yield path

            try:
                bytes_ = list(islice(bytes_extracted, 1))
            except:
                break

    def __decode(self):
        """
        Restore file from video
        """

        _bytes = self.__extract_frames()

        files = self.__decode_video(_bytes)
        
        if Options.CRYPTOGRAPHY: 
            for file in files:
                self.__decrypt_and_unzip(file)

    @classmethod
    def decode(cls, video_filename):
        print("""
██████  ███████  ██████  ██████  ██████  ██ ███    ██  ██████  
██   ██ ██      ██      ██    ██ ██   ██ ██ ████   ██ ██       
██   ██ █████   ██      ██    ██ ██   ██ ██ ██ ██  ██ ██   ███ 
██   ██ ██      ██      ██    ██ ██   ██ ██ ██  ██ ██ ██    ██ 
██████  ███████  ██████  ██████  ██████  ██ ██   ████  ██████  
                                                               
        """)

        os.makedirs("temp", exist_ok=True)

        v = VideoEncoder(video_filename)
        v.__decode()
