import streamlit as st
from algolab import Algolab
from config import AlgolabConfig
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(
    page_title="Algolab Trading",
    page_icon="📈",
    layout="wide"
)

# Session state başlatma
if 'algolab' not in st.session_state:
    st.session_state.algolab = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'waiting_for_sms' not in st.session_state:
    st.session_state.waiting_for_sms = False
if 'sms_pending' not in st.session_state:
    st.session_state.sms_pending = False

def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return value

def handle_login():
    try:
        api_key = st.session_state.get('api_key', '')
        username = st.session_state.get('username', '')
        password = st.session_state.get('password', '')

        if not api_key or not username or not password:
            st.error("Lütfen tüm bilgileri girin")
            return

        algolab = Algolab(api_key, username, password)
        response = algolab.login()
        
        if response and response.get('success'):
            st.session_state.algolab = algolab
            st.success("Giriş başarılı! SMS kodu bekleniyor...")
            st.session_state.logged_in = True
            st.session_state.sms_pending = True
            st.rerun()
        else:
            st.error(f"Giriş hatası: {response.get('message', 'Bilinmeyen hata')}")
            
    except Exception as e:
        st.error(f"Giriş hatası: {str(e)}")

def handle_sms():
    try:
        if st.session_state.algolab.login_control(st.session_state.sms_code):
            st.session_state.logged_in = True
            st.session_state.sms_pending = False
            st.success("Giriş başarılı!")
            st.rerun()
    except Exception as e:
        st.error(f"SMS doğrulama hatası: {str(e)}")

# Ana sayfa
st.title("Algolab Trading")

# Login olmamışsa login formu göster
if not st.session_state.logged_in:
    if not st.session_state.sms_pending:
        with st.form("login_form"):
            st.text_input("API Key", type="password", key="api_key")
            st.text_input("TC Kimlik No", key="username")
            st.text_input("Şifre", type="password", key="password")
            
            if st.form_submit_button("Giriş Yap"):
                handle_login()
    else:
        with st.form("sms_form"):
            st.text_input("SMS Kodu", type="password", key="sms_code")
            
            if st.form_submit_button("Doğrula"):
                handle_sms()
                
        if st.button("Geri Dön"):
            st.session_state.sms_pending = False
            st.session_state.algolab = None
            st.rerun()

# Login olmuşsa ana ekranı göster
else:
    # Portföy bilgilerini göster
    try:
        equity_info = st.session_state.algolab.get_equity_info()
        positions = st.session_state.algolab.get_instant_position()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Varlık", format_number(equity_info.get("totalAssets", 0)))
        with col2:
            st.metric("Kullanılabilir Bakiye", format_number(equity_info.get("availableBalance", 0)))
        with col3:
            st.metric("Kredi", format_number(equity_info.get("credit", 0)))
        with col4:
            st.metric("Risk Oranı", format_number(equity_info.get("riskRatio", 0)))
            
        # Pozisyonları tablo olarak göster
        if positions:
            st.subheader("Açık Pozisyonlar")
            df = pd.DataFrame(positions)
            st.dataframe(df)
            
        # Manuel emir girişi
        with st.form("order_form"):
            st.subheader("Manuel Emir Girişi")
            symbol = st.text_input("Sembol", key="order_symbol")
            quantity = st.number_input("Miktar", min_value=0, key="order_quantity")
            price = st.number_input("Fiyat", min_value=0.0, key="order_price")
            order_type = st.selectbox("Emir Tipi", ["limit", "market"], key="order_type")
            buy_sell = st.selectbox("İşlem Yönü", ["buy", "sell"], key="order_direction")
            
            if st.form_submit_button("Emir Gönder"):
                try:
                    order = st.session_state.algolab.send_order(
                        symbol=symbol,
                        quantity=quantity,
                        price=price,
                        buy_sell=buy_sell,
                        order_type=order_type
                    )
                    st.success("Emir başarıyla gönderildi!")
                except Exception as e:
                    st.error(f"Emir gönderme hatası: {str(e)}")
                    
        # Bekleyen emirleri göster
        try:
            transactions = st.session_state.algolab.get_todays_transaction()
            if transactions:
                st.subheader("Bekleyen Emirler")
                df = pd.DataFrame(transactions)
                st.dataframe(df)
        except Exception as e:
            st.error(f"İşlem geçmişi alınamadı: {str(e)}")
            
    except Exception as e:
        st.error(f"Veri alınamadı: {str(e)}")
        
    if st.button("Çıkış Yap"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
