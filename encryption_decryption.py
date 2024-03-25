from Crypto.Cipher import AES
import os
import binascii
import mysql.connector

# get iv(initialization vector) of each application from the user's table
def get_iv(table_name):
    connector = mysql.connector.connect(host='localhost', user='bharadh', password='Bharadh#mysql', database='pwd_manager')
    cursor = connector.cursor()
    sql_command_iv = "select iv from {}".format(table_name)
    cursor.execute(sql_command_iv)
    iv = cursor.fetchall()

    return iv

# encrypt account details entered by the user using an iv
def encryption(key, to_encrypt, iv=os.urandom(16)):
    padded = pad_text(to_encrypt)
    for i in range(len(padded)):
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        padded[i] = binascii.hexlify(cipher.encrypt(padded[i].encode('utf-8'))).decode('utf-8')

    return padded, binascii.hexlify(iv).decode('utf-8')

# encrypt the account details enterd by the user with the iv's present in the table
# this is to check is a certain account exist in the table since all the accounts are stored encrypted as hexadecimals 
def encrypt_using_iv(key, to_encrypt, table_name):
    iv = get_iv(table_name)
    to_encrypt = pad_text(to_encrypt)
    encrypted = []
    for i in range(len(to_encrypt)):
        for j in range(len(iv)):
            cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, binascii.unhexlify(iv[j][-1]))
            encrypt = binascii.hexlify(cipher.encrypt(to_encrypt[i].encode('utf-8'))).decode('utf-8')
            encrypted.append(encrypt)

    return str(tuple(encrypted)).strip('(),')

# decrypts the details returned from the table 
def decryption(key, to_decrypt):
    for i in range(len(to_decrypt)):
        to_decrypt[i] = list(to_decrypt[i])

        for j in range(len(to_decrypt[i])):
            to_decrypt[i][j] = binascii.unhexlify(to_decrypt[i][j])

        for k in range(len(to_decrypt[i])-1):
            cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC,to_decrypt[i][len(to_decrypt[i])-1])
            to_decrypt[i][k] = cipher.decrypt(to_decrypt[i][k]).decode('utf-8')

    to_decrypt = unpad_text(to_decrypt)
    return to_decrypt

# pad text with spaces before encryption since the text to be encrypted must be divisible 16
def pad_text(to_pad):
    for i in range(len(to_pad)):
        while len(to_pad[i]) % 16 != 0:
            to_pad[i] += " "

    return to_pad

# unpad the text after decryption 
def unpad_text(to_unpad):
    for i in range(len(to_unpad)):
        for j in range(len(to_unpad[i])-1):
            to_unpad[i][j] = to_unpad[i][j].strip(" ")
    return to_unpad
 