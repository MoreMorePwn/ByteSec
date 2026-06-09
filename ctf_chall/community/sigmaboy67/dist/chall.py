from Crypto.Util.number import getPrime, bytes_to_long
import secrets

with open("flag.txt", "rb") as f:
    m = bytes_to_long(f.read())

p = getPrime(512)
q = getPrime(512)
n = p * q
e = 65537

x = secrets.randbits(128)
nothing = x >> 24
also_nothing = p*p + x*p + x

c = pow(m, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = {c}")
print(f"a = {nothing}")
print(f"b = {also_nothing}")