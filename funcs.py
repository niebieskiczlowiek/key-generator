from Crypto.PublicKey import ECC
from ecpy.ecdsa import ECDSA
import ecdsa 


def generate_keypair():
    key = ECC.generate(curve='P-256')
    f = open('keys/private.pem', 'wt')
    f.write(key.export_key(format='PEM'))
    f.close()

    f = open('keys/public.pem', 'wt')
    f.write(key.public_key().export_key(format='PEM'))
    f.close()

# public_key = open('keys/public.pem', 'rb').read()
# private_key = open('keys/private.pem', 'rb').read()

def signFile(private_key, public_key, filename):
    # sign_key = ecdsa.SigningKey.generate()
    file = open(filename, 'rb').read()
    # sign_key = ecdsa.SigningKey.from_pem(private_key)

    # signature = sign_key.sign(file)

    sk = ecdsa.SigningKey.from_pem(private_key)
    # vk = sk.get_verifying_key()
    vk = ecdsa.VerifyingKey.from_pem(public_key)
    signature = sk.sign(file)

    # f = open('signed', 'wb') 
    # f.write(signature)
    # f.close()
    return signature

def verifyFile(vk, ogFile, signFile):
    originalFile = open(ogFile, 'rb').read()
    signedFile = open(signFile, 'rb').read()
    public_key = open(vk, 'rb').read()

    verifying_key = ecdsa.VerifyingKey.from_pem(public_key)

    # signedFile = bytes.fromhex(signedFile.hex())

    # pubkey = sign_key.verifying_key
    
    return verifying_key.verify(originalFile, signedFile)

# verify(sig, sig_key, 'signed')

# vk = sign(private_key, public_key, 'toSign.txt')

# verify(vk, 'toSign.txt', 'signed')