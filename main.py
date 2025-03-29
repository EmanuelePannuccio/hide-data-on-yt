
from os import remove,listdir
from time import sleep, time
from glob import glob
from utils import Options
from pathlib import Path

import yt_dlp
import argparse, logging
import os

from classes.YouTubeUploader import YouTubeUploader
from classes.VideoEncoder import VideoEncoder

logging.basicConfig(level=logging.INFO)

class Decoder: 
    def __init__(self, path):
        self.__path = path

    def decode(self):
        VideoEncoder.decode(self.__path)

class Encoder: 
    def __init__(self, path):
        self.__path = path

    def encode(self, video_filename="test", codec="mp4v"):
        return VideoEncoder.encode(video_filename, codec)

def upload_video(video_filename):

    youtube = YouTubeUploader()

    video = youtube.upload_video(
        video_filename, 
        "[ {} ] YIGS - Exam showcase - {}".format(
            "ENCRYPTED" if Options.CRYPTOGRAPHY else "PLAIN", 
            "( {} BS - {} PX DENSITY - {} )".format(Options.DCT_STRENGTH, Options.PIXEL_DENSITY, Options.BLOCK_SIZE, video_filename)
        ), 
        "Only for multimedia project -- testing", 
        [], 
        privacy_status="unlisted"
    )

    return video

def download_video(path, video):
    yt_opts = {
        'verbose': True,
        'format': 'bestvideo[ext=mp4]/best[ext=mp4]/best',
        'outtmpl': path
    }

    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        while True:
            try:
                ydl.download("https://www.youtube.com/watch?v={}".format(video))
                break
            except Exception as e:
                print(e)
                print("Waiting 10s before retrying...")
                sleep(10)
    return path

def main(action, filename, cryptography, pixel_density, dct_block_size=8, dct_bit_strength=100, mask_video="mask_.mp4", yt_video=None):

    Options.bootstrap(cryptography=cryptography, pixel_density=pixel_density, dct_bit_strength=dct_bit_strength, dct_block_size=dct_block_size, mask_video=mask_video)

    print(vars(Options))
    
    # Encoding

    print("Elaborazione {} di {}".format(action, filename))

    if action == "encode":
        video_filename = os.path.basename(filename)
        e = Encoder("./archive")
        e.encode(video_filename=video_filename)
        
        # for f in glob("./archive/*"): remove(f)
        # upload_video(video_filename)        
    elif action == "decode":
        # if yt_video is None: raise Exception("You must insert a Youtube Video Link!")
        # download_video(filename, yt_video)

        # Decoding
        for f in glob("./restore/*"): remove(f)
        print(filename)
        d = Decoder(filename)
        d.decode()
    
# Set up argument parser
parser = argparse.ArgumentParser(description="Encode or decode a video file.")

parser.add_argument("action", choices=["encode", "decode"], help="Action to perform: encode or decode")
parser.add_argument("--filename", type=str, help="The filename to encode or decode")
parser.add_argument("--cryptography", action="store_true", help="Enable cryptography")
parser.add_argument("--pixel-density", type=int, help="Set the pixel density as an integer")
parser.add_argument("--dct-block-size", default=8, type=int, help="Set the DCT block size as an integer")
parser.add_argument("--dct-bit-strength", default=25, type=int, help="Set the DCT bit strength as an integer")
parser.add_argument("--mask-video", default="mask_.mp4", help="Set the mask video")
parser.add_argument("--yt-video", help="Set the pixel density as an integer")

# Parse arguments
args = vars(parser.parse_args())

main(**args)