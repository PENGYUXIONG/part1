import sqlite3
import getpass
import datetime
import time
import os.path
from hashlib import pbkdf2_hmac
connection = None
cursor = None
hash_name = 'sha256'
salt = 'ssdirf993lksiqb4'
iterations = 100000

def connect(path):
        global connection, cursor

        #Initialize the global variable 'connection' with a connection to the dadabase specified by 'path'
        print("Making connection to database ... ", end = '')
        old_file_exists = os.path.exists(path)
        connection = sqlite3.connect(path)
        print('Done')
        #Initialize the global variable 'cursor' with a cursor to the database you just connected
        print("Initializing cursor ... ", end = '')
        cursor = connection.cursor()
        print('Done')
        #Create and populate table is the database using 'init.sql' (from eclass)


        cursor.execute(' PRAGMA foreign_keys=ON; ')

        #if no previous db was in directory
        if old_file_exists == False:
                print("Importing table ... ", end = '')
                sqlcommand = open("table.sql").read()
                cursor.executescript(sqlcommand)
                insertUser();
        connection.commit()
        print("Done \n")

        return

#checks integers are in right format
def int_check(i):
        try:
                i = int(i)
                return True
        except ValueError:
                return False

#checks dates are in right format
def date_check(text):
        try:
                datetime.datetime.strptime(text, '%Y-%m-%d')
                return True
        except ValueError:
                return False
#checks money is in right format
def float_check(price):
        try:
                price = float(price)
        except ValueError:
                return False
        n = str(price).split('.')
        if len(n[-1]) > 2 or price < 0:
                return False
        else:
                return True

def createMasterAccount(manager):
        #gets info
        account = ['',manager,0,0,0,'','','']
        while int_check(account[0]) == False:
                account[0] = input("\nEnter account number: ")
        #checks if account is already in db
        cursor.execute("Select count(*) from accounts where account_no = :a",{"a":account[0]})
        if cursor.fetchone()[0] > 0:
                print("That account already exists.\n")
                return
        account[2] = input("Enter customer name: ")
        account[3] = input("Enter customer info.: ")
        account[4] = input("Enter customer type: ")
        while date_check(account[5]) == False:
                account[5] = input("Enter start date (YYYY-MM-DD): ")

        while date_check(account[6]) == False or time.strptime(account[5], "%Y-%m-%d") > time.strptime(account[6], "%Y-%m-%d"):
                account[6] = input("Enter end date (YYYY-MM-DD): ")
                if time.strptime(account[5], "%Y-%m-%d") > time.strptime(account[6], "%Y-%m-%d"):
                        print("The end date must come after the start date.")
        while float_check(account[7]) == False:
                account[7] = input("Enter total amount of the services customer has with company: ")
        cursor.execute('Insert into accounts values (?, ?, ?, ?, ?, ?, ?, ?);',account)
        connection.commit()
        return

def customerSummaryReport(customer):
        #gets info
        cursor.execute("Select count(*),sum(price),sum(internal_cost),waste_type from service_agreements where master_account = :customer",{"customer":customer})
        info = list(cursor.fetchone())
        #set ensures no duplicate
        s = set()
        cursor.execute("Select waste_type from service_agreements where master_account = :customer",{"customer":customer})
        types = cursor.fetchall()
        for i in range(0,len(types)):
                for j in range(0,len(types[i])):
                        s.add(types[i][j])
        if info[1] == None:
                info[1] = 0
        if info[2] == None:
                info[2] = 0
        print("Total number of service agreements: "+str(info[0])+"\nSum of prices: $"+str(round(info[1],2))+"\nSum of costs: $"+str(round(info[2],2))+"\nTypes: "+", ".join(s)+"\n")
        return

def listCustomers(manager_id):
        #finds customer with correct manager
        cursor.execute("Select account_no, customer_name from accounts where account_mgr =:id",{"id":manager_id})
        query = cursor.fetchall()
        for i,j in enumerate(query):
                print(str(i+1)+". "+j[1]+" ("+j[0]+")")
        print(str(len(query)+1)+": Cancel\n0: Exit")
        while True:
                option = int(input("\nSelect the customer: "))
                #cancels
                if option == len(query)+1:
                        accountManager(manager_id)
                #lists info of customer at index
                elif option in range(1,len(query)+1):
                        return query[option-1][0]
                #exits
                elif option == 0:
                        connection.close()
                        exit()

def accountManager(user_id):
        option =input("1: Select customer (master account)\n2: Create new master account\n3: Add new service agreement\n4: Create summary report for a single customer\n5: Logout\n0: Exit\n")
        if(option == '1'):
                customer = listCustomers(user_id)
                cursor.execute("Select * from accounts where account_no =:customer",{"customer":customer})
                query = cursor.fetchone()
                print("\nAccount No.: "+str(query[0])+"\nAccount Mgr.: "+str(query[1])+"\nName: "+str(query[2])+"\nContact Info.: "+str(query[3])+"\nCustomer Type: "+str(query[4])+"\nStart Date: "+str(query[5])+"\nEnd Date: "+str(query[6])+"\nTotal Amount: $"+str(query[7])+"\n")
                cursor.execute("Select * from service_agreements where master_account =:customer order by service_no",{"customer":customer})
                query = cursor.fetchall()
                for i in query:
                        print("Service No.: "+i[0]+"\nMaster Account: "+i[1]+"\nLocation: "+i[2]+"\nWaste Type: "+i[3]+"\nPick Up Schedule: "+i[4]+"\nLocal Contact: "+i[5]+"\nInternal Cost: $"+str(i[6])+"\nPrice: $"+str(i[7])+"\n")

        elif (option == '2'):
                createMasterAccount(user_id)
        #new service agreement
        elif(option == '3'):
                #asks details
                customer = listCustomers(user_id)
                #find max service number from service agreements ith respective customer then adds 1 -> ensuring service no is unique
                cursor.execute("Select max(service_no) from service_agreements where master_account = :account_no",{"account_no":customer})
                service_no = cursor.fetchone()[0]
                if(service_no == None):
                        service_no = 1
                else:
                        service_no = int(service_no) + 1
                location = input("Enter location: ")
                cursor.execute("Select * from waste_types")
                query = cursor.fetchall()
                waste_types = []
                for i in range(0,len(query)):
                        waste_types.append(query[i][0])
                print("Valid waste types - "+", ".join(waste_types))
                waste = input("Enter waste type: ")
                while True:
                        if waste in waste_types:
                                break
                        waste = input("Please enter a valid waste type: ")
                pick_up = input("Enter pick up schedule: ")
                contact = input("Enter local contact: ")
                cost = ''
                while float_check(cost) == False:
                        cost = input("Enter internal cost: ")
                price = ''
                while float_check(price) == False:
                        price = input("Enter price: ")
                cursor.execute("Insert into service_agreements values (:s,:c,:l,:w,:p,:c2,:c3,:p2);",{"s":service_no,"c":customer,"l":location,"w":waste,"p":pick_up,"c2":contact,"c3":cost,"p2":price})
                connection.commit()
        #prompts user to select customer and then prints report for that customer
        elif(option == '4'):
                customerSummaryReport(listCustomers(user_id))
        #main menu
        elif(option == '5'):
                main_interface()
        #exit program
        elif(option == '0'):
                connection.close()
                exit()
        #calls itself
        accountManager(user_id)

def supervisor(user_id):
        option = input("1: Create new master account\n2: Create summary report for a single customer\n3: Create summary report for account managers\n4: Logout\n0: Exit\n")
        #creates master account
        if(option == '1'):
                #lists managers where supervisor id matches
                cursor.execute("Select p.name, p.pid from personnel p, account_managers a where p.supervisor_pid =:supervisor and p.pid = a.pid",{"supervisor":user_id})
                managers = cursor.fetchall()
                for i,j in enumerate(managers):
                        print("\n"+str(i+1)+". "+j[0]+" ("+j[1]+")")
                print(str(len(managers)+1)+": Cancel\n0: Exit")
                manager = ''
                while True:
                        while int_check(manager) == False:
                                manager = input("Select manager: ")
                        if manager == str(len(managers)+1):
                                supervisor(user_id)
                        elif manager == '0':
                                connection.close()
                                exit()
                        elif int(manager) in range(1,len(managers)+1):
                                createMasterAccount(managers[int(manager)-1][1])
                                break
        #Summary Report single customer
        elif(option == '2'):
                #calls each customer where the supervisor id matches
                cursor.execute("Select customer_name, account_no from accounts, personnel where account_mgr = pid and supervisor_pid = :user_id",{"user_id":user_id})
                query = cursor.fetchall()
                for i in range(0,len(query)):
                        print(str(i+1)+": "+query[i][0])
                print(str(len(query)+1)+": Cancel\n0: Exit")
                while True:
                        account = ''
                        while int_check(account) == False:
                                account = input("Select account: ")
                        account = int(account)
                        if account == len(query)+1:
                                supervisor(user_id)
                        elif account == 0:
                                connection.close()
                                exit()
                        elif account in range(1,len(query)+1):
                                customerSummaryReport(query[account-1][1])
                                break
        #Summary report managers
        elif(option == '3'):
                #selects details of each desired manager
                cursor.execute("Select name,count(service_no), sum(internal_cost) as c, sum(price) as p from service_agreements, accounts, personnel where (master_account  = account_no) and (account_mgr = pid) and (supervisor_pid = :user_id) group by name order by (p-c)",{"user_id":user_id})
                query = cursor.fetchall()
                #prints each manager with details
                for i in range(0,len(query)):
                        print("\nAccount Manager: "+query[i][0]+"\nTotal Number of Service Agreements: "+str(query[i][1])+"\nSum of prices: $"+str(round(query[i][2],2))+"\nSum of internal costs: $"+str(round(query[i][3],2))+"\n")
        #goes to main menu
        elif(option == '4'):
                main_interface()
        #exits program
        elif(option == '0'):
                connection.close()
                exit()
        #calls itself
        supervisor(user_id)

def dispatcher(user_id):
        global connection, cursor
        #The big loop for creating multiple tables
        while(True):
                #Choises given to user
                print("1: Create a service_fulfillments table. ")
                print("2: Logout\n0: Exit")
                choise = input("Choose what do you want to do: ")

                #Create fulfillment
                if (choise == '1'):

                        #List all service agreements
                        query = "select service_no, master_account from service_agreements order by service_no"
                        serviceList = cursor.execute(query).fetchall()
                        index = 0
                        print('Index','|','Service No.','|', 'Master Account')
                        for row in serviceList:
                                print(index,'|',row[0],'|',row[1])
                                index += 1


                        #Select service index
                        #Make sure input exists in list
                        while(True):
                                slct_Service_Index = int(input("Select a service agreement (Index) from above: "))
                                if(slct_Service_Index >= len(serviceList) or slct_Service_Index < 0):
                                        print("This is not an existing index, please try another one. \n")
                                else:
                                        break

                        query = "SELECT * from service_agreements where service_no = ? and master_account = ?"
                        slctService = cursor.execute(query,(serviceList[ slct_Service_Index][0],serviceList[ slct_Service_Index][1],)).fetchone()

                        #List all drivers
                        query = "SELECT * from drivers order by pid"
                        driverList = cursor.execute(query).fetchall()

                        print('Pid')
                        for row in driverList:
                                print(row[0])


                        #Select driver
                        query = "SELECT * from drivers where pid = ?"
                        #Make sure input exists in database
                        while(True):
                                slct_Driver_Id = input("Select a driver (id): ")
                                slctDriver = cursor.execute(query,(slct_Driver_Id,)).fetchall()
                                if(len(slctDriver) != 0):
                                        break
                                else:
                                        print("This is not an existing driver, please try another one. \n")

                        #Check if the driver owns a truck
                        query = "SELECT * from trucks where truck_id = ?"
                        if(slctDriver[0][2] != None):
                                slctTruck = cursor.execute(query,(slctDriver[0][2],)).fetchall()
                                print("The driver's truck being select.")
                        else:
                                #Show list of aviliabe trucks
                                        query3 = '''SELECT truck_id from trucks
                                                WHERE truck_id not in
                                                (SELECT owned_truck_id FROM drivers WHERE owned_truck_id is not null)'''
                                        truckList = cursor.execute(query3).fetchall()
                                        print('Truck id')
                                        for row in truckList:
                                                print(row[0])

                        while(True):
                                #Make sure input exists in database
                                slct_Truck_Id = input("Select a truck (id): ")
                                slctTruck = cursor.execute(query,(slct_Truck_Id,)).fetchall()
                                if(len(slctTruck) != 0):
                                        #Make sure the truck is owned by company
                                        query2 = '''SELECT * from trucks
                                                where truck_id = ?
                                                and truck_id not in
                                                (SELECT owned_truck_id FROM drivers WHERE owned_truck_id is not null)'''
                                        slctTruck = cursor.execute(query2,(slct_Truck_Id,)).fetchall()
                                        if(len(slctTruck) != 0):
                                                break
                                        else:
                                                print("This is not a truck owned by company, please try another one. \n")
                                else:
                                        print("This is not an existing truck, please try another one. \n")


                        #Auto fill pick up container
                        query = '''
                                SELECT c.container_id
                                FROM containers c
                                WHERE (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_pick_up = c.container_id)
                                <
                                (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_drop_off = c.container_id)
                                intersect
                                select cid_drop_off
                                from service_fulfillments sf, service_agreements sg
                                where sf.service_no = sg.service_no
                                and sg.location = ?
                                '''
                        #In case we got no container
                        slct_Container_Id = cursor.execute(query,(slctService[2],)).fetchall()
                        if(len(slct_Container_Id) != 0):
                                print("Pick-up-container automatically selected. ")
                        else:
                                print("No container at the loacation, Dunmmy container being select. ")
                                slct_Container_Id = [("NULLID",)]


                        #Select drop off container
                        query = '''
                                SELECT c.container_id
                                FROM containers c
                                WHERE NOT EXISTS (SELECT *
                                                FROM service_fulfillments s
                                                WHERE s.cid_drop_off = c.container_id)
                                UNION
                                SELECT c.container_id
                                FROM containers c
                                WHERE (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_pick_up = c.container_id)
                                >
                                (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_drop_off = c.container_id)
                                intersect
                                select container_id
                                from container_waste_types
                                where waste_type = ?
                                except
                                select container_id
                                from containers
                                where container_id = 'NULLID'
                                '''

                        #Get list of container that matches waste type
                        containerList = cursor.execute(query,(slctService[3],)).fetchall()
                        #Show list if available
                        if(len(containerList) == 0):
                                print("No containers available for drop off, Dummy container being select.")
                                slct_Container_Id2 = [("NULLID",)]
                        else:
                                for row in containerList:
                                        print(row[0])

                                query = "SELECT * from containers where container_id = ?"
                                while(True):
                                        slct_Container_Id2 = input("Select a container (id) from list above to drop off: ")
                                        if((slct_Container_Id2,) in containerList):
                                                break
                                        else:
                                                print("This is not an container from list, please try another one. \n")

                        #Collecting date
                        while(True):
                                date = input("Enter in the date in the form YYYY-MM-DD: ").replace(" ","")
                                if(not date_check(date)):
                                        print("The date is not in format")
                                else:
                                        break


                        #Create the fulfillments table
                        query = "Insert into service_fulfillments values (?,?,?,?,?,?,?)"
                        cursor.execute(query,(date,slctService[1],slctService[0],slctTruck[0][0],slct_Driver_Id,slct_Container_Id2,slct_Container_Id[0][0]))
                        connection.commit()
                        print("Table created! \n")

                elif(choise == '2'):
                        main_interface()
                elif(choise == '0'):
                        exit()
                else:
                        print("Please select option. \n")

def driver(user_id):
        # get date range from the input
        Start_date = input("Please input the start date for that search with correct form (yyyy-mm-dd): ")
        if date_check(Start_date) == False:
            print("invalid date format")
            driver(user_id)
            return
        End_date = input("Please input the end date for that search with correct form (yyyy-mm-dd): ")
        if date_check(End_date) == False:
            print("invalid date format")
            driver(user_id)
            return
        cursor.execute("SELECT strftime('%Y-%m-%d %H:%M:%S.%f', :End_date) >= strftime('%Y-%m-%d %H:%M:%S.%f', :start)", {"End_date":End_date, "start":Start_date})
        end_date_check = cursor.fetchone()[0]
        if end_date_check != 1:
            print("end date need to be larger than start date!")
            driver(user_id)
            return
        cursor.execute('''SELECT sa.location, sa.local_contact, sa.waste_type,
                    sf.cid_drop_off, sf.cid_pick_up
                    FROM service_agreements sa, service_fulfillments sf
                    WHERE sa.master_account = sf.master_account
                    and
                    sa.service_no = sf.service_no
                    and
                    strftime('%Y-%m-%d %H:%M:%S.%f', :start) < sf.date_time
                    and
                     sf.date_time < strftime('%Y-%m-%d %H:%M:%S.%f', :End_date)
                    and
                    sf.driver_id = :id''', {"id":user_id, "start":Start_date, "End_date":End_date})
        # get all informations of the qualified tours
        informations = cursor.fetchall()
        for inf in informations:
                # print information
                print("\n" + "Location: " + inf[0])
                print("contact information: " + inf[1])
                print("waste type: " + inf[2])
                print("drop_off container id: " + inf[3])
                print("pick_up container_id: " + inf[4])
        print("\n")
        main_interface()

def validate_new_account():
    global connection, cursor
    # check if the pid is inside personnel, if not stop and ask for valid pid
    user_pid = input('''Please enter the pid: ''')

    cursor.execute('''
                    SELECT pid, supervisor_pid
                    FROM personnel
                    WHERE pid = :uid
                    or
                    supervisor_pid = :uid
                    ''', {'uid': user_pid})
    user_id = cursor.fetchone()

    # pid not valid
    if user_id == None:
        print("Invalid pid")
        add_login_account()
    cursor.execute('''
                    SELECT user_id
                    FROM users
                    WHERE user_id = :uid'''
                    , {'uid': user_pid})
    user_id = cursor.fetchone()

    # pid already exist inside the databse
    if user_id != None:
        print("Account already exist")
        login()
    # check the role
    role = input('''Select role: \n1. Account Manager \n2. Driver \n3. Supervisor\n4. Dispatcher\n5: Cancel\n0: Exit\n''')
    # go to the main
    if role == 5:
        main_interface()
    # exit
    if role == 0:
        exit()
    # check account_managers
    if role == '1':
        cursor.execute('''SELECT pid FROM account_managers WHERE pid = :user''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Account Manager"
    # check driver
    if role == '2':
        cursor.execute('''SELECT pid FROM drivers WHERE pid = :user''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Driver"
    # check supervisor
    if role == '3':
        cursor.execute('''SELECT supervisor_pid FROM personnel WHERE supervisor_pid = :user''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Supervisor"
    # check for dispatcher pid
    if role == '4':
        cursor.execute('''
        SELECT pid
        FROM personnel
        WHERE
        :user = pid
        EXCEPT
        SELECT pid FROM drivers
        EXCEPT
        SELECT pid FROM account_managers
         ''', {'user': user_pid})
        pid = cursor.fetchone()
        if pid == None:
            print("Role not correct, please sign up again\n")
            add_login_account()
        Role = "Dispatcher"
    return user_pid, Role

def login_check(user_pid, role):
    global connection, cursor
    # check if the new login already exist in the database
    newlogin = input("Create Login: ")
    user = [user_pid, role, newlogin, 0]
    cursor.execute("SELECT login FROM users WHERE login = :nl", {'nl': newlogin})
    user_check = cursor.fetchone()
    return user, user_check

def add_login_account():
    global connection, cursor, hash_name, salt, iterations
    user_pid, role = validate_new_account()
    user, user_check = login_check(user_pid, role)
    # if the login alreay exist let user go the the log in
    while user_check != None:
        print("Login already exists!\n")
        user, user_check = login_check(user_pid, role)

    #Encrypt password
    password = input("Create password: ")
    dk = pbkdf2_hmac(hash_name, bytearray(password, 'ascii'), bytearray(salt, 'ascii'), iterations)
    user[3] = dk
    # insert the new value into user
    cursor.execute('Insert into users values (?, ?, ?, ?);', user)
    connection.commit()
    print("Success!\n Please log in with your Login and password")
    login()
    exit()
    return

def login():
    global connection, cursor, hash_name, salt, iterations, count
    # login input
    login = input('Please enter the login: ')
    # password input
    password = getpass.getpass("Please enter the password: ")
    #Generate a derived key
    dk = pbkdf2_hmac(hash_name, bytearray(password, 'ascii'), bytearray(salt, 'ascii'), iterations)
    # find matched information
    cursor.execute('''select user_id,role,login,password
                    from users where login =:l and password = :pw''',
                    {'l':login, 'pw':dk})
    # check the role of the user
    id_role = cursor.fetchone()
    if id_role == None:
        # add one for the counter
        count = count + 1
        # if the counter equal to three, exit the program
        if count == 3:
          exit()
        print("No matched login in database, please sign up")
        main_interface()
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
    while True:
        option = input("1. Log in \n2. Sign up\n0: Exit\n")
        if option == '1':
                login()
                exit()
        if option == '2':
                add_login_account()
                exit()
        if option == '0':
                exit()
        print("Invalid key\n")
    return

def insertUser():
        global connection, cursor, hash_name, salt, iterations
        query = 'Insert into users values (?, ?, ?, ?)'
        dk = pbkdf2_hmac(hash_name, bytearray('001', 'ascii'), bytearray(salt, 'ascii'), iterations)
        cursor.execute(query, ('34725', 'Account Manager', '000', dk))
        dk = pbkdf2_hmac(hash_name, bytearray('101', 'ascii'), bytearray(salt, 'ascii'), iterations)
        cursor.execute(query, ('50000', 'Supervisor', '100', dk))
        dk = pbkdf2_hmac(hash_name, bytearray('301', 'ascii'), bytearray(salt, 'ascii'), iterations)
        cursor.execute(query, ('43743', 'Driver', '300', dk))
        dk = pbkdf2_hmac(hash_name, bytearray('401', 'ascii'), bytearray(salt, 'ascii'), iterations)
        cursor.execute(query, ('40000', 'Dispatcher', '400', dk))
        connection.commit()

def main():
        global connection, cursor, count
        count = 0
        path="./mp1.db"
        connect(path)
        main_interface()
        connection.close()
        return


if __name__ == "__main__":
        main()
