import mysql.connector

con = mysql.connector.connect(
    user="root",
    password="!Aa12345",
    host="localhost",
    database="tpdaytrip"
)
cursor = con.cursor()
order_query = '''
CREATE TABLE orders (
    order_number CHAR(20) NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_price DECIMAL(10,2) NOT NULL,
    trip_attr_id INT NOT NULL,
    trip_date DATE NOT NULL,
    trip_time VARCHAR(10) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(255) NOT NULL,
    payment_status VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES userInfo(id),
    FOREIGN KEY (trip_attr_id) REFERENCES taipei_attractions(id)
);
'''
payment_query = '''
CREATE TABLE payment (
    payment_id CHAR(22) NOT NULL PRIMARY KEY,
    rec_trade_id VARCHAR(20) NOT NULL,
    order_number CHAR(20) NOT NULL,
    transaction_time_millis BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_number) REFERENCES orders(order_number)
);
'''
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
cursor.execute(order_query)
cursor.execute(payment_query)
con.commit()
con.close()