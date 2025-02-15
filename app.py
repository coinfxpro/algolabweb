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

# Algolab bağlantısı
config = AlgolabConfig()
algolab = Algolab(config)

# Webhook endpoint'i
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        
        # TradingView'dan gelen sinyali işle
        symbol = data.get("symbol")
        side = data.get("side")  # "BUY" veya "SELL"
        quantity = float(data.get("quantity", 1.0))
        
        if side == "BUY":
            # Alış emri
            order = algolab.submit_order(
                symbol=symbol,
                side="BUY",
                quantity=quantity
            )
            return {"status": "success", "message": f"Buy order placed for {symbol}", "order": order}
        elif side == "SELL":
            # Satış emri
            order = algolab.submit_order(
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
    
    # Sidebar
    st.sidebar.header("Bağlantı Durumu")
    if st.sidebar.button("Bağlantıyı Test Et"):
        try:
            # Algolab bağlantı testi
            account_info = algolab.get_account()
            st.sidebar.success("Algolab'a başarıyla bağlandı!")
            st.sidebar.json(account_info)
        except Exception as e:
            st.sidebar.error(f"Bağlantı hatası: {str(e)}")
    
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
    
    # Son işlemler
    st.header("Son İşlemler")
    try:
        orders = algolab.get_orders()
        st.table(orders)
    except Exception as e:
        st.error(f"İşlemler alınamadı: {str(e)}")

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # FastAPI sunucusunu ayrı bir thread'de başlat
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Streamlit uygulamasını başlat
    main()
