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
        sqlcommand = open("table.sql").read()
        cursor.executescript(sqlcommand)
        connection.commit()

        return

def accountManager(user_id):
  print("1: Select customer (master account)\n2: Create new master account\n3: Add new service agreement\n4: Create summary report for a single customer")
  option = int(input())
  if(option == 1):
    cursor.execute("Select account_no, customer_name from accounts where account_mgr =:id",{"id":user_id})
    query = cursor.fetchall()
    for i in query:
      print(i[0]+" "+i[1])
    customer = input("Enter the account number of the customer: ")
    cursor.execute("Select * from accounts where account_no =:customer",{"customer":customer})
    query = cursor.fetchone() 
    print("\nAccount No.: "+str(query[0])+"\nAccount Mgr.: "+str(query[1])+"\nName: "+str(query[2])+"\nContact Info.: "+str(query[3])+"\nCustomer Type: "+str(query[4])+"\nStart Date: "+str(query[5])+"\nEnd Date: "+str(query[6])+"\nTotal Amount: $"+str(query[7]))  
    cursor.execute("Select * from service_agreements where master_account =:customer order by service_no",{"customer":customer})
    query = cursor.fetchall()
    for i in query:
      print("\nService No.: "+i[0]+"\nMaster Account: "+i[1]+"\nLocation: "+i[2]+"\nWaste Type: "+i[3]+"\nPick Up Schedule: "+i[4]+"\nLocal Contact: "+i[5]+"\nInternal Cost: $"+str(i[6])+"\nPrice: $"+str(i[7]))
  if(option == 2):
    return
  if(option == 3):
    return
  if(option == 4): 
    return
  return

def supervisor(user_id):
  print("1: Create new master account\n2: Add new service agreement\n3: Create summary report for a single customer\n4: Create summary report for account managers")
  option = int(input())
  if(option == 1):
    return
  if(option == 2):
    return
  if(option == 3):
    return
  if(option == 4):
    return
  return

def dispatcher(user_id):
  print("Select a service agreement:")
  return

def driver(user_id):
  print("Tours:")
  return


def main():
        global connection, cursor

        path="./mp1.db"
        connect(path)

        login = input('Please enter the login: ')
        cursor.execute('select user_id,role,login,password from users where login =:l',{'l':login})
        id_role = cursor.fetchone()
        if(id_role[1] == 'Account Manager'):
          accountManager(id_role[0])
        if(id_role[1] == 'Supervisor'):
          supervisor(id_role[0])
        if(id_role[1] == 'Dispatcher'):
          dispatcher(id_role[0])
        if(id_role[1] == 'Driver'):
          driver(id_role[0])

        return


if __name__ == "__main__":
        main()

