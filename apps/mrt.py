from fastapi import *
from fastapi.responses import JSONResponse
from utils import *

mrt = APIRouter()

@mrt.get("/api/mrts", tags=["MRT Station"], summary="取得捷運站名稱列表",
		description="取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序",
		responses={
			200: {"description": "正常運作", "content": {"application/json": {"example": {"data": ["劍潭"]}}}},
			500: {"description": "伺服器內部錯誤", "content": error_content}
		})
async def get_mrt_list(request: Request):
	try:
		# 取得所有捷運站名稱
		query = "SELECT MRT, COUNT(MRT) FROM taipei_attractions WHERE NOT MRT IS NULL GROUP BY MRT ORDER BY COUNT(MRT) DESC;"
		data = get_db_data(query, params=())
		mrt_lst = [i[0] for i in data]
		response_data = {"data": mrt_lst}
		return JSONResponse(content=response_data)
	except:
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(status_code=500, content=response_msg)
	