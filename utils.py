import mysql.connector

error_content = {
    "application/json":{
        "example": {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
    }
}

def get_db_data(query, params) -> list:
    con = mysql.connector.connect(
		user = "root",
		password = "!Aa12345",
		host = "localhost",
		database = "tpdaytrip"
	)
    cursor = con.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    con.close()
    return data

def change_db_data(query, params) -> None:
	con = mysql.connector.connect(
		user = "root",
		password = "!Aa12345",
		host = "localhost",
		database = "tpdaytrip"
	)
	cursor = con.cursor()
	cursor.execute(query, params)
	con.commit()
	con.close()
	
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