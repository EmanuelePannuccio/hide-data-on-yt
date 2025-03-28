class Bytes:
    @classmethod
    def convertToBinaryString(cls, string, delimiter=""):
        return delimiter.join(f"{ord(s):08b}" for s in string)

    @classmethod
    def convertBinaryStringToInt(cls, byte):
        return int(byte,2)
    
    @classmethod
    def convertBinaryToString(cls, bytes):
        return "".join([chr(b) for b in bytes])

    @classmethod
    def group(cls, array_bytes, n=8):
        return [ array_bytes[i:i+n] for i in range(0, len(array_bytes),n) ]
    
    @classmethod
    def pprintBytes(cls, b, separator=" "):
        print(separator.join(b))

    @classmethod
    def convertIntToByteString(cls, num, bytes_pad=1):
        # return '{:08b}'.format(num)
        bytes_pad *= 8
        return cls.padByteString('{:08b}'.format(num), bytes_pad)

    @classmethod
    def padByteString(cls, st, quant=8):
        if quant % 8 != 0: 
            raise Exception("Quant not multiple of 8")

        remainder = len(st) % quant
        if remainder == 0: return st
        
        return '0'*(quant-remainder)+st

    @classmethod
    def join(cls,bytes :list, sep=""):
        return sep.join(bytes)