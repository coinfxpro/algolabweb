import streamlit as st
from algolab import Algolab
from config import AlgolabConfig
import pandas as pd
import time
from datetime import datetime, timedelta
import json

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
if 'sms_time' not in st.session_state:
    st.session_state.sms_time = None
if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = None

def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except:
        return value

def wait_for_api():
    """API istekleri arasında en az 5 saniye bekle"""
    if st.session_state.last_api_call:
        elapsed = (datetime.now() - st.session_state.last_api_call).total_seconds()
        if elapsed < 5:
            time.sleep(5 - elapsed)
    st.session_state.last_api_call = datetime.now()

def handle_login():
    try:
        api_key = st.session_state.get('api_key', '')
        username = st.session_state.get('username', '')
        password = st.session_state.get('password', '')

        if not api_key or not username or not password:
            st.error("Lütfen tüm bilgileri girin")
            return

        # API key formatını kontrol et
        if not api_key.startswith("API-"):
            api_key = "API-" + api_key

        print("\n=== LOGIN ATTEMPT ===")
        print(f"API Key: {api_key}")
        print(f"Username: {username}")
        
        wait_for_api()
        algolab = Algolab(api_key, username, password)
        
        try:
            response = algolab.login()
            st.session_state.algolab = algolab
            st.session_state.sms_pending = True
            st.session_state.sms_time = datetime.now()
            st.success("Giriş başarılı! SMS kodu bekleniyor...")
            st.rerun()
        except Exception as e:
            error_msg = str(e)
            st.error(f"Giriş hatası: {error_msg}")
            st.session_state.logged_in = False
            st.session_state.sms_pending = False
            st.session_state.sms_time = None
            
    except Exception as e:
        st.error(f"Sistem hatası: {str(e)}")
        st.session_state.logged_in = False
        st.session_state.sms_pending = False
        st.session_state.sms_time = None

def handle_sms():
    try:
        wait_for_api()
        if st.session_state.algolab.login_control(st.session_state.sms_code):
            st.session_state.logged_in = True
            st.session_state.sms_pending = False
            st.session_state.sms_time = None
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
        # SMS kodunun geçerlilik süresini kontrol et (60 saniye)
        if st.session_state.sms_time:
            remaining_time = 60 - (datetime.now() - st.session_state.sms_time).seconds
            if remaining_time > 0:
                st.warning(f"SMS kodunun geçerlilik süresi: {remaining_time} saniye")
                
                with st.form("sms_form"):
                    st.text_input("SMS Kodu", type="password", key="sms_code")
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        submit = st.form_submit_button("Doğrula")
                    with col2:
                        if st.form_submit_button("Yeni Kod İste"):
                            handle_login()  # Yeni SMS kodu için login işlemini tekrarla
                
                if submit:
                    handle_sms()
            else:
                st.error("SMS kodunun süresi doldu. Lütfen yeni kod isteyin.")
                if st.button("Yeni Kod İste"):
                    handle_login()
        
        if st.button("Geri Dön"):
            st.session_state.sms_pending = False
            st.session_state.algolab = None
            st.session_state.sms_time = None
            st.rerun()

# Login olmuşsa ve SMS doğrulaması tamamlanmışsa ana ekranı göster
elif st.session_state.logged_in and not st.session_state.sms_pending:
    # Sağ üst köşeye yenile ve çıkış butonları
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.button("🔄 Yenile"):
            st.rerun()
    with col3:
        if st.button("🚪 Çıkış"):
            st.session_state.clear()
            st.rerun()
            
    # Tab'lar oluştur
    tab1, tab2, tab3 = st.tabs(["📊 Portföy", "📈 Manuel Emir", "🔗 TradingView Webhook"])
    
    # Portföy Tab'ı
    with tab1:
        try:
            with st.spinner("Portföy bilgileri alınıyor... (API kısıtlaması nedeniyle her istek arasında 5 saniye bekleme olacaktır)"):
                wait_for_api()
                positions = st.session_state.algolab.GetInstantPosition()
                if positions and positions.get('success'):
                    st.subheader("Portföy Bilgileri")
                    df_positions = pd.DataFrame(positions['content'])
                    st.dataframe(df_positions)
                    
                    if not df_positions.empty and 'Symbol' in df_positions.columns:
                        st.info("Her sembol için detay bilgisi alınıyor... (Her istek arasında 5 saniye bekleme olacaktır)")
                        for symbol in df_positions['Symbol'].unique():
                            wait_for_api()
                            equity_info = st.session_state.algolab.GetEquityInfo(symbol)
                            if equity_info and equity_info.get('success'):
                                st.write(f"{symbol} Detayları:")
                                st.json(equity_info['content'])
                else:
                    st.warning("Portföy bilgileri alınamadı.")
                
        except Exception as e:
            st.error(f"Veri alınamadı: {str(e)}")
    
    # Manuel Emir Tab'ı
    with tab2:
        st.subheader("Manuel Emir Girişi")
        
        with st.form("order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Sembol", placeholder="Örn: GARAN")
                quantity = st.number_input("Miktar", min_value=1, step=1)
                
            with col2:
                price = st.number_input("Fiyat", min_value=0.01, step=0.01)
                order_type = st.selectbox("Emir Tipi", ["limit", "piyasa"])
                side = st.selectbox("İşlem Yönü", ["ALIŞ", "SATIŞ"])
                
            # Alt hesap ve bildirim seçenekleri
            col3, col4 = st.columns(2)
            with col3:
                subaccount = st.text_input("Alt Hesap No (Opsiyonel)", value="")
            with col4:
                sms = st.checkbox("SMS Bildirim", value=False)
                email = st.checkbox("Email Bildirim", value=False)
            
            submit_order = st.form_submit_button("Emir Gönder")
            
            if submit_order:
                try:
                    if not symbol:
                        st.error("Lütfen sembol girin")
                        st.stop()
                        
                    wait_for_api()
                    # API'ye gönderilecek değerleri hazırla
                    side_map = {"ALIŞ": "BUY", "SATIŞ": "SELL"}
                    
                    order_data = {
                        "symbol": symbol.upper(),
                        "direction": side_map[side],
                        "pricetype": order_type,
                        "price": str(price),
                        "lot": str(quantity),
                        "sms": sms,
                        "email": email,
                        "subAccount": subaccount
                    }
                    
                    response = st.session_state.algolab.post(
                        endpoint=st.session_state.algolab.config.URL_SEND_ORDER,
                        payload=order_data
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            st.success(f"Emir başarıyla gönderildi! Emir No: {data.get('content', {}).get('orderId', 'N/A')}")
                        else:
                            st.error(f"Emir gönderilemedi: {data.get('message', 'Bilinmeyen hata')}")
                    else:
                        st.error(f"Emir gönderilemedi. HTTP Status: {response.status_code}")
                        st.error(f"Hata detayı: {response.text}")
                        
                except Exception as e:
                    st.error(f"Emir gönderme hatası: {str(e)}")
                    
    # TradingView Webhook Tab'ı
    with tab3:
        st.subheader("TradingView Webhook Ayarları")
        
        # Webhook URL'i göster
        webhook_url = f"{st.session_state.algolab.config.api_hostname}/webhook"
        st.code(webhook_url, language="text")
        
        # Örnek Pine Script
        st.subheader("Örnek Pine Script")
        example_script = '''
// TradingView Pine Script v5
strategy("AlgoLab Trading Bot", overlay=true)

// Örnek strateji sinyalleri
longCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))
shortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))

// Webhook alert mesajları
if (longCondition)
    alert("{\\"symbol\\": \\"{{ticker}}\\", \\"side\\": \\"BUY\\", \\"quantity\\": 1, \\"price\\": {{close}}, \\"orderType\\": \\"LIMIT\\"}", alert.freq_once_per_bar)

if (shortCondition)
    alert("{\\"symbol\\": \\"{{ticker}}\\", \\"side\\": \\"SELL\\", \\"quantity\\": 1, \\"price\\": {{close}}, \\"orderType\\": \\"LIMIT\\"}", alert.freq_once_per_bar)
'''
        st.code(example_script, language="pine")
        
        # Webhook kurulum talimatları
        st.subheader("Webhook Kurulumu")
        st.markdown("""
        1. TradingView'da bir alert oluşturun
        2. Alert koşulunu belirleyin
        3. "Webhook URL" alanına yukarıdaki URL'i yapıştırın
        4. "Message" alanına Pine Script'teki gibi JSON formatında mesaj yazın
        5. Alert'i kaydedin
        
        Not: Webhook mesajı aşağıdaki formatta olmalıdır:
        ```json
        {
            "symbol": "GARAN",
            "side": "BUY",
            "quantity": 1,
            "price": 20.50,
            "orderType": "LIMIT"
        }
        """
        )
        
    # Çıkış yap butonu
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.sms_pending = False
        st.session_state.algolab = None
        st.session_state.sms_time = None
        st.session_state.last_api_call = None
        st.rerun()
