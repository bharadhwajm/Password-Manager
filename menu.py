import datetime
import password_generator
import sql_functions

# greet user based on the current time and display the number accounts in the users vault
def greet(username, key, table_name):
    time = datetime.datetime.now().time().strftime("%H")

    if time >= '00' and time < '12':
        print("Good morning", username)
    elif time >= '12' and time < '17':
        print("Good afternoon", username)
    else:
        print("Good evening", username)

    account_num = sql_functions.count_account(table_name)
    if account_num > 1:
        print("your vault contains {} account".format(account_num))
    else:
        print("Your vault contains {} accounts".format(account_num))

    return choice(key, table_name)

# ask user if they would like to view all accounts,view speciic account,add an account,
# update account details,delete account details, use the password generator or exit the preogram
def choice(key, table_name):
    while True:
        ask_user = input("\nWould you like to:\n"
                         " 1.view all accounts\n"
                         " 2.view details of a specific account\n"
                         " 3.add account\n"
                         " 4.update account details\n"
                         " 5.delete account details\n"
                         " 6.generate password\n"
                         " 7.exit\n")

        if ask_user == '1':
            return sql_functions.view_all_accounts(key, table_name)
        elif ask_user == '2':
            return sql_functions.search_specific_account(key, table_name)
        elif ask_user == '3':
            return sql_functions.add_account(key, table_name)
        elif ask_user == '4':
            return sql_functions.update_account_details(key, table_name)
        elif ask_user == '5':
            return sql_functions.delete_details(key, table_name)
        elif ask_user == '6':
            return password_generator.choice(key, table_name)
        elif ask_user == '7':
            print("\nBye :)")
            break
        else:
            print("\nTry again.Enter 1 2 3 4 5 6 or 7")
            continue
