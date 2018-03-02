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

def accountManager(user_id):
  print("Select customer (master account)\nCreate new master account\nAdd new service agreement\nCreate summary report for a single customer")
  while True:
    break
  return

def supervisor(user_id):
  print("Create new master account\nAdd new service agreement\ncreate summary report for a single customer\nCreate summary report for account managers")
  while True:
    break
  return

def dispatcher(user_id):
  print("Select a service agreement:")
  while True:
    break
  return

def driver(user_id):
  print("Tours:")
  while True:
    break
  return


def main():
        global connection, cursor

        path="./mp1.db"
        connect(path)


        while True:

                login = input('Please enter the login: ')
                cursor.execute('select user_id,role from users where login =:l',{'l':login})
                id_role = cursor.fetchone()
                if(id_role[1] == 'Account Manager'):
                  accountManager(id_role[0])
                if(id_role[1] == 'Supervisor'):
                  supervisor(id_role[0])
                if(id_role[1] == 'Dispatcher'):
                  dispatcher(id_role[0])
                if(id_role[1] == 'Driver'):
                  driver(id_role[0])
                break


        return


if __name__ == "__main__":
        main()

