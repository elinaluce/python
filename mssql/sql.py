from os import getenv
import pymssql

# Those are read from the shell env.
# export MSSQL_SERVER=mssql.dw.com or IP address
server = getenv('MSSQL_SERVER')
user = getenv('MSSQL_USERNAME')
password = getenv('MSSQL_PASSWORD')
db_name = getenv('MSSQL_DB_NAME')

# Connect to server and get cursor.
conn = pymssql.connect(server, user, password, db_name)
cursor = conn.cursor()

# Select rows from DB.
# Table 'persons' has columns: 'id', 'name', 'age', 'salary'
age = 40
cursor.execute('SELECT * FROM persons WHERE age < %d', age)
row = cursor.fetchone()
# row is a list where:
# id = row[0]
# name = row[1]
# age = row[2]
# salary = row[3]
while row:
    # divide salary by nb of months
    monthly_salary = row[3] / 12.
    print('ID=%d, Name=%s, MonthlySalary=%d' % (row[0], row[1],
        monthly_salary))
    row = cursor.fetchone()

conn.close()
