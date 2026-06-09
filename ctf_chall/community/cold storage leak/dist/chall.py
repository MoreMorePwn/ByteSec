import random
import math

def get_keys(num_bits):
    jump_bits = 512

    priv_key = []
    current_sum = 0
    for _ in range(num_bits):
        val = current_sum + random.randint(1, 2**jump_bits)
        priv_key.append(val)
        current_sum += val
    
    q = current_sum + random.randint(1, 2**jump_bits)
    
    r = random.randint(2, q - 1)
    while math.gcd(r, q) != 1:
        r = random.randint(2, q - 1)
    
    pub_key = [(w * r) % q for w in priv_key]
    
    return pub_key, priv_key, q, r

def encrypt(message_bytes, pub_key):
    binary_msg = ''.join([bin(b)[2:].zfill(8) for b in message_bytes])
    
    ciphertext = 0
    for i in range(len(binary_msg)):
        if binary_msg[i] == '1':
            ciphertext += pub_key[i]
            
    return ciphertext

if __name__ == '__main__':
    with open("flag.txt", "rb") as f:
        flag = f.read().strip()
        
    num_bits = len(flag) * 8
    pub_key, priv_key, q, r = get_keys(num_bits)
    
    ciphertext = encrypt(flag, pub_key)
    
    with open("output.txt", "w") as f:
        f.write(f"pub_key = {pub_key}\n")
        f.write(f"ciphertext = {ciphertext}\n")