from fastapi import *
from fastapi.responses import JSONResponse
from typing import Annotated
import utils

attrac = APIRouter()


@attrac.get("/api/attractions", tags=["Attraction"], summary="取得景點資料表",
		description="取得不同分頁的旅游景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選",
		responses={
			200: {"description": "正常運作"},
			500: {"description": "伺服器內部錯誤", "content": utils.error_content}
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
		data = utils.get_db_data(query, {"keyword": keyword, "like_keyword": like_keyword, "offset": offset})
		# 將獲取的mysql data轉換成字典列表
		data_dict_lst = utils.turn_data_to_list(data)
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
	
@attrac.get("/api/attraction/{attractionId}", tags=["Attraction"], summary="根據景點編號取得景點資料表",
		responses={
			200: {"description": "正常運作"},
			400: {"description": "景點編號不正確", "content": utils.error_content},
			500: {"description": "伺服器內部錯誤", "content": utils.error_content}
		})
async def get_attraction_by_id(
	request: Request,
	attractionId: Annotated[int, Path(description="景點編號")]
):
	try:
		query = '''SELECT id, name, CAT, description, address, direction, MRT, latitude, longitude, file
		FROM taipei_attractions WHERE id=%s'''
		data = utils.get_db_data(query, (attractionId, ))
		if not data == []:
			data_dict = utils.turn_data_to_list(data)[0]
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