import subprocess

class SymmetricEncrypter:
    def __init__(self, password : str):
        self.__password = password

    def crypt(self, file_path, output_path):
        try:
            # Costruisce il comando OpenSSL per cifrare il file
            command = [
                'openssl', 'enc', '-aes-256-cbc', '-salt', '-in', file_path,
                '-out', output_path, '-pbkdf2', '-k',  self.__password
            ]
            # Esegue il comando
            subprocess.run(command, check=True)
            print(f"File '{file_path}' cifrato e salvato come '{output_path}'.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante la cifratura del file: {e}")

    
    def decrypt(self, encrypted_file_path, output_path):
        try:
            # Costruisce il comando OpenSSL per decifrare il file
            command = [
                'openssl', 'enc', '-d', '-aes-256-cbc', '-in', encrypted_file_path,
                '-out', output_path, '-pbkdf2', '-k',  self.__password
            ]
            # Esegue il comando
            subprocess.run(command, check=True)
            print(f"File '{encrypted_file_path}' decifrato e salvato come '{output_path}'.")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante la decifratura del file: {e}")

