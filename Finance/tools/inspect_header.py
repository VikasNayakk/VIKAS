import sys, binascii
p = sys.argv[1]
with open(p,'rb') as f:
    b = f.read(32)
print('bytes_read:', len(b))
print('hex:', binascii.hexlify(b))
print('starts with PK (50 4b):', b.startswith(b'PK'))
print('starts with D0 CF 11 E0:', binascii.hexlify(b).startswith(b'd0cf11e0'))
