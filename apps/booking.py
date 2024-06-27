from datetime import date
from fastapi import *
from fastapi.exceptions import ValidationException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel, ValidationError
from typing import Annotated
import utils

book = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# get unbooked information
SECRET_KEY = utils.SECRET_KEY
ALGORITHM = utils.ALGORITHM

def decode_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        data = payload.get("data")
        if data is None:
            return None
        return data
    except:
        return None

@book.get("/api/booking", summary="取得尚未下單的預定行程")
async def get_unbooked_infor(token_data: dict | None = Depends(decode_token)):
    try:
        if not token_data:
            response_msg = {
                "error": True,
                "message": "未登入系統，拒絕存取"
            }
            return JSONResponse(response_msg, status_code=403)
        else:
            user_id = token_data["data"]["id"]
            # get pending schedule
            query = "SELECT attractionId, date, time, price FROM pending WHERE userId = %s"
            pending_data = utils.get_db_data(query, (user_id, ))
            attraction_id = pending_data[0][0]
            pending_dict = dict(zip(["date", "time", "price"], pending_data[0][1:]))
            # get attraction data
            query = "SELECT id, name, address, file FROM taipei_attractions WHERE id = %s"
            attraction_data = utils.get_db_data(query, (attraction_id, ))
            attraction_dict = dict(zip(["id", "name", "address", "image"], list(attraction_data[0][0:3]) + [attraction_data[0][3].split(",")[0]]))
            response_data = {"data": {"attraction": attraction_dict, **pending_dict}}
            return response_data
    except:
        return None
    

# create new schedule
class Schedule(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int

@book.post("/api/booking", summary="建立新的預定行程")
async def create_schedule(schedule: Schedule, token_data: dict | None = Depends(decode_token)):
    try:
        if not token_data:
            response_msg = {
                "error": True,
                "message": "未登入系統，拒絕存取"
            }
            return JSONResponse(response_msg, status_code=403)
        else:
            user_id = token_data["data"]["id"]
            utils.change_db_data("DELETE FROM pending WHERE userId = %s", (user_id, ))
            query = '''INSERT INTO pending (userId, attractionId, date, time, price)
            VALUES (%s, %s, %s, %s, %s)'''
            values = (user_id, schedule.attractionId, schedule.date, schedule.time, schedule.price)
            utils.change_db_data(query, values)
            # check if the data is successfully built
            data = utils.get_db_data("SELECT * FROM pending WHERE userId=%s", (user_id, ))
            if data == []:
                response_msg = {
                    "error": True,
                    "message": "建立失敗，輸入不正確或其他原因"
                }
                return JSONResponse(response_msg, status_code=400)
            return {'ok': True}
    except:
        response_msg = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return JSONResponse(response_msg, status_code=500)
    

# delete current booking schedule
@book.delete("/api/booking", summary="刪除目前的預定行程")
async def delete_schedule(token_data: dict | None = Depends(decode_token)):
    try:
        if not token_data:
            response_msg = {
                "error": True,
                "message": "未登入系統，拒絕存取"
            }
            return JSONResponse(response_msg, status_code=403)
        else:
            user_id = token_data["data"]["id"]
            utils.change_db_data("DELETE FROM pending WHERE userId = %s", (user_id, ))
            return {"ok": True}
    except:
        response_msg = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return JSONResponse(response_msg, status_code=500)