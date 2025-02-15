import streamlit as st

class AlgolabConfig:
    def __init__(self):
        # Credentials
        self.api_key = ""
        self.username = ""
        self.password = ""
        
        # API URLs
        self.hostname = "www.algolab.com.tr"
        self.api_hostname = self.hostname
        self.api_url = f"https://{self.hostname}"  
        self.socket_url = f"wss://{self.hostname}/ws"  

        # API Endpoints
        self.URL_LOGIN_USER = "/api/LoginUser"  
        self.URL_LOGIN_CONTROL = "/api/LoginUserControl"
        self.URL_GET_EQUITY_INFO = "/api/GetEquityInfo"
        self.URL_GET_INSTANT_POSITION = "/api/GetInstantPosition"
        self.URL_SEND_ORDER = "/api/SendOrder"
        self.URL_SESSION_REFRESH = "/api/SessionRefresh"
        self.URL_GET_TODAYS_TRANSACTION = "/api/GetTodaysTransaction"

    def get_api_key(self):
        return self.api_key
        
    def get_username(self):
        return self.username
        
    def get_password(self):
        return self.password
        
    def get_api_url(self):
        return self.api_url

# ORDER STATUS
ORDER_STATUS = {
    0: "Bekleyen",
    1: "Teslim Edildi",
    2: "Gerçekleşti",
    3: "İptal Edildi",
    4: "Reddedildi",
    5: "Beklemede",
    6: "İptal Edildi",
    7: "Kısmi İptal",
    8: "Kısmi Gerçekleşti",
    9: "Kısmi Gerçekleşti ve İptal Edildi",
    10: "Kısmi Gerçekleşti ve Kısmi İptal Edildi",
    11: "Kısmi Gerçekleşti ve Beklemede",
    12: "Kısmi Gerçekleşti ve Teslim Edildi",
    13: "Kısmi Gerçekleşti ve Reddedildi",
    14: "Kısmi Gerçekleşti ve İptal Edildi",
    15: "Kısmi Gerçekleşti ve Kısmi İptal Edildi",
    16: "Kısmi Gerçekleşti ve Kısmi İptal Edildi ve Beklemede",
    17: "Kısmi Gerçekleşti ve Kısmi İptal Edildi ve Teslim Edildi",
    18: "Kısmi Gerçekleşti ve Kısmi İptal Edildi ve Reddedildi"
}

# Tick to OHLCV converter için takip edilmesi istenen semboller, boş olarak verilirse tüm semboller veya marketler takip edilir.
TRACKED_SYMBOLS = []
TRACKED_MARKETS = []
BUFFER_SIZE = 50000  # Converter için kaç veri sayısı biriktirilip json dosyalarına aktarılmalı
#Sadece IMKBH için 5000 gecikme olmadan çalışmaktadır. Tüm semboller içinse 50000 gecikme olmadan çalışmaktadır.
