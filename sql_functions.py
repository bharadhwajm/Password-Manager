import binascii
import mysql.connector
import menu
import string
import encryption_decryption
import os

connector = mysql.connector.connect(host='localhost', user='bharadh', password='Bharadh#mysql', database='pwd_manager')
cursor = connector.cursor()

# count the number of accounts in the users vault 
def count_account(table_name):
    sql_command = "select count(application_name) from {}".format(table_name)
    cursor.execute(sql_command)
    accounts_count = cursor.fetchone()
    return accounts_count[0]

# check if the user's vault is empty
def check_table(key, table_name):
    sql_command = "select * from {}".format(table_name)
    cursor.execute(sql_command)
    accounts = cursor.fetchall()
    if cursor.rowcount > 0:
        return
    else:
        print("\nYour vault is empty")
        return menu.choice(key, table_name)

# view all accounts in the vault
# the contents in the vault are decrypted the printed
def view_all_accounts(key, table_name):
    check_table(key, table_name)
    sql_command = "select application_name,username_email,iv from {}".format(table_name)
    cursor.execute(sql_command)
    application_names = cursor.fetchall()
    application_names = encryption_decryption.decryption(key, application_names)
    print("\nAppications\t\t username\t\t")
    for i in range(len(application_names)):
        for j in range(len(application_names[i])-1):
            print(application_names[i][j], end='\t\t\t')
        print()

    return menu.choice(key, table_name)

# search for a specific account's details
# if account exist's the records returned from the vault are decrypted then printed
def search_specific_account(key, table_name):
    check_table(key, table_name)
    count = 0

    while True:
        if count > 2:
            retry(key, table_name)

        application_name = input("\nEnter the application's name : ")

        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in application_name) == False:
            print("\nThe application name is invalid")
            count += 1
            continue
        else:
            application_name = encryption_decryption.encrypt_using_iv(key, [application_name, ], table_name)
            sql_command_search = "select * from {} where application_name in ({})".format(table_name, application_name)
            cursor.execute(sql_command_search)
            applications = cursor.fetchall()

            if cursor.rowcount == 0:
                print("\nThe application entered does not exist in your vault")
                return menu.choice(key, table_name)
            else:
                applications = encryption_decryption.decryption(key, applications)
                print('\napplication\t\t\tusername/email\t\t\t\t\tpassword')
                for i in applications:
                    for j in i[:3]:
                        print(j, end='\t\t\t\t')
                    print()
                return menu.choice(key, table_name)

# add account to the vault 
# the details entered are encrypted the stored in the vault 
# if the account already exist the the vault the acccount is not added and the user is informed
# if password is reused user will be given choice to re-eneter password
def add_account(key, table_name):
    count = 0

    while True:
        if count > 2:
            retry(key, table_name)

        application_name = input("\nEnter the application's name : ")
        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in application_name) == False:
            count += 1
            print("\nThe application name cannot be empty")
            continue
        else:
            count=0
            break

    while True:
        if count > 2:
            retry(key, table_name)

        username_email = input("Enter the username or email of the account : ")
        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in username_email) == False:
            count += 1
            print("\nThe username/email cannt be left empty")
            continue
        else:
            if count_account(table_name) > 0:
                application_encrypted = encryption_decryption.encrypt_using_iv(key, [application_name,], table_name)
                username_email_encrypted=encryption_decryption.encrypt_using_iv(key,[username_email,],table_name)
                sql_command_check = "select application_name,username_email from {} where application_name in ({}) and username_email in ({})".format(table_name, application_encrypted, username_email_encrypted)
                cursor.execute(sql_command_check)
                accounts = cursor.fetchall()
                if cursor.rowcount > 0:
                    print("\nThe account already exists in your vault")
                    retry(key, table_name)
                    continue
                else:
                    count=0
                    break
            else:
                count=0
                break

    while True:
        if count > 2:
            retry(key, table_name)

        password = input("Enter the password for the account : ")
        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in password) == False:
            count += 1
            print("\nThe password cannot be left empty\n")
            continue
        else:
            if count_account(table_name)>0:
                check=check_passwords(key,password,table_name)
                if check==False or check==None:
                    break
                continue
            break
    try:
        encrypt_details = encryption_decryption.encryption(key, [application_name, username_email, password],os.urandom(16))
        sql_command_insert = "insert into {} values('{}','{}','{}','{}')".format(table_name, encrypt_details[0][0], encrypt_details[0][1], encrypt_details[0][2], encrypt_details[1])
        cursor.execute(sql_command_insert)
        connector.commit()
        print("\nThe account details has been added to your vault")
        return menu.choice(key, table_name)
    except mysql.connector.errors.DataError:
        print("\nThe input is too long.Try again")
        return add_account(key,table_name)

# update account information such as the application's name, username or password 
# if account already exist in the vault then the user will be asked to try again or go back to the menu
# if multiple accounts from an application exist, the user will be asked which one to update
# if password is reused user will be given choice to re-enter password
def update_account_details(key, table_name):
    check_table(key, table_name)
    count = 0

    def update_details(application_name, username_email, iv,username_email_unencrypted):
        nonlocal count
        while True:
            ask_user = input("\nWould you like to update:\n"
                             "1.application name\n"
                             "2.username/email\n"
                             "3.password\n")


            if ask_user == '1':
                while True:
                    new_application_name = input("Enter the new application name : ")
                    if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in new_application_name) == False:
                        print("\nThe application name cannot be left empty")
                        count += 1
                        if count > 2:
                            retry(key, table_name)
                            continue
                        continue
                    else:
                        check_application_name=encryption_decryption.encrypt_using_iv(key,[new_application_name,],table_name)
                        check_username_email=encryption_decryption.encrypt_using_iv(key,[username_email_unencrypted,],table_name)
                        sql_command_check="select * from {} where application_name in ({}) and username_email in ({})".format(table_name,check_application_name,check_username_email)
                        cursor.execute(sql_command_check)
                        accounts=cursor.fetchall()
                        if cursor.rowcount==0:
                            new_application_name = encryption_decryption.encryption(key, [new_application_name, ], binascii.unhexlify(iv))
                            if username_email == "":
                                sql_command = "update {} set application_name='{}' where application_name in ({})".format(table_name, new_application_name[0][0], application_name)
                                break
                            else:
                                sql_command = "update {} set application_name='{}' where username_email='{}' and application_name in ({})".format(table_name, new_application_name[0][0], username_email, application_name)
                                break
                        else:
                            print("\nThe account already exists in your account")
                            retry(key,table_name)
                            continue

            elif ask_user == '2':
                while True:
                    new_username_email = input("\nEnter the new username/email : ")
                    if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in new_username_email) == False:
                        print("\nThe username/email cannot be left empty")
                        count += 1
                        if count > 2:
                            retry(key, table_name)
                        continue
                    else:
                        new_username_email_encrypted = encryption_decryption.encryption(key, [new_username_email, ], binascii.unhexlify(iv))
                        if username_email == "":
                            sql_command = "update {} set username_email='{}' where application_name in ({})".format(table_name, new_username_email_encrypted[0][0], application_name)
                            break
                        else:
                            check_new_username_email = encryption_decryption.encrypt_using_iv(key, [new_username_email, ], table_name)
                            sql_command_check = "select username_email from {} where application_name in ({}) and username_email in ({}) ".format(table_name, application_name, check_new_username_email)
                            cursor.execute(sql_command_check)
                            accounts = cursor.fetchall()
                            if cursor.rowcount > 0:
                                print("\nThe username/email is already used")
                                retry(key, table_name)
                                continue
                            else:
                                sql_command = "update {} set username_email='{}' where application_name in ({}) and username_email='{}'".format(table_name, new_username_email_encrypted[0][0], application_name, username_email)
                                break

            elif ask_user == '3':
                while True:
                    new_password = input("\nEnter the new password : ")
                    if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in new_password) == False:
                        print("\nThe password cannot be left empty")
                        count += 1
                        if count > 2:
                            retry(key, table_name)
                        continue
                    else:
                        check=check_passwords(key,new_password,table_name)
                        if check==False or check==None:
                            new_password = encryption_decryption.encryption(key, [new_password, ], binascii.unhexlify(iv))
                            if username_email == "":
                                sql_command = "update {} set password='{}' where application_name in ({})".format(table_name, new_password[0][0], application_name)
                                break
                            else:
                                sql_command = "update {} set password='{}' where application_name in ({}) and username_email='{}'".format(table_name, new_password[0][0], application_name, username_email)
                                break
                        continue
            else:
                if count>2:
                    retry(key,table_name)
                    print("\nInvalid input")
                    continue
                else:
                    print("\nTry again.Enter 1 2 or 3")
                    count+=1
                    continue
            
            try:
                cursor.execute(sql_command)
                connector.commit()
                print("\nUpdated!")
                return menu.choice(key, table_name)

            except mysql.connector.errors.DataError:
                print("\nThe input is too long")
                return menu.choice(key,table_name)

    while True:
        application_name = input("\nEnter the application's name that you want to update : ")
        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in application_name) == False:
            print("\nThe application's name is invalid")
            count += 1
            if count > 2:
                retry(key, table_name)
            continue
        break

    application_name = encryption_decryption.encrypt_using_iv(key, [application_name, ], table_name)
    sql_command_check = "select application_name,username_email,iv from {} where application_name in ({})".format(table_name, application_name)
    cursor.execute(sql_command_check)
    accounts = cursor.fetchall()
    if cursor.rowcount > 0:
        if cursor.rowcount > 1:
            accounts = encryption_decryption.decryption(key, accounts)
            print("\napplication\t\tusername/email")
            for i in accounts:
                for j in i[:2]:
                    print(j, end='\t\t\t')
                print()

            while True:
                username_email = input("\nEnter the username/email of the account you want to update : ")
                if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in username_email) == False:
                    print("\nThe username entered is invalid")
                    count += 1
                    if count > 2:
                        retry(key, table_name)
                        continue
                    continue

                else:
                    for i in range(len(accounts)):
                        if username_email == accounts[i][1]:
                            encrypted_username_email_iv = encryption_decryption.encryption(key, [accounts[i][1], ], accounts[i][2])
                            return update_details(application_name, encrypted_username_email_iv[0][0], encrypted_username_email_iv[1],username_email)
                    else:
                        print("\nThe username entered is incorrect")
                        count += 1
                        if count > 2:
                            retry(key, table_name)
                        continue
        else:
            return update_details(application_name, "", accounts[0][2],encryption_decryption.decryption(key,[(accounts[0][1],accounts[0][2]),])[0][0])
    else:
        print("\nThe application does not exist in your vault")
        return menu.choice(key, table_name)

# deletes the account given by the user
# if multiple accounts from an aplication exists in the table,the user will be asked which one to delete 
def delete_details(key, table_name):
    check_table(key, table_name)
    count = 0

    while True:
        if count > 2:
            retry(key, table_name)

        account = input("\nEnter the application's name that you want to delete : ")
        if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in account) == False:
            print("\nThe application's name cannot be left empty")
            count += 1
            continue
        else:
            account = encryption_decryption.encrypt_using_iv(key, [account, ], table_name)
            sql_command_accounts = "select application_name,username_email,iv from {} where application_name in ({})".format(table_name, account)
            cursor.execute(sql_command_accounts)
            accounts = cursor.fetchall()
            if cursor.rowcount > 1:
                accounts = encryption_decryption.decryption(key, accounts)
                print("\napplication\t\tusername/email")
                for i in accounts:
                    for j in i[:2]:
                        print(j, end='\t\t\t')
                    print()

                while True:
                    if count > 2:
                        retry(key, table_name)

                    username_email = input("\nEnter the username/email of the account that you want to delete : ")
                    if any(i in string.ascii_letters or i in string.digits or i in string.punctuation for i in username_email) == False:
                        count += 1
                        print("\nThe username/email cannot be left empty")
                        continue
                    else:
                        for i in accounts:
                            if username_email == i[1]:
                                username_email = encryption_decryption.encrypt_using_iv(key, [username_email, ], table_name)
                                sql_command_delete = "delete from {} where application_name in ({}) and username_email in ({})".format(table_name, account, username_email)
                                cursor.execute(sql_command_delete)
                                break
                        else:
                            print("\nThe username/email does not exist")
                            retry(key, table_name)
                            return delete_details(key, table_name)
                        break
            else:
                for i in accounts:
                    for j in account:
                        if i[0]==j:
                            sql_command_delete = "delete from {} where application_name='{}'".format(table_name, j)
                            cursor.execute(sql_command_delete)
                            break
                    else:
                        print("\nThe account does not exist in your vault")
                        return menu.choice(key, table_name)
            break

    connector.commit()
    print("\ndeleted!")
    return menu.choice(key, table_name)

# returned if account does not exist or if user inputs an invalid input multiple times
# user will be asked to try again or go back to the menu
def retry(key, table_name):
    while True:
        ask_user = input("\nWould you like to 1.try again or 2.go back")
        if ask_user == '1':
            return
        elif ask_user == '2':
            return menu.choice(key, table_name)
        else:
            print("\nTry again.Enter 1 or 2")
            continue

# checks if password is reused in any other application
def check_passwords(key,password,table_name):
    encrypted_passwords=encryption_decryption.encrypt_using_iv(key,[password,],table_name)
    sql_command_check_password="select count(password) from {} where password in ({})".format(table_name, encrypted_passwords)
    cursor.execute(sql_command_check_password)
    count=cursor.fetchall()
    if count[0][0]>0:
        print("\nThis password has already been used by you for another account.It is not safe to reuse the password.\n")
        while True:
            ask_user=input("Would you like to 1.change password or 2.continue : ")
            if ask_user=='1':
                return True
            elif ask_user=='2':
                return False
            else:
                print("\nTry again.Enter 1 or 2")
                continue
    return
