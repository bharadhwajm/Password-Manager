import random
import string
import tkinter
import menu

# generates a strong password with random characters using random module
# random characters in a password makes the password more secure since its harder to guess
def generate_password():
    characters = string.ascii_letters+string.digits+string.punctuation
    password = ""
    while True:
        try:
            ask_user_char = int(input("\nHow many characters would you like to have in your password(8-30) : "))
            if ask_user_char < 8 or ask_user_char > 30:
                print("\nTry again.Enter a number between 8-30")
                continue
            else:
                for i in range(ask_user_char):
                    password += random.choice(characters)

        except ValueError:
            print("\nTry again.Enter a number between 8-30")
            continue

        return password

# the user is asked if they want to get another password, copy password to clipboard or go back to the menu
def choice(key, table_name):
    password = generate_password()
    print(password)
    while True:
        ask_user = input("\nWould you like to 1.get another password 2.copy password to clipboard 3.go back : ")
        if ask_user == '1':
            return choice(key,table_name)
        elif ask_user == '2':
            window = tkinter.Tk()
            window.withdraw()
            window.clipboard_append(password)
            print("\nPassword copied to clipboard")
            return menu.choice(key, table_name)
        elif ask_user == '3':
            return menu.choice(key, table_name)
        else:
            print("\nTry again.Enter 1 2 or 3")
            continue
