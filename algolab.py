from datetime import datetime
import requests
import json
import base64
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from config import AlgolabConfig

class Algolab:
    def __init__(self, config: AlgolabConfig):
        self.config = config
        self.token = ""
        self.hash = ""
        self.session = requests.Session()
        self.headers = {"APIKEY": self.config.get_api_key()}

    def encrypt(self, text):
        key = b'1234567890123456'
        cipher = AES.new(key, AES.MODE_CBC, key)
        encrypted = cipher.encrypt(pad(text.encode(), 16))
        return base64.b64encode(encrypted).decode()

    def login(self):
        try:
            # İlk adım: Login isteği
            username = self.encrypt(self.config.get_username())
            password = self.encrypt(self.config.get_password())
            payload = {"username": username, "password": password}
            
            response = requests.post(
                f"{self.config.get_api_url()}/auth/login/user",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    self.token = data["content"]["token"]
                    
                    # İkinci adım: SMS gönderimi için istek
                    sms_response = requests.post(
                        f"{self.config.get_api_url()}/auth/login/sms",
                        json={"token": self.encrypt(self.token)},
                        headers=self.headers
                    )
                    
                    if sms_response.status_code == 200:
                        sms_data = sms_response.json()
                        if sms_data["success"]:
                            return True
                        else:
                            raise Exception(f"SMS request failed: {sms_data['message']}")
                    else:
                        raise Exception(f"SMS request failed with status {sms_response.status_code}")
                else:
                    raise Exception(f"Login failed: {data['message']}")
            else:
                raise Exception(f"Login request failed: {response.text}")
        except Exception as e:
            raise Exception(f"Login error: {str(e)}")

    def login_control(self, sms_code):
        try:
            token = self.encrypt(self.token)
            sms = self.encrypt(sms_code)
            payload = {'token': token, 'password': sms}
            
            response = requests.post(
                f"{self.config.get_api_url()}/auth/login/control",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    self.hash = data["content"]["hash"]
                    return True
                else:
                    raise Exception(f"Login control failed: {data['message']}")
            else:
                raise Exception(f"Login control request failed: {response.text}")
        except Exception as e:
            raise Exception(f"Login control error: {str(e)}")

    def get_equity_info(self, symbol):
        try:
            payload = {'symbol': symbol}
            response = requests.post(
                f"{self.config.get_api_url()}/data/getequityinfo",
                json=payload,
                headers={"HASH": self.hash, **self.headers}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get equity info: {response.text}")
        except Exception as e:
            raise Exception(f"Get equity info error: {str(e)}")

    def get_positions(self):
        try:
            response = requests.post(
                f"{self.config.get_api_url()}/data/instantposition",
                json={},
                headers={"HASH": self.hash, **self.headers}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get positions: {response.text}")
        except Exception as e:
            raise Exception(f"Get positions error: {str(e)}")

    def submit_order(self, symbol, side, quantity, price=None, order_type="MARKET"):
        try:
            payload = {
                "Symbol": symbol,
                "Side": "Buy" if side.upper() == "BUY" else "Sell",
                "Quantity": quantity,
                "SubAccount": "1"  # Default sub account
            }
            
            if price is not None and order_type.upper() == "LIMIT":
                payload["Price"] = price
                payload["OrderType"] = "Limit"
            else:
                payload["OrderType"] = "Market"

            response = requests.post(
                f"{self.config.get_api_url()}/order/sendorder",
                json=payload,
                headers={"HASH": self.hash, **self.headers}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to submit order: {response.text}")
        except Exception as e:
            raise Exception(f"Submit order error: {str(e)}")

    def session_refresh(self):
        try:
            response = requests.post(
                f"{self.config.get_api_url()}/auth/sessionrefresh",
                json={},
                headers={"HASH": self.hash, **self.headers}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to refresh session: {response.text}")
        except Exception as e:
            raise Exception(f"Session refresh error: {str(e)}")
