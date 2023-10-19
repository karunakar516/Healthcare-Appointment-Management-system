import sqlite3

# Connecting to sqlite
# connection object
connection_obj = sqlite3.connect('db.sqlite3')

# cursor object
cursor_obj = connection_obj.cursor()


#delete data
cursor_obj.execute('''DELETE FROM customer_appointment;''')

connection_obj.commit()
# Close the connection
connection_obj.close()
