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
    def __init__(self, username, password):
        """
        Algolab API'si için gerekli parametreler
        :param username: Kullanıcı adı
        :param password: Şifre
        """
        self.config = AlgolabConfig()
        self.api_key = self.config.api_key
        self.username = username
        self.password = password
        self.token = None
        self.hash = None

    def encrypt(self, text):
        """
        Kullanıcı adı ve şifre için şifreleme
        """
        try:
            # API key'i doğru formata getir
            api_code = self.api_key.split("-")[1]  # "API-XXXX" formatından "XXXX" kısmını al
            key = base64.b64decode(api_code)  # Base64 decode
            
            # Text'i şifrele
            text = str(text).encode('utf-8')
            cipher = AES.new(key, AES.MODE_ECB)
            padded = pad(text, AES.block_size)
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            raise

    def make_checker(self, endpoint, payload):
        """
        API istekleri için Checker header'ı oluşturur
        """
        if len(payload) > 0:
            body = json.dumps(payload).replace(' ', '')
        else:
            body = ""
        data = self.api_key + self.config.api_hostname + endpoint + body
        checker = hashlib.sha256(data.encode('utf-8')).hexdigest()
        return checker

    def post(self, endpoint, payload=None, login=True):
        """
        API'ye POST isteği gönderme
        """
        try:
            if not login:
                headers = {"APIKEY": self.api_key}
            else:
                checker = self.make_checker(endpoint, payload or {})
                headers = {
                    "APIKEY": self.api_key,
                    "Checker": checker,
                    "Authorization": f"Bearer {self.hash}"  # Bearer token ekle
                }
                
            url = self.config.api_url
            
            print("\n=== API REQUEST DETAILS ===")
            print(f"Base URL: {url}")
            print(f"Endpoint: {endpoint}")
            print(f"Final URL: {url}{endpoint}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Payload: {json.dumps(payload, indent=2) if payload else None}")
            
            response = requests.post(
                url=url + endpoint,
                json=payload,
                headers=headers,
                verify=False
            )
            
            print("\n=== API RESPONSE DETAILS ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Text: {response.text}")
            
            # Try to parse response as JSON
            try:
                response_data = response.json()
            except:
                response_data = {
                    "success": False,
                    "message": response.text,
                    "content": None
                }
            
            # Add status code to response data
            response_data["status_code"] = response.status_code
            
            # Check for error status codes
            if response.status_code != 200:
                raise Exception(f"Submit order request failed with status {response.status_code}: {response.text}")
                
            return response_data
            
        except Exception as e:
            print(f"POST request error: {str(e)}")
            raise

    def login(self):
        """
        Login işlemi
        """
        try:
            payload = {
                "username": self.encrypt(self.username),
                "password": self.encrypt(self.password)
            }
            
            response = self.post(self.config.URL_LOGIN, payload=payload, login=False)
            
            if response.get('success'):
                self.token = response.get('content', {}).get('token', '')
                return response
            else:
                raise Exception(f"Login failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise

    def login_control(self):
        """
        Login kontrolü
        """
        try:
            payload = {
                "token": self.token
            }
            response = self.post(self.config.URL_LOGIN_CONTROL, payload=payload, login=True)
            
            if response.get('success'):
                self.hash = response.get('content', {}).get('hash', '')
                return response
            else:
                raise Exception(f"Login control failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Login control error: {str(e)}")
            raise

    def get_instant_position(self, subaccount=""):
        """
        Anlık pozisyon bilgilerini çeker
        """
        try:
            payload = {'Subaccount': subaccount}
            response = self.post(self.config.URL_GET_INSTANT_POSITION, payload=payload, login=True)
            return response
        except Exception as e:
            print(f"Failed to get positions: {str(e)}")
            raise

    def get_equity_info(self, symbol):
        """
        Sembol bilgilerini çeker
        """
        try:
            payload = {'symbol': symbol}
            response = self.post(self.config.URL_GET_EQUITY_INFO, payload=payload, login=True)
            return response
        except Exception as e:
            print(f"Failed to get equity info: {str(e)}")
            raise

    def submit_order(self, symbol, quantity, side, price=None, order_type="limit"):
        """
        Emir gönderir
        :param symbol: Sembol Kodu
        :param quantity: İşlem Miktarı
        :param side: İşlem Yönü (ALIŞ/SATIŞ)
        :param price: Fiyat (LIMIT emirlerde zorunlu)
        :param order_type: Emir Tipi (limit/piyasa)
        """
        try:
            # Login kontrolü
            if not self.hash:
                print("Yeniden login yapılıyor...")
                self.login()
                if not self.hash:
                    raise Exception("Login başarısız")

            # API'nin beklediği formata dönüştür
            side_map = {"ALIŞ": "BUY", "SATIŞ": "SELL"}
            
            payload = {
                "symbol": symbol.upper(),
                "direction": side_map.get(side, side),  # Eğer side zaten BUY/SELL ise onu kullan
                "pricetype": order_type.lower(),
                "price": str(price) if price is not None else "",
                "lot": str(quantity),
                "sms": False,  # Varsayılan olarak kapalı
                "email": False,  # Varsayılan olarak kapalı
                "subAccount": ""  # Varsayılan olarak boş
            }
            
            print("\n=== EMIR DETAYLARI ===")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Headers: APIKEY={self.api_key}, Hash={self.hash}")
            
            response = self.post(self.config.URL_SEND_ORDER, payload=payload, login=True)
            return response
        except Exception as e:
            print(f"Failed to submit order: {str(e)}")
            raise

    def session_refresh(self):
        """
        Oturumu yeniler
        """
        try:
            response = self.post(self.config.URL_SESSION_REFRESH, payload={}, login=True)
            return response
        except Exception as e:
            print(f"Failed to refresh session: {str(e)}")
            raise

    def get_todays_transaction(self, subaccount=""):
        """
        Günlük işlemleri çeker
        """
        try:
            payload = {'Subaccount': subaccount}
            response = self.post(self.config.URL_GET_TODAYS_TRANSACTION, payload=payload, login=True)
            return response
        except Exception as e:
            print(f"Failed to get today's transactions: {str(e)}")
            raise
