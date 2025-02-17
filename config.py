import streamlit as st

class AlgolabConfig:
    def __init__(self):
        # URL configuration
        self.hostname = "www.algolab.com.tr"
        self.api_hostname = f"https://{self.hostname}"
        self.api_url = self.api_hostname + "/api"  # /api (küçük harfle)
        
        # API Key
        self.api_key = "API-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        
        # API Endpoints
        self.URL_LOGIN = "/LoginUser"  # /api önceden eklendi
        self.URL_LOGIN_CONTROL = "/LoginUserControl"
        self.URL_SESSION_REFRESH = "/SessionRefresh"
        self.URL_SEND_ORDER = "/SendOrder"
        self.URL_MODIFY_ORDER = "/ModifyOrder"
        self.URL_DELETE_ORDER = "/DeleteOrder"
        self.URL_DELETE_ORDER_VIOP = "/DeleteOrderViop"
        self.URL_GET_EQUITY_INFO = "/GetEquityInfo"
        self.URL_GET_CANDLE_DATA = "/GetCandleData"
        self.URL_GET_INSTANT_POSITION = "/InstantPosition"
        self.URL_GET_VIOP_CUSTOMER_OVERALL = "/ViopCustomerOverall"
        self.URL_GET_SUBACCOUNTS = "/GetSubAccounts"
        self.URL_GET_TODAYS_TRANSACTION = "/TodaysTransaction"
        self.URL_GET_VIOP_CUSTOMER_TRANSACTIONS = "/ViopCustomerTransactions"
        self.URL_GET_EQUITY_ORDER_HISTORY = "/GetEquityOrderHistory"
        self.URL_GET_VIOP_ORDER_HISTORY = "/GetViopOrderHistory"
        self.URL_GET_ACCOUNT_EXTRE = "/AccountExtre"
        self.URL_GET_CASH_FLOW = "/CashFlow"
        self.URL_RISK_SIMULATION = "/RiskSimulation"
        self.URL_VIOP_COLLATERAL_INFO = "/ViopCollateralInfo"

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
