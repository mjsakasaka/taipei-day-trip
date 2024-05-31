import json
import mysql.connector

def filter_urls(urls_string) -> str:
    urls_string = urls_string.lower()
    file_lst = urls_string.split("http")
    new_file_lst = []
    for i in range(len(file_lst)):
        file_lst[i] = "http" + file_lst[i]
        url = file_lst[i]
        if url[-3:] == "jpg" or url[-3:] == "png":
            new_file_lst.append(url)
    return ", ".join(new_file_lst)

# 获取json文件data
with open('taipei-attractions.json', 'r', encoding="utf-8") as file:
    data = json.load(file)
results = data["result"]["results"] # 是包含景点字典的列表

# 连接mysql, 创建table
con = mysql.connector.connect(
    user="root",
    password="!Aa12345",
    host="localhost",
    database="tpdaytrip"
)
cursor = con.cursor()
create_table_query = '''
CREATE TABLE taipei_attractions(
id INT AUTO_INCREMENT PRIMARY KEY,
rate INT,
direction TEXT,
name VARCHAR(255),
date DATE,
longitude VARCHAR(255),
REF_WP VARCHAR(255),
avBegin DATE,
langinfo VARCHAR(255),
MRT VARCHAR(255),
SERIAL_NO VARCHAR(255),
RowNumber VARCHAR(255),
CAT VARCHAR(255),
MEMO_TIME TEXT,
POI VARCHAR(255),
file TEXT,
idpt VARCHAR(255),
latitude VARCHAR(255),
description TEXT,
_id INT,
avEnd DATE,
address VARCHAR(255)
);
'''
cursor.execute(create_table_query)
# 将景点信息逐个储存到database
for attr_dict in results:
    # 处理图片url
    attr_dict["file"] = filter_urls(attr_dict["file"])
    # 存入mysql database
    values = tuple(attr_dict.values())
    query = '''INSERT INTO taipei_attractions(rate,direction,name,date,longitude,REF_WP,avBegin,langinfo,MRT,SERIAL_NO,RowNumber,CAT,MEMO_TIME,POI,file,idpt,latitude,description,_id,avEnd,address) 
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    cursor.execute(query, values)
con.commit()
con.close()


