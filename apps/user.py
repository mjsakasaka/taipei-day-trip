from fastapi import *
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated
import utils
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

user = APIRouter()

# sign up new member
class UserInfo(BaseModel):
	name: str
	email: str
	password: str

pwd_context = CryptContext(schemes=["argon2"])

def get_hashed_pwd(password: str) -> str:
	return pwd_context.hash(password)
	
@user.post(
		"/api/user",
		summary="註冊一個新的會員",
		responses={
			200: {"description": "註冊成功"},
			400: {"description": "註冊失敗，重複的 Email 或其他原因", "content": utils.error_content},
			500: {"description": "伺服器內部錯誤", "content": utils.error_content},
		}
)
async def sign_up(request: Request, user_info: UserInfo):
	try:
		# check if email already exists
		query = "SELECT email FROM userInfo WHERE email = %s"
		email_check = utils.get_db_data(query, (user_info.email, ))
		if email_check != []:
			response_msg = {
				"error": True,
				"message": "重複的email"
			}
			return JSONResponse(content=response_msg, status_code=400)
		else:
			hashed_pwd = get_hashed_pwd(user_info.password)
			query = "INSERT INTO userInfo (name, email, hashed_pwd) VALUES (%(name)s, %(email)s, %(hashed_pwd)s);"
			utils.change_db_data(query, {"name": user_info.name, "email": user_info.email, "hashed_pwd": hashed_pwd})
		return {"ok": True}
	except:
		response_msg = {
			"error": True,
			"message": "伺服器內部錯誤"
		}
		return JSONResponse(content=response_msg)

# get current user information
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = utils.SECRET_KEY
ALGORITHM = utils.ALGORITHM

def decode_token(token: str):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		data = payload.get("data")
		if data is None:
			return None
		return data
	except:
		return None
	
def get_current_user(token: str = Depends(oauth2_scheme)):
	return decode_token(token)

@user.get(
		"/api/user/auth",
		summary="取得當前登入的會員信息",
)
async def get_user_info(data: str = Depends(get_current_user)):
	return data


# sign in

class UserInput(BaseModel):
	email: str
	password: str

@user.put(
		"/api/user/auth",
		summary="登入會員賬戶",
)
async def sign_in(request: Request, user_input: UserInput):
	try:
		# check email and password
		query = "SELECT id, name, email, hashed_pwd FROM userInfo WHERE email = %s"
		user_info = utils.get_db_data(query, (user_input.email, ))
		response_msg = {
			"error": True,
			"message": "賬號或密碼錯誤"
		}
		if user_info == []:
			return JSONResponse(response_msg, status_code=400)
		else:
			hashed_pwd = user_info[0][3]
			if not pwd_context.verify(user_input.password, hashed_pwd):
				return JSONResponse(response_msg, status_code=400)				
			else:
			# encode data and return token
				data = dict(zip(["id", "name", "email"], user_info[0][0:3]))
				to_encode = {"data": {"data": data}}
				expire = datetime.now(timezone.utc) + timedelta(days=7)
				token = jwt.encode({**to_encode, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
				response = {"token": token}
				return JSONResponse(response)
	except:
		response_msg = {
			"error": True,
			"message": "伺服器内部錯誤"
		}
		return JSONResponse(response_msg, status_code=500)


