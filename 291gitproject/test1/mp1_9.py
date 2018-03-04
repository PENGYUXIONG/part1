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

def createMasterAccount(manager):
        account = [0,manager,0,0,0,0,0,0]
        account[0] = input("\nEnter account number: ")
        account[2] = input("Enter customer name: ")
        account[3] = input("Enter customer info.: ")
        account[4] = input("Enter customer type: ")
        account[5] = input("Enter start date: ")
        account[6] = input("Enter end date: ")
        account[7] = float(input("Enter total amount of services customer has with company: "))
        cursor.execute('Insert into accounts values (?, ?, ?, ?, ?, ?, ?, ?);',account)
        return

def customerSummaryReport(customer):
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
        return
        print("Total number of service agreements: "+str(count[0])+"\nSum of prices: $"+str(price[0])+"\nSum of costs: $"+str(cost[0])+"\nTypes: "+", ".join(s)+"\n")
        return

def listCustomers(manager_id):
        cursor.execute("Select account_no, customer_name from accounts where account_mgr =:id",{"id":manager_id})
        query = cursor.fetchall()
        for i,j in enumerate(query):
                print(str(i+1)+". "+j[1]+" ("+j[0]+")")
        return query[int(input("\nSelect the customer: "))-1][0]

def accountManager(user_id):
        print("1: Select customer (master account)\n2: Create new master account\n3: Add new service agreement\n4: Create summary report for a single customer\n5: Logout\n0: Exit")
        option = int(input())
        if(option == 1):
                customer = listCustomers(user_id)
                cursor.execute("Select * from accounts where account_no =:customer",{"customer":customer})
                query = cursor.fetchone()
                print("\nAccount No.: "+str(query[0])+"\nAccount Mgr.: "+str(query[1])+"\nName: "+str(query[2])+"\nContact Info.: "+str(query[3])+"\nCustomer Type: "+str(query[4])+"\nStart Date: "+str(query[5])+"\nEnd Date: "+str(query[6])+"\nTotal Amount: $"+str(query[7]))
                query = cursor.fetchone()
                print("\nAccount No.: "+str(query[0])+"\nAccount Mgr.: "+str(query[1])+"\nName: "+str(query[2])+"\nContact Info.: "+str(query[3])+"\nCustomer Type: "+str(query[4])+"\nStart Date: "+str(query[5])+"\nEnd Date: "+str(query[6])+"\nTotal Amount: $"+str(query[7])+"\n")
                cursor.execute("Select * from service_agreements where master_account =:customer order by service_no",{"customer":customer})
                query = cursor.fetchall()
                for i in query:
                        print("Service No.: "+i[0]+"\nMaster Account: "+i[1]+"\nLocation: "+i[2]+"\nWaste Type: "+i[3]+"\nPick Up Schedule: "+i[4]+"\nLocal Contact: "+i[5]+"\nInternal Cost: $"+str(i[6])+"\nPrice: $"+str(i[7])+"\n")

        elif (option == 2):
                createMasterAccount(user_id)

        elif(option == 3):
                customer = input("Enter the name of the customer (case sensitive): ")
                cursor.execute("Select account_no from accounts where customer_name = :customer",{"customer":customer})
                account_no = cursor.fetchone()[0]
                cursor.execute("Select max(service_no) from service_agreements where master_account = :account_no",{"account_no":account_no})
                customer = listCustomers(user_id)
                cursor.execute("Select max(service_no) from service_agreements where master_account = :account_no",{"account_no":customer})
                service_no = cursor.fetchone()[0]
                if(service_no == None):
                        service_no = 1
                else:
                        service_no = int(service_no) + 1
                location = input("Enter location: ")
                waste = input("Enter waste type: ")
                pick_up = input("Enter pick up schedule: ")
                contact = input("Enter local contact: ")
                cost = float(input("Enter internal cost"))
                price = float(input("Enter price: "))
                cursor.execute("Insert into service_agreements values (?,?,?,?,?,?,?,?);",service_no,account_no,location,waste,pick_up,contact,cost,price)
                cursor.execute("Insert into service_agreements values (?,?,?,?,?,?,?,?);",service_no,customer,location,waste,pick_up,contact,cost,price)

        elif(option == 4):
                customerSummaryReport(listCustomers(user_id))

        elif(option == 5):
                login()
        elif(option == 0):
                exit()
        accountManager(user_id)

def supervisor(user_id):
        print("1: Create new master account\n2: Create summary report for a single customer\n3: Create summary report for account managers\n4: Logout\n0: Exit")
        option = int(input())
        if(option == 1):
                cursor.execute("Select p.name, p.pid from personnel p, account_managers a where p.supervisor_pid =:supervisor and p.pid = a.pid",{"supervisor":user_id})
                managers = cursor.fetchall()
                for i,j in enumerate(managers):
                        print(str(i+1)+". "+j[0]+" ("+j[1]+")\n")
                createMasterAccount(input("Select manager: "))
        elif(option == 2):
                cursor.execute("Select customer_name, account_no from accounts, personnel where account_mgr = pid and supervisor_pid = :user_id",{"user_id":user_id})
                query = cursor.fetchall()
                for i in range(0,len(query)):
                        print(query[i][0])
                        customerSummaryReport(query[i][1])
        elif(option == 3):
                cursor.execute("Select name,count(service_no), sum(internal_cost) as c, sum(price) as p from service_agreements, accounts, personnel where (master_account  = account_no) and (account_mgr = pid) and (supervisor_pid = :user_id) group by name order by (p-c)",{"user_id":user_id})
                query = cursor.fetchall()
                for i in range(0,len(query)):
                        print("\nAccount Manager: "+query[i][0]+"\nTotal Number of Service Agreements: "+str(query[i][1])+"\nSum of prices: $"+str(query[i][2])+"\nSum of internal costs: $"+str(query[i][3])+"\n")

        elif(option == 4):
                login()
        elif(option == 0):
                exit()
        supervisor(user_id)

def dispatcher(user_id):
        print("Select a service agreement:")
        return

def driver(user_id):
    # get date range from the input
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
        # get all informations of the qualified tours
        informations = cursor.fetchall()
        for inf in informations:
                # print information
                print("\n" + "Location: " + inf[0])
                print("contact information: " + inf[1])
                print("waste type: " + inf[2])
                print("drop_off container id: " + inf[3])
                print("pick_up container_id: " + inf[4])
        return

def validate_new_account():
    global connection, cursor
    user_pid = input(''' please enter the pid: \n (press m to back to main page)\n (press e to exit)\n''')
    if user_pid == "m" or user_pid == "M":
        main_interface()
    if user_pid == "e" or user_pid == "E":
        exit()
    cursor.execute('''
                    SELECT pid
                    FROM personnel
                    WHERE pid = :uid
                    ''', {'uid': user_pid})
    user_id = cursor.fetchone()
    if user_id == None:
        print("invalid pid")
        add_login_account()
    cursor.execute('''
                    SELECT user_id
                    FROM users
                    WHERE user_id = :uid'''
                    , {'uid': user_pid})
    user_id = cursor.fetchone()
    if user_id != None:
        print("Account already exist")
        login()

    role = input('''What is your role: \n 1. Account Manager \n 2. Driver \n (press e to exit)\n (press m to back to main page)\n''')
    if role == 'm' or role == 'M':
        main_interface()
    if role == 'e' or role == 'E':
        exit()
    if role == '1':
        cursor.execute('''SELECT pid FROM account_managers WHERE pid = :user''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Account Manager"
    if role == '2':
        cursor.execute('''SELECT pid FROM drivers WHERE pid = :user''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Driver"
    return user_pid, Role

def login_check(user_pid, role):
    global connection, cursor
    newlogin = input("Create Login: ")
    user = [user_pid, role, newlogin, 0]
    cursor.execute("SELECT login FROM users WHERE login = :nl", {'nl': newlogin})
    user_check = cursor.fetchone()
    return user, user_check

def add_login_account():
    global connection, cursor
    user_pid, role = validate_new_account()
    user, user_check = login_check(user_pid, role)
    while user_check != None:
        print("login already exist!\n")
        user, user_check = login_check(user_pid, role)
    user[3] = input("Create password: ")
    print(user)
    cursor.execute('Insert into users values (?, ?, ?, ?);', user)
    connection.commit()
    print("success!\n please log in with your Login and password")
    login()
    connection.close()
    exit()
    return

def login():
    global connection, cursor
    # login input
    login = input('Please enter the login: \n (press e to exit)\n (press m back to main page)\n' )
    if login == 'e' or login == 'E':
        exit()
    if login == 'm' or login == 'M':
        main_interface()
    # password input
    password = input('please enter the password: \n (press e to exit)\n (press m back to main page)\n')
    if password == "e" or password == "E":
        exit()
    if password == "m" or password == "M":
        main_interface()
    # find matched information
    cursor.execute('''select user_id,role,login,password
                    from users where login =:l and password = :pw''',
                    {'l':login, 'pw':password})
    # check the role of the user
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

def main_interface():
    option = input(" 1. log in \n 2. sign up\n (press e to exit)\n")
    while option != 'e' or option != 'E':
        if option == '1':
            login()
            exit()
        if option == '2':
            add_login_account()
            exit()
        if option == 'e' or option == 'E':
            exit()
        option = input("invalid key\n")
    return


def main():
        global connection, cursor

        path="./mp1.db"
        connect(path)
        main_interface()
        return


if __name__ == "__main__":
        main()
