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
        
        # Orijinal header yapısı
        self.headers = {"APIKEY": self.api_key}
        
        print(f"Initialized with API Key: {self.api_key}")  # Debug için

    def encrypt(self, text):
        """
        Orijinal API'nin şifreleme yöntemi
        """
        try:
            print("\n=== ENCRYPTION DETAILS ===")
            print(f"Text to encrypt: {text}")
            print(f"API Code: {self.api_code}")
            
            iv = b'\0' * 16
            key = base64.b64decode(self.api_code.encode('utf-8'))
            cipher = AES.new(key, AES.MODE_CBC, iv)
            bytes_text = text.encode()
            padded_bytes = pad(bytes_text, 16)
            encrypted = cipher.encrypt(padded_bytes)
            result = base64.b64encode(encrypted).decode("utf-8")
            
            print(f"Encrypted result: {result}")
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
            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key
            }
            
            if login and self.token:
                headers['token'] = self.token
                
            url = self.config.api_url + endpoint  # API base URL ile endpoint'i birleştir
            
            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                verify=True
            )
            
            return response
            
        except Exception as e:
            print(f"POST request error: {str(e)}")
            raise

    def login(self):
        """
        API'ye login olma işlemi
        """
        try:
            u = self.encrypt(self.username)
            p = self.encrypt(self.password)
            payload = {"username": u, "password": p}
            
            response = self.post(self.config.URL_LOGIN_USER, payload=payload, login=False)
            
            if response.status_code == 200:
                data = response.json()
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
                data = response.json()
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

    def get_equity_info(self, symbol):
        try:
            payload = {'symbol': symbol}
            response = self.post(
                endpoint=self.config.URL_GET_EQUITY_INFO,
                payload=payload,
                login=True
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
                login=True
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get positions: {response.text}")
        except Exception as e:
            raise Exception(f"Get positions error: {str(e)}")

    def GetInstantPosition(self, sub_account=""):
        """
        Yatırım Hesabınıza bağlı alt hesapları (101, 102 v.b.) ve limitlerini görüntüleyebilirsiniz.
        """
        try:
            payload = {'Subaccount': sub_account}
            response = self.post(self.config.URL_GET_INSTANT_POSITION, payload=payload, login=True)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
                else:
                    raise Exception(f"GetInstantPosition failed: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"GetInstantPosition request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"GetInstantPosition error: {str(e)}")
            raise

    def GetEquityInfo(self, symbol):
        """
        Sembolle ilgili tavan taban yüksek düşük anlık fiyat gibi bilgileri çekebilirsiniz.
        """
        try:
            payload = {'symbol': symbol}
            response = self.post(self.config.URL_GET_EQUITY_INFO, payload=payload, login=True)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
                else:
                    raise Exception(f"GetEquityInfo failed: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"GetEquityInfo request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"GetEquityInfo error: {str(e)}")
            raise

    def submit_order(self, symbol, quantity, side, price=None, order_type="LIMIT"):
        """
        Emir gönderme işlemi
        Args:
            symbol (str): İşlem yapılacak sembol (örn: GARAN)
            quantity (int): İşlem miktarı
            side (str): İşlem yönü (BUY veya SELL)
            price (float, optional): Limit fiyat. MARKET emirlerde None olabilir
            order_type (str): Emir tipi (LIMIT veya MARKET)
        Returns:
            dict: API yanıtı
        """
        try:
            payload = {
                "symbol": symbol,
                "quantity": quantity,
                "side": side,
                "orderType": order_type
            }
            
            if order_type == "LIMIT" and price is not None:
                payload["price"] = price
                
            response = self.post(self.config.URL_SEND_ORDER, payload=payload, login=True)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data
                else:
                    raise Exception(f"Submit order failed: {data.get('message', 'Unknown error')}")
            else:
                raise Exception(f"Submit order request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Submit order error: {str(e)}")
            raise

    def session_refresh(self):
        try:
            response = self.post(
                endpoint=self.config.URL_SESSION_REFRESH,
                payload={},
                login=True
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
                login=True
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get today's transactions: {response.text}")
        except Exception as e:
            raise Exception(f"Get today's transactions error: {str(e)}")
