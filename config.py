import streamlit as st

class AlgolabConfig:
    def __init__(self):
        # API Endpoint'leri
        self.api_url = "https://api.algolab.com.tr"
        
        # API Key
        self.api_key = "API-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        
        # API Endpoint'leri
        self.URL_LOGIN = "/auth/login"
        self.URL_LOGIN_CONTROL = "/auth/login/control"
        self.URL_SEND_ORDER = "/order/send"
        self.URL_CANCEL_ORDER = "/order/cancel"
        self.URL_GET_ORDERS = "/order/list"
        self.URL_GET_POSITIONS = "/position/list"
        self.URL_GET_BALANCE = "/balance"
        self.URL_GET_INSTRUMENTS = "/instrument/list"
        self.URL_GET_QUOTES = "/quote/list"
        self.URL_GET_TRADES = "/trade/list"

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def get_api_key(self):
        return self.api_key

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_api_url(self):
        return self.api_url

    def get_endpoint(self, name):
        return getattr(self, name, None)

# ORDER STATUS
ORDER_STATUS = {
    0: "Bekleyen",
    1: "Gerçekleşen",
    2: "İptal",
    3: "Reddedilen",
    4: "Bekleyen"
}

# Tick to OHLCV converter için takip edilmesi istenen semboller, boş olarak verilirse tüm semboller veya marketler takip edilir.
TRACKED_SYMBOLS = []
TRACKED_MARKETS = []
BUFFER_SIZE = 50000  # Converter için kaç veri sayısı biriktirilip json dosyalarına aktarılmalı
#Sadece IMKBH için 5000 gecikme olmadan çalışmaktadır. Tüm semboller içinse 50000 gecikme olmadan çalışmaktadır.
