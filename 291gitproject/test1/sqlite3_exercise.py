import sqlite3
import time

connection = None
cursor = None

def connect(path):
	global connection, cursor

	# TODO: Initialize the global variable 'connection' with a connection to the dadabase specified by 'path'
	# TODO: Initialize the global variable 'cursor' with a cursor to the database you just connected
	# TODO: Create and populate table is the database using 'init.sql' (from eclass)
	connection = sqlite3.connect('register.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(' PRAGMA forteign_keys=ON; ')
	sqlcommand = open("init.sql").read()
	cursor.executescript(sqlcommand)
	connection.commit()

	return

def createEnrollTable():

	global connection, cursor

	# TODO: create a table enroll (studentID, courseID, term, grade)
	cursor.executescript(
	'''
	DROP TABLE if exists enroll;
	CREATE TABLE enroll(
	studentID INTEGER,
	courseID INTEGER,
	term TEXT,
	grade TEXT,
	PRIMARY KEY(studentID, courseID, term));'''
	)
	connection.commit()
	return


def checkSeatsAvailable(course_id):

	global connection, cursor
	cursor.execute("SELECT * FROM courses;")
	row = cursor.fetchone()
	print(row.keys())
	rows = cursor.fetchall()
	for row in rows:
		print (row ["courseID"], row["seatsAvailable"])
	cursor.execute("SELECT * FROM professors;")
	test = cursor.fetchone()
	print(test.keys())
	connection.commit()
	# Write your code here

	return


def enroll(student_id, course_id):

	global connection, cursor

	current_term = "Winter 2018"

	# TODO: Check that there is a spot in the course for this student.
	# TODO: Register the student in the course.
	# TODO: Update the seats_available in the course table. (decrement)

	return


def generateTranscript(student_id):

	global connection, cursor

	# Write your code here

	return


def main():
	global connection, cursor

	path="./register.db"
	connect(path)

	createEnrollTable()
	checkSeatsAvailable('9')
	while True:

		student_id = input('Please enter the student ID or q to exit: ')
		if student_id == 'q':
			break

		course_id = input('Please enter the course ID: ')
		if course_id == 'q':
			break

		enroll(student_id, course_id)
		generateTranscript(student_id)


	return


if __name__ == "__main__":
	main()
