import mysql.connector

con = mysql.connector.connect(
    user="root",
    password="!Aa12345",
    host="localhost",
    database="tpdaytrip"
)

cursor = con.cursor()
create_table_query = '''
CREATE TABLE userInfo (
	id INT PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	hashed_pwd VARCHAR(255) NOT NULL
);
'''
cursor.execute(create_table_query)
con.commit()
con.close()