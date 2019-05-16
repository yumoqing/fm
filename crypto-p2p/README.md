# Crypto-p2p
This module provide the data encrypt and decrypt function p2p

## Public key center(pkc)

download pkc's public key from pkc's  website and save it to file

generates ssl private key and public key, and save them to file, and upload public key to pkc on website

## Crypto process

### Encrypt

1. Get receiver's public key from key center, if sender not has it.

When a Node(A) want to send a bytes data to other node(B) , A check if it has Node B's public key, if not, it gets the Node B's public key from public key center(www.publicky.cc)

2. Generate a random symmetric key, use it to encrypt the data

3. encrypt the symmetric key with receiver's public key

4. using sender's private key to sign encrypted data,generate a sign data

5. pack it to a json data:
{
	'sender':A,
	"key":"encryptedkey",
	"receiver':B,
	'data':encypteddata,
	'sign':signedtext
} 

6. using trasnfer level function to send to json data to receiver

### Decrypt

1. receiver the json data fro sender

2. get sender's public key from key center, if it not has sender's public key

3. using sender's public key to check the sender's sign data

4. if sign data mismatch, discard the data, abort

5. decrypt the key using receiver's private key

6. using the decrypted  symmetric key to decryt the encrypted data

7. return the decrypted data


