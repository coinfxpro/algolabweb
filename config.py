import streamlit as st

class AlgolabConfig:
    def __init__(self):
        # URL configuration
        self.hostname = "www.algolab.com.tr"
        self.api_hostname = f"https://{self.hostname}"
        self.api_url = self.api_hostname + "/api"
        
        # API Key
        self.api_key = "API-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        
        # API Endpoints
        self.URL_LOGIN = "/api/LoginUser"  # Algolab'ın beklediği endpoint
        self.URL_LOGIN_CONTROL = "/api/LoginUserControl"
        self.URL_SEND_ORDER = "/api/SendOrder"
        self.URL_SESSION_REFRESH = "/api/SessionRefresh"
        self.URL_GET_EQUITY_INFO = "/api/GetEquityInfo"
        self.URL_GET_SUBACCOUNTS = "/api/GetSubAccounts"
        self.URL_INSTANT_POSITION = "/api/InstantPosition"
        self.URL_TODAYS_TRANSACTION = "/api/TodaysTransaction"
        self.URL_VIOP_CUSTOMER_OVERALL = "/api/ViopCustomerOverall"
        self.URL_VIOP_CUSTOMER_TRANSACTIONS = "/api/ViopCustomerTransactions"
        self.URL_MODIFY_ORDER = "/api/ModifyOrder"
        self.URL_DELETE_ORDER = "/api/DeleteOrder"
        self.URL_DELETE_ORDER_VIOP = "/api/DeleteOrderViop"
        self.URL_GET_CANDLE_DATA = "/api/GetCandleData"
        self.URL_VIOP_COLLATERAL_INFO = "/api/ViopCollateralInfo"
        self.URL_RISK_SIMULATION = "/api/RiskSimulation"
        self.URL_GET_EQUITY_ORDER_HISTORY = "/api/GetEquityOrderHistory"
        self.URL_GET_VIOP_ORDER_HISTORY = "/api/GetViopOrderHistory"
        self.URL_CASH_FLOW = "/api/CashFlow"
        self.URL_ACCOUNT_EXTRE = "/api/AccountExtre"

        # Socket URL
        self.socket_url = f"wss://{self.hostname}/api/ws"

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
