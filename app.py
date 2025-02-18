from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from algolab import Algolab
from config import AlgolabConfig
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="Algolab Trading")

# Global değişkenler
algolab_instance = None
last_api_call = None

class LoginRequest(BaseModel):
    username: str
    password: str

class SMSRequest(BaseModel):
    sms_code: str

def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return value

def wait_for_api():
    global last_api_call
    if last_api_call is not None:
        elapsed = time.time() - last_api_call
        if elapsed < 5:
            time.sleep(5 - elapsed)
    last_api_call = time.time()

@app.post("/login")
async def login(login_request: LoginRequest):
    global algolab_instance
    try:
        wait_for_api()
        algolab_instance = Algolab()
        result = algolab_instance.login(login_request.username, login_request.password)
        
        if result.get("Status") == "Successful":
            if result.get("Result", {}).get("IsSMSRequired", False):
                return {"status": "sms_required"}
            return {"status": "success"}
        else:
            raise HTTPException(status_code=401, detail=result.get("Message", "Login failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-sms")
async def verify_sms(sms_request: SMSRequest):
    global algolab_instance
    if not algolab_instance:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
        wait_for_api()
        result = algolab_instance.verify_sms(sms_request.sms_code)
        if result.get("Status") == "Successful":
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail=result.get("Message", "SMS verification failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account-info")
async def get_account_info():
    global algolab_instance
    if not algolab_instance:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
        wait_for_api()
        account_info = algolab_instance.get_account_info()
        positions = algolab_instance.get_positions()
        orders = algolab_instance.get_orders()
        
        return {
            "account_info": account_info,
            "positions": positions,
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logout")
async def logout():
    global algolab_instance
    algolab_instance = None
    return {"status": "success"}

@app.post("/submit-order")
async def submit_order(request: Request):
    global algolab_instance
    if not algolab_instance:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
        wait_for_api()
        data = await request.json()
        symbol = data.get("symbol")
        quantity = data.get("quantity")
        side = data.get("side")
        price = data.get("price")
        order_type = data.get("orderType")
        
        if not symbol or not quantity or not side or not price or not order_type:
            raise HTTPException(status_code=400, detail="Invalid order data")
        
        result = algolab_instance.submit_order(symbol, quantity, side, price, order_type)
        if result.get("Status") == "Successful":
            return {"status": "success", "orderId": result.get("Result", {}).get("orderId")}
        else:
            raise HTTPException(status_code=400, detail=result.get("Message", "Order submission failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def webhook(request: Request):
    global algolab_instance
    if not algolab_instance:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
        data = await request.json()
        symbol = data.get("symbol")
        side = data.get("side")
        quantity = data.get("quantity")
        price = data.get("price")
        order_type = data.get("orderType")
        
        if not symbol or not side or not quantity or not price or not order_type:
            raise HTTPException(status_code=400, detail="Invalid webhook data")
        
        result = algolab_instance.submit_order(symbol, quantity, side, price, order_type)
        if result.get("Status") == "Successful":
            return {"status": "success", "orderId": result.get("Result", {}).get("orderId")}
        else:
            raise HTTPException(status_code=400, detail=result.get("Message", "Order submission failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
