from Crypto.Cipher import AES as crypto
from Crypto.Util.Padding import pad, unpad

class AES:
    
    def encrypt(self, data, key):
        cipher = crypto.new(key, crypto.MODE_ECB)
        encrypted_data = cipher.encrypt(pad(data,crypto.block_size))
        return encrypted_data

    def decrypt(self, data, key):
        cipher = crypto.new(key, crypto.MODE_ECB)
        decrypted_data = unpad(cipher.decrypt(data),crypto.block_size)
        return decrypted_data