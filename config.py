import streamlit as st

class AlgolabConfig:
    def __init__(self):
        self.api_key = None
        self.username = None
        self.password = None
        self.hostname = "www.algolab.com.tr"
        self.api_hostname = f"https://{self.hostname}"
        self.api_url = self.api_hostname + "/api"
        self.socket_url = f"wss://{self.hostname}/api/ws"

        # API Endpoints
        self.URL_LOGIN_USER = "/auth/login/user"
        self.URL_LOGIN_CONTROL = "/auth/login/control"
        self.URL_SESSION_REFRESH = "/auth/sessionrefresh"
        self.URL_SEND_ORDER = "/order/sendorder"
        self.URL_MODIFY_ORDER = "/order/modifyorder"
        self.URL_DELETE_ORDER = "/order/deleteorder"
        self.URL_DELETE_ORDER_VIOP = "/order/deleteorderviop"
        self.URL_GET_EQUITY_INFO = "/data/getequityinfo"
        self.URL_GET_CANDLE_DATA = "/data/getcandledata"
        self.URL_GET_INSTANT_POSITION = "/data/instantposition"
        self.URL_GET_VIOP_CUSTOMER_OVERALL = "/data/viopcustomeroverall"
        self.URL_GET_SUBACCOUNTS = "/data/subaccounts"
        self.URL_GET_TODAYS_TRANSACTION = "/data/todaystransaction"
        self.URL_GET_VIOP_CUSTOMER_TRANSACTIONS = "/data/viopcustomertransactions"
        self.URL_GET_EQUITY_ORDER_HISTORY = "/data/equityorderhistory"
        self.URL_GET_VIOP_ORDER_HISTORY = "/data/vioporderhistory"
        self.URL_GET_ACCOUNT_EXTRE = "/data/accountextre"
        self.URL_GET_CASH_FLOW = "/data/cashflow"
        self.URL_RISK_SIMULATION = "/data/risksimulation"
        self.URL_VIOP_COLLATERAL_INFO = "/data/viopcollateralinfo"

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
