import mysql.connector
import os
import hashlib
import binascii
import string
import menu

# connect to the password manager database
connector = mysql.connector.connect(host='localhost', user='bharadh', password='Bharadh#mysql', database='pwd_manager')
cursor = connector.cursor()

# obtain all the user info
sql_command_users = "select * from users"
cursor.execute(sql_command_users)
user_info = cursor.fetchall()

# ask the user if they want to login or signup
def choice():
    print("Welcome to your password manager")
    while True:
        ask_user = input("\nDo you want to 1.login or 2.signup : ")
        if ask_user == '1':
            return username_login()
        elif ask_user == '2':
            return username_signup()
        else:
            print("\nTry again.Enter 1 or 2")
            continue

# ask user for a username and check if username already exist to ensude duplicate accounts are not create
def username_signup():
    username = input("\nEnter an username for your account : ")

    if len(username) < 4:
        print("\nThe username must contain at least 4 characters")
        return username_signup()
    elif " " in username:
        print("\nThe username must not conatin a space")
        return username_signup()

    for i in user_info:
        if username == i[0]:
            print("\nThe username is already taken.Try again")
            return username_signup()
    else:
        print("\nYour password must contain\n"
              "at least 10 characters\n"
              "at least 1 digit\n"
              "at least 1 uppercase and 1 lowercase character\n"
              "at least 1 special character\n"
              "no spaces")
        return password_signup(username)

# ask user for a secure password and check if the password eneterd contains certain characteristics
def password_signup(username):
    password = input("\nEnter a password for your account : ")

    password_error_message = ""
    if len(password) < 10:
        password_error_message += "doesn't contain 10 characters\n"
    if any(i.isdigit() for i in password) == False:
        password_error_message += "doesn't contain a digit\n"
    if any(i.isupper() for i in password) == False:
        password_error_message += "doesn't contain a uppercase character\n"
    if any(i.islower() for i in password) == False:
        password_error_message += "doesn't contain a lowercase character\n"
    if any(i in string.punctuation for i in password) == False:
        password_error_message += "doesn't contain a special character\n"
    if " " in password:
        password_error_message += "contain's a space"

    if password_error_message == "":
        re_password = input("Re-enter your password : ")
        if re_password == password:
            return hash_vault_key_table_name(username, re_password)
        else:
            print("\nThe passwords entered doesn't match")
            return password_signup(username)
    else:
        print("\nYour password : \n", password_error_message)
        return password_signup(username)

# hash the password with a salt create a vault key and derive the table name using the vault key and password to ensure that the tables of a
# certain user cannot be found
def hash_vault_key_table_name(username, password):
    salt = hashlib.sha256(os.urandom(64)).hexdigest().encode('utf-8')
    hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)).decode('utf-8')

    vault_key = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', (username+password).encode('utf-8'), salt, 100000)).decode('utf-8')

    table_name = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', (vault_key+password).encode('utf-8'), salt, 100000)).decode('utf-8')

    return store_info_create_table(username, vault_key[:32], binascii.hexlify(salt).decode('utf-8'), hash, table_name[:64])

# store the username and hashed password with the salt and create a table for every new user
def store_info_create_table(username, key, salt, hash, table_name):
    sql_command_store_info = "insert into users values('{}','{}','{}')".format(username, salt, hash)
    cursor.execute(sql_command_store_info)
    connector.commit()

    sql_command_create_table = "create table {}(application_name varchar(64),username_email varchar(128),password varchar(64),iv char(32))".format(table_name)
    cursor.execute(sql_command_create_table)
    print("\nAccount created\n")

    return menu.greet(username, key, table_name)

# ask username of the user and check if the username exists
def username_login():
    count = 0

    def retry():
        while True:
            ask_user = input("\nDo you want to 1.try again 2.signup")
            if ask_user == '1':
                return username_login()
            elif ask_user == '2':
                return username_signup()
            else:
                print("\nTry again.Enter 1 or 2")
                continue
    while True:
        if count > 2:
            return retry()

        username = input("\nEnter your username : ")

        if len(username) < 4 or " " in username:
            print("\nThe username is invalid")
            count += 1
            continue

        for i in user_info:
            if username == i[0]:
                return password_login(username, i[1], i[2])
        else:
            print("\nThe username does not exist")
            count += 1
            continue

# ask user for password and hash the password with the salt from the table
# if the hash is same the user is allowed access
# if the hash is not same the user will be asked to try again or signup
def password_login(username, salt, hash):
    count = 0

    def retry():
        while True:
            ask_user = input("\nDo you want to 1.try again 2.re-enter username 3.signup")
            if ask_user == '1':
                return password_login(username, salt, hash)
            elif ask_user == '2':
                return username_login()
            elif ask_user == '3':
                return username_signup()
            else:
                print("\nTry again.Enter 1 2 or 3")
                continue
    while True:
        if count > 2:
            return retry()

        password = input("Enter your password : ")

        if len(password) < 10 or " " in password:
            count += 1
            print("\nThe password is invalid")
            continue

        password_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), binascii.unhexlify(salt), 100000)).decode('utf-8')

        if password_hash == hash:
            vault_key = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', (username+password).encode('utf-8'), binascii.unhexlify(salt), 100000)).decode('utf-8')
            table_name = binascii.hexlify(hashlib.pbkdf2_hmac('sha512', (vault_key+password).encode('utf-8'), binascii.unhexlify(salt), 100000)).decode('utf-8')
            print("\naccess granted\n")
            return menu.greet(username, vault_key[:32], table_name[:64])

        else:
            count += 1
            print("Incorrect password")
            continue


choice()
