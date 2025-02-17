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
            
        self.api_key = "API-" + self.api_code
        self.username = username
        self.password = password
        
        self.config = AlgolabConfig()
        self.token = ""
        self.hash = ""
        
        self.headers = {"APIKEY": self.api_key}

    def encrypt(self, text):
        """
        Orijinal API'nin şifreleme yöntemi
        """
        try:
            iv = b'\0' * 16
            key = base64.b64decode(self.api_code.encode('utf-8'))
            cipher = AES.new(key, AES.MODE_CBC, iv)
            bytes_text = text.encode()
            padded_bytes = pad(bytes_text, 16)
            encrypted = cipher.encrypt(padded_bytes)
            result = base64.b64encode(encrypted).decode("utf-8")
            return result
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
                    "Authorization": self.hash
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
            return response_data
            
        except Exception as e:
            print(f"POST request error: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "content": None,
                "status_code": 500
            }

    def login(self):
        """
        API'ye login olma işlemi
        """
        try:
            u = self.encrypt(self.username)
            p = self.encrypt(self.password)
            payload = {"username": u, "password": p}
            
            response = self.post(
                endpoint=self.config.URL_LOGIN_USER,
                payload=payload,
                login=False  # İlk login'de header'da sadece APIKEY olmalı
            )
            
            if response.status_code == 200:
                data = response
                if data.get('success'):
                    self.token = data.get('content', {}).get('token', '')
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
        SMS doğrulaması için kullanılır
        """
        try:
            token = self.encrypt(self.token)
            password = self.encrypt(sms_code)
            payload = {"token": token, "password": password}
            
            response = self.post(self.config.URL_LOGIN_CONTROL, payload=payload, login=True)
            
            if response.status_code == 200:
                data = response
                if data.get("success"):
                    self.hash = data["content"]["hash"]
                    return data
                else:
                    raise Exception(f"Login control failed: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"Login control request failed with status {response.status_code}: {response.text}")
                
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

    def submit_order(self, **kwargs):
        """
        Emir gönderir
        :String symbol: Sembol Kodu
        :String direction: İşlem Yönü: BUY / SELL (Aliş/Satiş)
        :String pricetype: Emir Tipi: piyasa/limit
        :String price: Emir tipi limit ise fiyat girilmelidir. (Örn. 1.98 şeklinde girilmelidir.)
        :String lot: Emir Adeti
        :Bool sms: Sms Gönderim
        :Bool email: Email Gönderim
        :String subAccount: Alt Hesap Numarasi "Boş gönderilebilir. Boş gönderilir ise Aktif Hesap Bilgilerini getirir."
        """
        try:
            # Required fields
            symbol = kwargs.get('symbol')
            direction = kwargs.get('direction')
            pricetype = kwargs.get('pricetype')
            price = kwargs.get('price')
            lot = kwargs.get('lot')
            
            # Optional fields with defaults
            sms = kwargs.get('sms', False)
            email = kwargs.get('email', False)
            subAccount = kwargs.get('subAccount', '')
            
            payload = {
                "symbol": symbol.upper() if symbol else '',
                "direction": direction,
                "pricetype": pricetype.lower() if pricetype else '',
                "price": str(price),
                "lot": str(lot),
                "sms": sms,
                "email": email,
                "subAccount": subAccount
            }
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
