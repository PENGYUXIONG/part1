import sqlite3
import os
connection = None
cursor = None

def connect(path):
        global connection, cursor

        #Initialize the global variable 'connection' with a connection to the dadabase specified by 'path'
        print("Making connection to database ... ", end = '')
        connection = sqlite3.connect(path)
        print('Done')
        #Initialize the global variable 'cursor' with a cursor to the database you just connected
        print("Initializing cursor ... ", end = '')
        cursor = connection.cursor()
        print('Done')
        #Create and populate table is the database using 'init.sql' (from eclass)
        

        cursor.execute(' PRAGMA foreign_keys=ON; ')
        #print("Importing table ... ", end = '')
        #sqlcommand = open("table.sql").read()
        #cursor.executescript(sqlcommand)
        connection.commit()
        print("Done \n")

        return

def directory():
        arr = os.listdir()
        for i,j in enumerate(arr):
                if j[-3:] != ".db" and j[-9:] != ".sqliteDB":
                        arr.remove(j)
        for i,value in enumerate(arr,1):
                print(str(i)+": "+value)
        path = arr[int(input("Select valid database: "))-1]
        print("\n")
        return path



def BCNF(inputRelationSchemas,r1,person):
        
        return

def main_interface():
        while True:
                option = input("1: Enter database name\n2: Select database from current directory\n0: Exit\nSelect option: ")
                print("\n")
                if option == '0':
                        exit()
                elif option == '1' or option == '2':
                        if option == '1':
                                connect(input("Enter database name: "))
                        else:
                                connect(directory())
                        inputRelationSchemas = cursor.execute("Select * from InputRelationSchemas;").fetchall()[0]
                        r1 = cursor.execute("Select * from R1;").fetchall()[0]
                        person = cursor.execute("Select * from Person;").fetchall()[0]
                        option = input("1: Perform BCNF on schema\n2: Compute attribute closure on schema\n3: Determine equivalency on two sets of functional dependencies\n0: Exit\nSelect option: ")
                        if option == '0':
                                exit()
                        elif option == '1':
                                BCNF(inputRelationSchemas,r1,person)
                print("Invalid key\n")
        return  


def main():
        global connection, cursor        

        main_interface()
        connection.close()
        return


if __name__ == "__main__":
        main()