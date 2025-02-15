from datetime import datetime
import requests
import json
import base64
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from config import AlgolabConfig

class Algolab:
    def __init__(self, api_key, username, password):
        """
        API'ye bağlanmak için gerekli bilgileri alır
        """
        try:
            self.api_code = api_key.split("-")[1]
        except:
            self.api_code = api_key
            
        self.api_key = "API-" + self.api_code  # API key formatı: "API-XXXXX"
        self.username = username
        self.password = password
        self.config = AlgolabConfig()
        self.token = ""
        self.hash = ""
        self.sms_code = ""
        self.session = requests.Session()
        
        self.headers = {"APIKEY": self.api_key}
        print(f"Initialized with API Key: {self.api_key}")  # Debug için

    def encrypt(self, text):
        """
        Orijinal API'nin şifreleme yöntemi
        """
        iv = b'\0' * 16
        key = base64.b64decode(self.api_code.encode('utf-8'))
        cipher = AES.new(key, AES.MODE_CBC, iv)
        bytes_text = text.encode()
        padded_bytes = pad(bytes_text, 16)
        encrypted = cipher.encrypt(padded_bytes)
        return base64.b64encode(encrypted).decode("utf-8")

    def make_checker(self, endpoint, payload):
        """
        API istekleri için checker oluşturma
        """
        if len(payload) > 0:
            body = json.dumps(payload).replace(' ', '')
        else:
            body = ""
            
        print("\n=== CHECKER DETAILS ===")
        print(f"API Key: {self.api_key}")
        print(f"API Hostname: {self.config.api_hostname}")
        print(f"Endpoint: {endpoint}")
        print(f"Body: {body}")
        
        # Orijinal API'deki gibi checker hesaplama
        data = self.api_key + self.config.api_hostname + endpoint + body
        checker = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        print(f"Data for checker: {data}")
        print(f"Generated checker: {checker}")
        
        return checker

    def post(self, endpoint, payload, login=False):
        """
        API istekleri için ortak method
        """
        url = self.config.get_api_url()
        
        if not login:
            checker = self.make_checker(endpoint, payload)
            headers = {
                "APIKEY": self.api_key,
                "Checker": checker,
                "Authorization": self.hash  # Authorization header eklendi
            }
        else:
            headers = {"APIKEY": self.api_key}
            
        print("\n=== API REQUEST DETAILS ===")
        print(f"Config API URL: {self.config.api_url}")
        print(f"Config API Hostname: {self.config.api_hostname}")
        print(f"Base URL: {url}")
        print(f"Endpoint: {endpoint}")
        print(f"Full URL: {url + endpoint}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            url + endpoint,
            json=payload,
            headers=headers
        )
        
        print("\n=== API RESPONSE DETAILS ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        return response

    def login(self):
        """
        API'ye login olmak için kullanılır
        """
        try:
            if not self.api_key.startswith("API-"):
                raise Exception("API Key must start with 'API-'")
                
            username = self.encrypt(self.username)
            password = self.encrypt(self.password)
            payload = {"username": username, "password": password}
            
            print("\n=== LOGIN REQUEST DETAILS ===")
            print(f"API Key: {self.api_key}")
            print(f"API Code: {self.api_code}")
            print(f"API URL: {self.config.get_api_url()}")
            print(f"Endpoint: {self.config.URL_LOGIN_USER}")
            print(f"Full URL: {self.config.get_api_url() + self.config.URL_LOGIN_USER}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {payload}")
            
            response = self.post(self.config.URL_LOGIN_USER, payload, login=True)
            
            print("\n=== LOGIN RESPONSE DETAILS ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["content"]["token"]
                    return data
                else:
                    raise Exception(f"Login failed: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"Login request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise

    def login_control(self, sms_code):
        """
        İkinci login adımı - SMS doğrulama
        """
        try:
            print("\n=== LOGIN CONTROL ATTEMPT ===")
            
            token = self.encrypt(self.token)
            sms = self.encrypt(sms_code)
            
            payload = {'token': token, 'password': sms}
            
            response = self.post(
                endpoint=self.config.URL_LOGIN_CONTROL,
                payload=payload,
                login=True
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    self.hash = data["content"]["hash"]
                    return True
                else:
                    raise Exception(f"Login control failed: {data['message']}")
            else:
                raise Exception(f"Login control request failed with status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Login Control Exception: {str(e)}")
            raise Exception(f"Login control error: {str(e)}")

    def get_equity_info(self, symbol):
        try:
            payload = {'symbol': symbol}
            response = self.post(
                endpoint=self.config.URL_GET_EQUITY_INFO,
                payload=payload,
                login=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get equity info: {response.text}")
        except Exception as e:
            raise Exception(f"Get equity info error: {str(e)}")

    def get_positions(self):
        try:
            response = self.post(
                endpoint=self.config.URL_GET_INSTANT_POSITION,
                payload={},
                login=False
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
                "symbol": symbol,
                "direction": "Buy" if side.upper() == "BUY" else "Sell",
                "pricetype": "limit" if order_type.upper() == "LIMIT" else "piyasa",
                "lot": str(quantity),
                "sms": False,
                "email": False,
                "subAccount": ""
            }
            
            if price is not None and order_type.upper() == "LIMIT":
                payload["price"] = str(price)
            else:
                payload["price"] = ""

            response = self.post(
                endpoint=self.config.URL_SEND_ORDER,
                payload=payload,
                login=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to submit order: {response.text}")
        except Exception as e:
            raise Exception(f"Submit order error: {str(e)}")

    def session_refresh(self):
        try:
            response = self.post(
                endpoint=self.config.URL_SESSION_REFRESH,
                payload={},
                login=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to refresh session: {response.text}")
        except Exception as e:
            raise Exception(f"Session refresh error: {str(e)}")

    def get_todays_transaction(self):  # Metod ismini config ile uyumlu hale getirdik
        """
        Günlük işlemleri ve bekleyen emirleri getirir
        """
        try:
            response = self.post(
                endpoint=self.config.URL_GET_TODAYS_TRANSACTION,  # Config'deki isimle aynı
                payload={},
                login=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get today's transactions: {response.text}")
        except Exception as e:
            raise Exception(f"Get today's transactions error: {str(e)}")
