import streamlit as st

class AlgolabConfig:
    def __init__(self):
        try:
            # Streamlit Cloud'da secrets.toml'dan oku
            self.api_key = st.secrets["algolab"]["api_key"]
            self.username = st.secrets["algolab"]["username"]
            self.password = st.secrets["algolab"]["password"]
            self.hostname = "www.algolab.com.tr"
            self.api_hostname = f"https://{self.hostname}"
            self.api_url = self.api_hostname + "/api"
            self.socket_url = f"wss://{self.hostname}/api/ws"
        except Exception as e:
            # Lokal geliştirme için
            self.api_key = "API-KEY" #API Key'inizi Buraya Giriniz
            self.username = "TC veya Denizbank Kullanici Adi" #TC veya Denizbank Kullanıcı Adınızı Buraya Giriniz
            self.password = "Şifre" #Denizbank İnternet Bankacılığı Şifrenizi Buraya Giriniz
            self.hostname = "www.algolab.com.tr"
            self.api_hostname = f"https://{self.hostname}"
            self.api_url = self.api_hostname + "/api"
            self.socket_url = f"wss://{self.hostname}/api/ws"

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

    def get_hostname(self):
        return self.hostname

# ORDER STATUS
ORDER_STATUS = {0: "Bekleyen",
1: "Teslim Edildi",
2: "Gerçekleşti",
3: "Kismi Gerçekleşti",
4: "İptal Edildi",
5: "Değiştirildi",
6: "Askiya Alindi",
7: "Süresi Doldu",
8: "Hata"}

# Tick to OHLCV converter için takip edilmesi istenen semboller, boş olarak verilirse tüm semboller veya marketler takip edilir.
TRACKED_SYMBOLS = []
TRACKED_MARKETS = []
BUFFER_SIZE = 50000  # Converter için kaç veri sayısı biriktirilip json dosyalarına aktarılmalı
#Sadece IMKBH için 5000 gecikme olmadan çalışmaktadır. Tüm semboller içinse 50000 gecikme olmadan çalışmaktadır.

# ENDPOINTS
URL_LOGIN_USER = "/api/LoginUser"
URL_LOGIN_CONTROL = "/api/LoginUserControl"
URL_GETEQUITYINFO = "/api/GetEquityInfo"
URL_GETSUBACCOUNTS = "/api/GetSubAccounts"
URL_INSTANTPOSITION = "/api/InstantPosition"
URL_TODAYTRANSACTION = "/api/TodaysTransaction"
URL_VIOPCUSTOMEROVERALL = "/api/ViopCustomerOverall"
URL_VIOPCUSTOMERTRANSACTIONS = "/api/ViopCustomerTransactions"
URL_SENDORDER = "/api/SendOrder"
URL_MODIFYORDER = "/api/ModifyOrder"
URL_DELETEORDER = "/api/DeleteOrder"
URL_DELETEORDERVIOP = "/api/DeleteOrderViop"
URL_SESSIONREFRESH = "/api/SessionRefresh"
URL_GETCANDLEDATA = "/api/GetCandleData"
URL_VIOPCOLLETERALINFO = "/api/ViopCollateralInfo"
URL_RISKSIMULATION = "/api/RiskSimulation"
URL_GETEQUITYORDERHISTORY = "/api/GetEquityOrderHistory" # 404 Hatası alıyor
URL_GETVIOPORDERHISTORY = "/api/GetViopOrderHistory" # 404 Hatası alıyor
URL_CASHFLOW = "/api/CashFlow"
URL_ACCOUNTEXTRE = "/api/AccountExtre"
