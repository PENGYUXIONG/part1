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
  print("1: Select customer (master account)\n2: Create new master account")
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

    print("\n1: Add new service agreement\n2: Create summary report for a single customer")
    option = int(input())
    if(option == 1):
      service_no = int(query[len(query)-1][0]) + 1
      location = input("Enter location: ")
      waste = input("Enter waste type: ")
      pick_up = input("Enter pick up schedule: ")
      contact = input("Enter local contact: ")
      cost = float(input("Enter internal cost"))
      price = float(input("Enter price: "))
      cursor.execute("Insert into service_agreements values (?,?,?,?,?,?,?,?);",service_no,customer,location,waste,pick_up,contact,cost,price)

    elif(option == 2):
      cursor.execute("Select count(*) from service_agreements where master_account = :customer",{"customer":customer})
      count = cursor.fetchone()
      cursor.execute("Select sum(price) from service_agreements where master_account = :customer",{"customer":customer})
      price = cursor.fetchone()
      cursor.execute("Select sum(internal_cost) from service_agreements where master_account = :customer",{"customer":customer})
      cost = cursor.fetchone()
      s = set()
      cursor.execute("Select waste_type from service_agreements where master_account = :customer",{"customer":customer})
      types = cursor.fetchall()
      for i in range(0,len(types)):
        for j in range(0,len(types[i])):
          s.add(types[i][j])
      print("Total number of service agreements: "+str(count[0])+"\nSum of prices: $"+str(price[0])+"\nSum of costs: $"+str(cost[0])+"\nTypes: "+", ".join(s))

  elif (option == 2):
    account = [0,user_id,0,0,0,0,0,0]
    account[0] = input("Enter account number: ")
    account[2] = input("Enter customer name: ")
    account[3] = input("Enter customer info.: ")
    account[4] = input("Enter customer type: ")
    account[5] = input("Enter start date: ")
    account[6] = input("Enter end date: ")
    account[7] = float(input("Enter total amount of services customer has with company: "))
    cursor.execute('Insert into accounts values (?, ?, ?, ?, ?, ?, ?, ?);',account)
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
    Date_Range = '+' + input("Please input the date range (an int number):") + ' day'
    cursor.execute('''SELECT sa.location, sa.local_contact, sa.waste_type,
                    sf.cid_drop_off, sf.cid_pick_up
                    FROM service_agreements sa, service_fulfillments sf
                    WHERE sa.master_account = sf.master_account
                    and
                    sa.service_no = sf.service_no
                    and
                    date('now') < sf.date_time
                    and
                     sf.date_time < date('now', :range)
                    and
                    sf.driver_id = :id''', {"id":user_id, "range":Date_Range})
    informations = cursor.fetchall()
    for inf in informations:
        # print information
        print("\n" + "Location: " + inf[0])
        print("contact information: " + inf[1])
        print("waste type: " + inf[2])
        print("drop_off container id: " + inf[3])
        print("pick_up container_id: " + inf[4])
    return

def login():
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

def main():
        global connection, cursor

        path="./mp1.db"
        connect(path)
        login()
        return


if __name__ == "__main__":
        main()
