import mysql.connector

con = mysql.connector.connect(
    user="root",
    password="!Aa12345",
    host="localhost",
    database="tpdaytrip"
)
cursor = con.cursor()

pending_query = '''
CREATE TABLE pending (
	userId INT NOT NULL,
	attractionId INT NOT NULL,
	date DATE NOT NULL,
	time VARCHAR(255) NOT NULL,
	price INT NOT NULL,
	FOREIGN KEY(userId) REFERENCES userInfo(id),
	FOREIGN KEY(attractionId) REFERENCES taipei_attractions(id)
); 
'''

cursor.execute(pending_query)
con.commit()
con.close()