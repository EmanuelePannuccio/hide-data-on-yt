import math

class Options:
    WIDTH=1920
    HEIGHT=1080
    PASSWORD="supercalifragili"
    CRYPTOGRAPHY=True
    
    @classmethod
    def find_longest_bytes_len(cls, n):
        found = False
        while not found:
            div_in_dupl_bytes : float = n / (Options.PIXEL_DENSITY**2)

            if not div_in_dupl_bytes.is_integer():
                n -= 1
                continue
            
            div_in_bytes : float = div_in_dupl_bytes / 8

            if not div_in_bytes.is_integer():
                n -= 1
                continue
            
            sqrt = math.sqrt(n)

            if not sqrt.is_integer():
                n -= 1
                continue

            found = True

        return int(( n / (Options.PIXEL_DENSITY**2) ) / 8) 
    
    @classmethod
    def bootstrap(cls, cryptography=True, pixel_density=4, dct_block_size=8, dct_bit_strength=25, mask_video="mask_.mp4"):
        cls.CRYPTOGRAPHY=cryptography
        cls.PIXEL_DENSITY=pixel_density
        cls.BLOCK_SIZE=dct_block_size
        cls.DCT_STRENGTH=dct_bit_strength
        cls.MASK_VIDEO=mask_video
        cls.SHOW_FRAMES=False
    
    @classmethod
    def calculateVideoStegParams(cls, width, height):
        cls.WIDTH = width
        cls.HEIGHT = height
        cls.PIXEL_PER_WIDTH=cls.WIDTH // cls.BLOCK_SIZE
        cls.PIXEL_PER_HEIGHT=cls.HEIGHT // cls.BLOCK_SIZE 
        cls.TOTAL_BYTES_PER_FRAME=((cls.PIXEL_PER_WIDTH) * (cls.PIXEL_PER_HEIGHT)) * 2

        cls.WRITABLE_BYTES=cls.find_longest_bytes_len(cls.TOTAL_BYTES_PER_FRAME)