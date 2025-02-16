import streamlit as st

class AlgolabConfig:
    def __init__(self):
        # API bilgileri
        self.api_key = None
        self.username = None
        self.password = None
        
        # URL yapılandırması - orijinal API ile aynı
        self.hostname = "www.algolab.com.tr"
        self.api_hostname = f"https://{self.hostname}"
        self.api_url = self.api_hostname + "/api"    # Yani: https://www.algolab.com.tr/api
        self.socket_url = f"wss://{self.hostname}/api/ws"

        # API endpoint'leri
        self.URL_LOGIN_USER = f"{self.api_url}/LoginUser"
        self.URL_LOGIN_CONTROL = f"{self.api_url}/LoginUserControl"
        self.URL_GET_INSTANT_POSITION = f"{self.api_url}/GetInstantPosition"
        self.URL_GET_EQUITY_INFO = f"{self.api_url}/GetEquityInfo"
        self.URL_SEND_ORDER = f"{self.api_url}/SendOrder"
        self.URL_MODIFY_ORDER = f"{self.api_url}/ModifyOrder"
        self.URL_DELETE_ORDER = f"{self.api_url}/DeleteOrder"
        self.URL_DELETE_ORDER_VIOP = f"{self.api_url}/DeleteOrderViop"
        self.URL_SESSION_REFRESH = f"{self.api_url}/SessionRefresh"
        self.URL_GET_CANDLE_DATA = f"{self.api_url}/GetCandleData"
        self.URL_GET_VIOP_CUSTOMER_OVERALL = f"{self.api_url}/ViopCustomerOverall"
        self.URL_GET_SUBACCOUNTS = f"{self.api_url}/GetSubAccounts"
        self.URL_GET_TODAYS_TRANSACTION = f"{self.api_url}/TodaysTransaction"
        self.URL_GET_VIOP_CUSTOMER_TRANSACTIONS = f"{self.api_url}/ViopCustomerTransactions"
        self.URL_GET_EQUITY_ORDER_HISTORY = f"{self.api_url}/GetEquityOrderHistory"
        self.URL_GET_VIOP_ORDER_HISTORY = f"{self.api_url}/GetViopOrderHistory"
        self.URL_GET_ACCOUNT_EXTRE = f"{self.api_url}/AccountExtre"
        self.URL_GET_CASH_FLOW = f"{self.api_url}/CashFlow"
        self.URL_RISK_SIMULATION = f"{self.api_url}/RiskSimulation"
        self.URL_VIOP_COLLATERAL_INFO = f"{self.api_url}/ViopCollateralInfo"

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
