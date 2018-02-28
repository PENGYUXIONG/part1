import sqlite3

connection = None
cursor = None

def connect(path):
        global connection, cursor

        # TODO: Initialize the global variable 'connection' with a connection to the dadabase specified by 'path'
        connection = sqlite3.connect(path)
        # TODO: Initialize the global variable 'cursor' with a cursor to the database you just connected
        cursor = connection.cursor()
        # TODO: Create and populate table is the database using 'init.sql' (from eclass)

        cursor.execute(' PRAGMA forteign_keys=ON; ')
        connection.commit()

        return

def main():
        global connection, cursor

        path="./mp1.db"
        connect(path)


        while True:

                login = input('Please enter the login: ')
                cursor.execute('select role from users where login ='+login+';')
                role = cursor.fetchone()
                print(role)
                break


        return


if __name__ == "__main__":
        main()

