import streamlit as st

class AlgolabConfig:
    def __init__(self):
        self.api_key = None
        self.username = None
        self.password = None
        self.hostname = "api.algolab.com.tr"  
        self.api_hostname = f"https://{self.hostname}"
        self.api_url = f"{self.api_hostname}/api/v1"  
        self.socket_url = f"wss://{self.hostname}/ws"

        # API Endpoints
        self.URL_LOGIN_USER = "/auth/login"  
        self.URL_LOGIN_CONTROL = "/auth/verify"
        self.URL_SESSION_REFRESH = "/auth/refresh"
        self.URL_SEND_ORDER = "/orders"
        self.URL_MODIFY_ORDER = "/orders/modify"
        self.URL_DELETE_ORDER = "/orders/cancel"
        self.URL_DELETE_ORDER_VIOP = "/orders/viop/cancel"
        self.URL_GET_EQUITY_INFO = "/market/equity"
        self.URL_GET_CANDLE_DATA = "/market/candles"
        self.URL_GET_INSTANT_POSITION = "/positions"
        self.URL_GET_VIOP_CUSTOMER_OVERALL = "/positions/viop"
        self.URL_GET_SUBACCOUNTS = "/accounts/sub"
        self.URL_GET_TODAYS_TRANSACTION = "/transactions/today"
        self.URL_GET_VIOP_CUSTOMER_TRANSACTIONS = "/transactions/viop"
        self.URL_GET_EQUITY_ORDER_HISTORY = "/orders/history/equity"
        self.URL_GET_VIOP_ORDER_HISTORY = "/orders/history/viop"
        self.URL_GET_ACCOUNT_EXTRE = "/accounts/statement"
        self.URL_GET_CASH_FLOW = "/accounts/cashflow"
        self.URL_RISK_SIMULATION = "/risk/simulate"
        self.URL_VIOP_COLLATERAL_INFO = "/positions/viop/collateral"

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

    def get_socket_url(self):
        return self.socket_url

    def get_endpoint(self, name):
        return getattr(self, name, None)

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
