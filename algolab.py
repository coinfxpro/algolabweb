import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json

class Algolab:
    def __init__(self, config):
        self.config = config
        self.token = ""
        self.hash = ""
        self.session = requests.Session()
        
        # API Key formatını düzenle
        api_key = config.get_api_key()
        if api_key.startswith("API-"):
            self.api_key = api_key
            self.api_code = api_key[4:]  # "API-" kısmını çıkar
        else:
            self.api_key = f"API-{api_key}"
            self.api_code = api_key
            
        # Base64 padding kontrolü
        padding_length = len(self.api_code) % 4
        if padding_length:
            self.api_code += "=" * (4 - padding_length)
            
        self.headers = {"APIKEY": self.api_key}
        print(f"API Key: {self.api_key}, Code: {self.api_code}")  # Debug için

    def encrypt(self, text):
        """
        Orijinal API'nin şifreleme yöntemi
        """
        try:
            iv = b'\0' * 16
            key = base64.b64decode(self.api_code)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            bytes_text = text.encode()
            padded_bytes = pad(bytes_text, 16)
            encrypted = cipher.encrypt(padded_bytes)
            return base64.b64encode(encrypted).decode("utf-8")
        except Exception as e:
            print(f"Encryption error: {str(e)}")  # Debug için
            raise Exception(f"Encryption failed: {str(e)}")

    def make_checker(self, endpoint, payload):
        """
        API isteklerini hazırla ve gönder
        """
        url = self.config.api_url + endpoint
        headers = self.headers.copy()
        
        if self.hash:
            headers["Hash"] = self.hash
            
        response = self.session.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")
            
        return response.json()

    def login(self):
        """
        Kullanıcı girişi yap
        """
        try:
            username = self.encrypt(self.config.get_username())
            password = self.encrypt(self.config.get_password())
            payload = {"username": username, "password": password}
            
            response = self.make_checker(self.config.URL_LOGIN_USER, payload)
            if response.get("success"):
                self.token = response.get("result", {}).get("token", "")
                return True
            else:
                raise Exception(f"Login error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Login error: {str(e)}")

    def login_control(self, sms_code):
        """
        SMS doğrulaması yap
        """
        try:
            token = self.encrypt(self.token)
            sms = self.encrypt(sms_code)
            payload = {"token": token, "password": sms}
            
            response = self.make_checker(self.config.URL_LOGIN_CONTROL, payload)
            if response.get("success"):
                self.hash = response.get("result", {}).get("hash", "")
                return True
            else:
                raise Exception(f"SMS verification error: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"SMS verification error: {str(e)}")

    def get_equity_info(self):
        """
        Portföy bilgilerini getir
        """
        try:
            response = self.make_checker(self.config.URL_GET_EQUITY_INFO, {})
            if response.get("success"):
                return response.get("result", {})
            else:
                raise Exception(f"Error getting equity info: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Error getting equity info: {str(e)}")

    def get_instant_position(self):
        """
        Anlık pozisyon bilgilerini getir
        """
        try:
            response = self.make_checker(self.config.URL_GET_INSTANT_POSITION, {})
            if response.get("success"):
                return response.get("result", {})
            else:
                raise Exception(f"Error getting instant position: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Error getting instant position: {str(e)}")

    def get_todays_transaction(self):
        """
        Günlük işlemleri getir
        """
        try:
            response = self.make_checker(self.config.URL_GET_TODAYS_TRANSACTION, {})
            if response.get("success"):
                return response.get("result", {})
            else:
                raise Exception(f"Error getting today's transactions: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Error getting today's transactions: {str(e)}")

    def send_order(self, symbol, quantity, price, buy_sell, order_type="limit"):
        """
        Emir gönder
        """
        try:
            payload = {
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "buy_sell": buy_sell,
                "order_type": order_type
            }
            
            response = self.make_checker(self.config.URL_SEND_ORDER, payload)
            if response.get("success"):
                return response.get("result", {})
            else:
                raise Exception(f"Error sending order: {response.get('message', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Error sending order: {str(e)}")
