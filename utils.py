import mysql.connector
from mysql.connector import pooling

error_content = {
    "application/json":{
        "example": {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
    }
}

dbconfig = {
	"user": "root",
	"password": "!Aa12345",
	"host": "localhost",
	# "database": "tpdaytrip"
	"database": "test"
}

pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

def get_db_data(query, params) -> list:
	try:
		con = pool.get_connection()
		cursor = con.cursor()
		cursor.execute(query, params)
		data = cursor.fetchall()
		cursor.close()
		con.close()
		return data
	except mysql.connector.Error as e:
		print("Error while getting database data: ", e)

def change_db_data(query, params) -> None:
	try:
		con = pool.get_connection()
		cursor = con.cursor()
		cursor.execute(query, params)
		con.commit()
		cursor.close()
		con.close()
		return
	except mysql.connector.Error as e:
		print("Error while changing database data: ", e)
	
def turn_data_to_list(data) -> list:
	if not data == []:
		keys = ["id", "name", "category", "description", "address", "transport", "mrt", "lat", "lng", "images"]
		data_dict_lst = [{key: value for key, value in zip(keys, tup)} for tup in data]
		# 將urls處理成列表
		for data_dict in data_dict_lst:
			data_dict["images"] = data_dict["images"].split(", ")
	else:
		data_dict_lst = []
	return data_dict_lst





# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["argon2"])

# from datetime import datetime, timedelta, timezone
# expire = datetime.now(timezone.utc) + timedelta(days=7)

# import jwt

# email = "test@test.com"
# password = "test"
# query = "SELECT id, name, email, hashed_pwd FROM userinfo WHERE email = %s"
# user_info = get_db_data(query, (email, ))

# if user_info == []:
# 	print("1")
# else:
# 	hashed_pwd = user_info[0][3]
# 	if not pwd_context.verify(password, hashed_pwd):
# 		print("2")			
# 	else:
# 		data = dict(zip(["id", "name", "email"], user_info[0][0:3]))
# 		expire = datetime.now(timezone.utc) + timedelta(days=7)
# 		token = jwt.encode({**data, "exp": expire}, "secret", algorithm="HS256")
# 		decode = jwt.decode(token, "secret", algorithms=["HS256"])
# 		print(decode)

		