import streamlit as st
from algolab import Algolab
from config import AlgolabConfig
import pandas as pd
from datetime import datetime

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
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'password' not in st.session_state:
    st.session_state.password = ""

def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return value

def handle_login(api_key, username, password):
    try:
        # Form verilerini session state'e kaydet
        st.session_state.api_key = api_key
        st.session_state.username = username
        st.session_state.password = password
        
        config = AlgolabConfig()
        config.api_key = api_key
        config.username = username
        config.password = password
        
        algolab = Algolab(config)
        if algolab.login():
            st.session_state.algolab = algolab
            st.session_state.waiting_for_sms = True
            st.success("İlk aşama başarılı, SMS kodu bekleniyor...")
            st.rerun()
    except Exception as e:
        st.error(f"Giriş hatası: {str(e)}")

def handle_sms(sms_code):
    try:
        if st.session_state.algolab.login_control(sms_code):
            st.session_state.logged_in = True
            st.session_state.waiting_for_sms = False
            st.success("Giriş başarılı!")
            st.rerun()
    except Exception as e:
        st.error(f"SMS doğrulama hatası: {str(e)}")

# Ana sayfa
st.title("Algolab Trading")

# Login olmamışsa login formu göster
if not st.session_state.logged_in:
    if not st.session_state.waiting_for_sms:
        with st.form("login_form"):
            api_key = st.text_input("API Key", type="password", value=st.session_state.api_key)
            username = st.text_input("TC Kimlik No", value=st.session_state.username)
            password = st.text_input("Şifre", type="password", value=st.session_state.password)
            
            submitted = st.form_submit_button("Giriş Yap")
            if submitted:
                handle_login(api_key, username, password)
    else:
        with st.form("sms_form"):
            sms_code = st.text_input("SMS Kodu", type="password")
            
            submitted = st.form_submit_button("Doğrula")
            if submitted:
                handle_sms(sms_code)
                
        if st.button("Geri Dön"):
            st.session_state.waiting_for_sms = False
            st.session_state.algolab = None
            st.rerun()
else:
    # Ana dashboard
    # Üst bilgi çubuğu
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Yenile"):
            st.rerun()
    with col2:
        st.write("")  # Boş orta kolon
    with col3:
        if st.button("🚪 Çıkış"):
            st.session_state.clear()
            st.rerun()
    
    # Ana içerik
    tab1, tab2 = st.tabs(["📊 Portföy", "🎯 Emir İşlemleri"])
    
    # Portföy sekmesi
    with tab1:
        try:
            positions = st.session_state.algolab.get_positions()
            if positions and positions.get("success"):
                data = positions.get("content", {})
                
                # Hesap Özeti
                st.subheader("💰 Hesap Özeti")
                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("Toplam Varlık", format_number(data.get("toplamVarlik", 0)))
                with summary_cols[1]:
                    st.metric("Kullanılabilir Bakiye", format_number(data.get("kullanilabilirBakiye", 0)))
                with summary_cols[2]:
                    st.metric("Kredi", format_number(data.get("kredi", 0)))
                with summary_cols[3]:
                    st.metric("Risk Oranı", f"%{format_number(data.get('riskOrani', 0))}")
                
                # Pozisyonlar
                st.subheader("📈 Açık Pozisyonlar")
                if "pozisyonlar" in data:
                    positions_df = pd.DataFrame(data["pozisyonlar"])
                    if not positions_df.empty:
                        positions_df = positions_df.rename(columns={
                            'sembol': 'Sembol',
                            'maliyet': 'Maliyet',
                            'miktar': 'Miktar',
                            'guncelFiyat': 'Güncel Fiyat',
                            'karZarar': 'Kar/Zarar'
                        })
                        st.dataframe(positions_df, use_container_width=True)
                    else:
                        st.info("Açık pozisyon bulunmuyor.")
                else:
                    st.info("Pozisyon bilgisi bulunamadı.")
                
        except Exception as e:
            st.error(f"Portföy bilgisi alınamadı: {str(e)}")
    
    # Emir İşlemleri sekmesi
    with tab2:
        st.subheader("📝 Yeni Emir")
        
        # Emir formu
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Sembol", key="symbol", placeholder="Örn: GARAN")
            st.selectbox("İşlem Yönü", options=["BUY", "SELL"], key="side")
            st.number_input("Miktar", min_value=0.0, step=1.0, key="quantity")
        
        with col2:
            order_type = st.selectbox("Emir Tipi", options=["MARKET", "LIMIT"], key="order_type")
            if order_type == "LIMIT":
                st.number_input("Fiyat", min_value=0.0, step=0.01, key="price")
        
        # Emir gönderme butonu
        if st.button("💫 Emir Gönder", type="primary"):
            try:
                symbol = st.session_state.symbol.upper()
                side = st.session_state.side
                quantity = float(st.session_state.quantity)
                order_type = st.session_state.order_type
                
                price = None
                if order_type == "LIMIT":
                    price = float(st.session_state.price)
                
                result = st.session_state.algolab.submit_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                    order_type=order_type
                )
                
                if result and result.get("success"):
                    st.success(f"Emir başarıyla gönderildi! Mesaj: {result.get('message')}")
                else:
                    st.error(f"Emir gönderilemedi! Hata: {result.get('message') if result else 'Bilinmeyen hata'}")
                    
            except Exception as e:
                st.error(f"Emir gönderme hatası: {str(e)}")
        
        # Bekleyen Emirler
        st.subheader("⏳ Bekleyen Emirler")
        try:
            transactions = st.session_state.algolab.get_todays_transaction()
            if transactions and transactions.get("success"):
                orders = transactions.get("content", [])
                if orders:
                    orders_df = pd.DataFrame(orders)
                    st.dataframe(orders_df, use_container_width=True)
                else:
                    st.info("Bekleyen emir bulunmuyor.")
        except Exception as e:
            st.error(f"Bekleyen emirler alınamadı: {str(e)}")
