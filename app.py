import streamlit as st
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from config import AlgolabConfig
from algolab import Algolab

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
    st.set_page_config(page_title="Algolab Trading Bot", page_icon="📈")
    
    st.title("Algolab Trading Bot")
    
    # Login işlemi
    if not st.session_state.logged_in and not st.session_state.waiting_for_sms:
        with st.form("login_form"):
            st.write("Algolab Giriş")
            api_key = st.text_input("API Key", type="password")
            username = st.text_input("TC Kimlik No / Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            
            if st.form_submit_button("Giriş Yap"):
                try:
                    config = AlgolabConfig()
                    config.api_key = api_key
                    config.username = username
                    config.password = password
                    
                    st.session_state.algolab = Algolab(config)
                    st.session_state.waiting_for_sms = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Giriş hatası: {str(e)}")
    
    # SMS doğrulama
    elif st.session_state.waiting_for_sms:
        with st.form("sms_form"):
            st.write("SMS Doğrulama")
            sms_code = st.text_input("SMS Kodu")
            
            if st.form_submit_button("Doğrula"):
                try:
                    if st.session_state.algolab.login_control(sms_code):
                        st.session_state.logged_in = True
                        st.session_state.waiting_for_sms = False
                        st.success("Başarıyla giriş yapıldı!")
                        st.rerun()
                except Exception as e:
                    st.error(f"SMS doğrulama hatası: {str(e)}")
    
    # Ana sayfa
    else:
        # Sidebar
        st.sidebar.header("İşlemler")
        if st.sidebar.button("Oturumu Kapat"):
            st.session_state.algolab = None
            st.session_state.logged_in = False
            st.session_state.waiting_for_sms = False
            st.rerun()
        
        # Ana sayfa
        st.header("Webhook Bilgileri")
        st.info("Webhook URL: http://your-domain/webhook")
        
        st.markdown("""
        ### TradingView Webhook Format:
        ```json
        {
            "symbol": "BTCUSDT",
            "side": "BUY",  // veya "SELL"
            "quantity": 1.0
        }
        ```
        """)
        
        # Pozisyonlar
        st.header("Mevcut Pozisyonlar")
        try:
            positions = st.session_state.algolab.get_positions()
            if positions["success"]:
                st.table(positions["content"])
            else:
                st.warning("Pozisyon bilgileri alınamadı")
        except Exception as e:
            st.error(f"Pozisyonlar alınırken hata oluştu: {str(e)}")

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # FastAPI sunucusunu ayrı bir thread'de başlat
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Streamlit uygulamasını başlat
    main()
