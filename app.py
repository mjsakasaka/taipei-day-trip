from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from typing import Annotated
from utils import *
import uvicorn
app = FastAPI()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

error_content = {
    "application/json":{
        "example": {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
    }
}
# Attraction
@app.get("/api/attractions", tags=["Attraction"], summary="取得景點資料表",
		description="取得不同分頁的旅游景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選",
		responses={
			200: {"description": "正常運作"},
			500: {"description": "伺服器內部錯誤", "content": error_content}
		})
async def get_attractions(
	request: Request,
	page: Annotated[int, Query(ge=0, description="要取得的分頁，每頁12筆資料")],
	keyword: Annotated[str | None, Query(description="用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選")] = None
):
	try:
		# 從mysql按照page取得12筆資料
		if keyword == None:
			keyword = ""
		like_keyword = f"%{keyword}%"
		offset = page * 12
		query = '''
		SELECT id, name, CAT, description, address, direction, MRT, latitude, longitude, file
		FROM taipei_attractions
		WHERE MRT=%(keyword)s OR name LIKE %(like_keyword)s
		LIMIT 12 OFFSET %(offset)s
		'''
		data = get_db_data(query, {"keyword": keyword, "like_keyword": like_keyword, "offset": offset})
		# 將獲取的mysql data轉換成字典列表
		data_dict_lst = turn_data_to_list(data)
		if data != [] and len(data_dict_lst) == 12:
			next_page = page + 1
		else:
			next_page = None
		# 返回response data
		response_data = {
			"nextPage": next_page,
			"data": data_dict_lst
		}
		return JSONResponse(content=response_data)
	except: # 500錯誤處理：伺服器內部錯誤
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(status_code=500, content=response_msg)

@app.get("/api/attraction/{attractionId}", tags=["Attraction"], summary="根據景點編號取得景點資料表",
		responses={
			200: {"description": "正常運作"},
			400: {"description": "景點編號不正確", "content": error_content},
			500: {"description": "伺服器內部錯誤", "content": error_content}
		})
async def get_attraction_by_id(
	request: Request,
	attractionId: Annotated[int, Path(description="景點編號")]
):
	try:
		query = '''SELECT id, name, CAT, description, address, direction, MRT, latitude, longitude, file
		FROM taipei_attractions WHERE id=%s'''
		data = get_db_data(query, (attractionId, ))
		if not data == []:
			data_dict = turn_data_to_list(data)[0]
			response_data = {"data": data_dict}
			return JSONResponse(content=response_data)
		else: # 400错误处理：景點編號不正確
			response_msg = {
				"error": True,
				"message": "景點編號不正確"
			}
			return JSONResponse(status_code=400, content=response_msg)
	except: # 500錯誤處理：
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(status_code=500, content=response_msg)


# MRT Station
@app.get("/api/mrts", tags=["MRT Station"], summary="取得捷運站名稱列表",
		description="取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序",
		responses={
			200: {"description": "正常運作", "content": {"application/json": {"example": {"data": ["劍潭"]}}}},
			500: {"description": "伺服器內部錯誤", "content": error_content}
		})
async def get_mrt_list(request: Request):
	try:
		# 取得所有景點的名稱和捷運站名稱
		query = "SELECT name, MRT FROM taipei_attractions;"
		data = get_db_data(query, params=())
		# 創建字典{"捷運站名": ["經典"]}
		mrt_spot_dic = {}
		for tup in data:
			if tup[1] == None:
				pass
			elif not tup[1] in mrt_spot_dic:
				mrt_spot_dic[tup[1]] = [tup[0]]
			else:
				mrt_spot_dic[tup[1]].append(tup[0])
		mrt_lst = sorted(mrt_spot_dic.keys(), key=lambda x: len(mrt_spot_dic[x]), reverse=True)
		response_data = {"data": mrt_lst}
		return JSONResponse(content=response_data)
	except:
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(status_code=500, content=response_msg)

if __name__ == '__main__':
    uvicorn.run("app:app", port=8000, reload=True, host='0.0.0.0')