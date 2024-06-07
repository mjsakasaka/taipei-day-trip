from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Annotated
import utils

user = APIRouter()

class User_info(BaseModel):
	name: str
	email: EmailStr
	password: str
	
@user.post(
		"/api/user",
		summary="註冊一個新的會員",
		responses={
			200: {"description": "註冊成功"},
			400: {"description": "註冊失敗，重複的 Email 或其他原因", "content": utils.error_content},
			500: {"description": "伺服器內部錯誤", "content": utils.error_content},
		}
)
async def sign_up(request: Request, user_info: User_info):
	try:
		pass
	except:
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(content=response_msg)

	return {"ok": True}