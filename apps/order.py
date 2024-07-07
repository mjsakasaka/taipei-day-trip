from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import time
import random
import string
import utils

order = APIRouter()


class Attraction(BaseModel):
    id: int
    name: str
    address: str
    image: str

class Trip(BaseModel):
    attraction: Attraction
    date: str
    time: str    

class Contact(BaseModel):
    name: str
    email: str
    phone: str

class Order(BaseModel):
    price: int
    trip: Trip
    contact: Contact

class PaymentRequest(BaseModel):
    prime: str
    order: Order

class UserData(BaseModel):
    id: int
    name: str
    email: str

class TokenData(BaseModel):
    data: UserData

def generate_order_number():
    current_time = time.localtime()
    timestamp = time.strftime("%Y%m%d%H%M%S", current_time)
    random_str = ''.join(random.choices(string.digits, k=6))
    order_number = timestamp + random_str
    return order_number

def generate_payment_id():
    current_time = time.localtime()
    timestamp = time.strftime("%Y%m%d%H%M%S", current_time)
    random_str = ''.join(random.choices(string.digits, k=8))
    payment_id = timestamp + random_str
    return payment_id

def save_order_record(order_number: str, request: PaymentRequest, token_data: TokenData):
    try:
        user_id = token_data["data"]["id"]
        order_price = request.order.price
        trip_attr_id = request.order.trip.attraction.id
        trip_date = request.order.trip.date
        trip_time = request.order.trip.time
        contact_name = request.order.contact.name
        contact_email = request.order.contact.email
        contact_phone = request.order.contact.phone
        payment_status = "UNPAID"
        query = '''
        INSERT INTO orders (order_number, user_id, order_price, trip_attr_id, trip_date, trip_time, payment_status, contact_name, contact_email, contact_phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (order_number, user_id, order_price, trip_attr_id, trip_date, trip_time, payment_status, contact_name, contact_email, contact_phone)
        utils.change_db_data(query, values)
        return 1
    except:
        return

async def make_payment(order_number: str, request: PaymentRequest):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': TAPPAY_PARTNER_KEY
    }
    cardholder = {
        'phone_number': request.order.contact.phone,
        'name': request.order.contact.name,
        'email': request.order.contact.email
    }
    data = {
        'prime': request.prime,
        'partner_key': TAPPAY_PARTNER_KEY,
        'merchant_id': TAPPAY_MERCHANT_ID,
        'amount': request.order.price,
        'details': request.order.trip.attraction.name,
        'cardholder': cardholder,
        'order_number': order_number
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TAPPAY_API_URL, headers=headers, json=data)
    return response

def save_payment_record(payment_result):
    payment_id = generate_payment_id()
    rec_trade_id = payment_result.get("rec_trade_id")
    order_number = payment_result.get("order_number")
    transaction_time_millis = payment_result.get("transaction_time_millis")
    amount = payment_result.get("amount")
    query = '''
    INSERT INTO payment (payment_id, rec_trade_id, order_number, transaction_time_millis, amount)
    VALUES (%s, %s, %s, %s, %s)
    '''
    values = payment_id, rec_trade_id, order_number, transaction_time_millis, amount
    utils.change_db_data(query, values)

TAPPAY_PARTNER_KEY = 'partner_m6CyvGkNLlGunsg4BosVWkoHC4w5z6kOrRP3bHTv9rCH0gkHFLDvRua5'
TAPPAY_MERCHANT_ID = 'tppf_mjriver_GP_POS_1'
TAPPAY_API_URL = 'https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime'

@order.post("/api/orders", summary="建立新的訂單，并完成付款程序")
async def create_order(request: PaymentRequest, token_data: dict | None = Depends(utils.decode_token)):
    if not token_data:
        response_msg = {"error": True,"message": "未登入系統，拒絕存取"}
        return JSONResponse(response_msg, status_code=403)
    
    # create an order record
    order_number = generate_order_number()
    order_record = save_order_record(order_number, request, token_data)
    if not order_record:
        response_msg = {"error": True,"message": "訂單建立失敗，存入資料庫發生錯誤"}
        return JSONResponse(response_msg, status_code=400)

    # call tappay api to make payment
    try:
        response = await make_payment(order_number, request)
    except:
        response_msg = {"error": True,"message": "付款失敗，連接tappay api失敗"}
        return JSONResponse(response_msg, status_code=400)
    if response.status_code != 200:
        response_msg = {"error": True,"message": "付款失敗，呼叫tappay api不成功"}
        return JSONResponse(response_msg, status_code=400)
    result = response.json()
    if result.get("status") != 0:
        print(result)
        response_msg = {"error": True,"message": "付款失敗，tappay api返回錯誤"}
        return JSONResponse(response_msg, status_code=400)
    
    # save payment record
    save_payment_record(result)
    # mark order record as PAID
    query = "UPDATE orders SET payment_status = %s WHERE order_number = %s"
    utils.change_db_data(query, ("PAID", order_number))

    # send order number back to front end
    response_data = {
        "data": {
            "number": order_number,
            "payment": {
            "status": 0,
            "message": "付款成功"
            }
        }
    }
    return JSONResponse(response_data, status_code=200)


@order.get("/api/order/{order_number}", summary="根據訂單編號取得訂單資訊")
async def get_order_data(order_number: str, token_data: dict | None = Depends(utils.decode_token)):
    if not token_data:
        response_msg = {"error": True,"message": "未登入系統，拒絕存取"}
        return JSONResponse(response_msg, status_code=403)
    
    query = '''
    SELECT order_price, trip_attr_id, trip_date, trip_time, contact_name, contact_email, contact_phone
    FROM orders WHERE order_number = %s
    '''
    raw_order_data = utils.get_db_data(query, (order_number, ))
    order_data = raw_order_data[0]
    # attraction {id, name, address, image}
    attr_id = order_data[1]
    query = "SELECT name, address, file FROM taipei_attractions WHERE id = %s"
    raw_attr_data = utils.get_db_data(query, (attr_id, ))
    image = raw_attr_data[0][2].split(",")[0]
    attr_dict_keys = ("id", "name", "address", "image")
    attr_dict_values = (attr_id, raw_attr_data[0][0], raw_attr_data[0][1], image)
    attr_dict = dict(zip(attr_dict_keys, attr_dict_values))
    # trip {attraction, date, time}
    trip_dict = {"attraction": attr_dict, "date": str(order_data[2]), "time": order_data[3]}
    # contact {name, email, phone}
    contact_keys = ("name", "email", "phone")
    contact_dict = dict(zip(contact_keys, order_data[4:]))
    # data {number, price, trip, contact, status}
    data_dict_keys = ("number", "price", "trip", "contact", "status")
    data_dict_values = (order_number, float(order_data[0]), trip_dict, contact_dict, 1)
    data_dict = dict(zip(data_dict_keys, data_dict_values))
    return {"data": data_dict}