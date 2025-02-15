import streamlit as st
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from config import AlgolabConfig
from algolab import Algolab
import pandas as pd
from datetime import datetime

# FastAPI uygulaması
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Streamlit state yönetimi
if 'algolab' not in st.session_state:
    st.session_state.algolab = None
    st.session_state.logged_in = False
    st.session_state.waiting_for_sms = False
    st.session_state.login_error = None

# Webhook endpoint'i
@app.post("/webhook")
async def webhook(request: Request):
    try:
        if not st.session_state.logged_in:
            raise HTTPException(status_code=401, detail="Not logged in")
            
        data = await request.json()
        
        # TradingView'dan gelen sinyali işle
        symbol = data.get("symbol")
        side = data.get("side")  # "BUY" veya "SELL"
        quantity = float(data.get("quantity", 1.0))
        
        if side == "BUY":
            # Alış emri
            order = st.session_state.algolab.submit_order(
                symbol=symbol,
                side="BUY",
                quantity=quantity
            )
            return {"status": "success", "message": f"Buy order placed for {symbol}", "order": order}
        elif side == "SELL":
            # Satış emri
            order = st.session_state.algolab.submit_order(
                symbol=symbol,
                side="SELL",
                quantity=quantity
            )
            return {"status": "success", "message": f"Sell order placed for {symbol}", "order": order}
        else:
            raise HTTPException(status_code=400, detail="Invalid side parameter")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Streamlit arayüzü
def main():
    st.set_page_config(
        page_title="Algolab Trading Bot",
        page_icon="📈",
        layout="wide"
    )

    # Login fonksiyonu
    def login():
        try:
            config = AlgolabConfig()
            api_key = st.text_input("API Key", type="password")
            username = st.text_input("TC Kimlik No / Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            config.api_key = api_key
            config.username = username
            config.password = password
            algolab = Algolab(config)
            if algolab.login():
                st.session_state.algolab = algolab
                st.session_state.waiting_for_sms = True
                st.session_state.login_error = None
                st.success("İlk aşama başarılı, SMS kodu bekleniyor...")
        except Exception as e:
            st.error(f"Giriş hatası: {str(e)}")

    # SMS doğrulama fonksiyonu
    def verify_sms():
        try:
            sms_code = st.text_input("SMS Kodu", type="password")
            if st.session_state.algolab.login_control(sms_code):
                st.session_state.logged_in = True
                st.session_state.waiting_for_sms = False
                st.session_state.login_error = None
                st.success("Giriş başarılı!")
                st.rerun()
        except Exception as e:
            st.error(f"SMS doğrulama hatası: {str(e)}")

    # Emir gönderme fonksiyonu
    def send_order():
        try:
            symbol = st.text_input("Sembol", placeholder="Örn: GARAN").upper()
            side = st.selectbox("İşlem Yönü", options=["BUY", "SELL"])
            quantity = float(st.number_input("Miktar", min_value=0.0, step=1.0))
            order_type = st.selectbox("Emir Tipi", options=["MARKET", "LIMIT"])
            price = None
            if order_type == "LIMIT":
                price = float(st.number_input("Fiyat", min_value=0.0, step=0.01))
            
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

    # Ana sayfa
    st.title("Algolab Trading Bot")

    # Login olmamışsa login formu göster
    if not st.session_state.logged_in:
        if not st.session_state.get('waiting_for_sms'):
            st.button("Giriş Yap", on_click=login)
        else:
            verify_sms()
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
                send_order()
            
            # Bekleyen Emirler
            st.subheader("⏳ Bekleyen Emirler")
            try:
                transactions = st.session_state.algolab.get_todays_transaction()  # Metod ismini güncelledik
                if transactions and transactions.get("success"):
                    orders = transactions.get("content", [])
                    if orders:
                        orders_df = pd.DataFrame(orders)
                        st.dataframe(orders_df, use_container_width=True)
                    else:
                        st.info("Bekleyen emir bulunmuyor.")
            except Exception as e:
                st.error(f"Bekleyen emirler alınamadı: {str(e)}")

def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return value

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # FastAPI sunucusunu ayrı bir thread'de başlat
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Streamlit arayüzünü başlat
    main()
