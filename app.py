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

        wait_for_api()
        algolab = Algolab(api_key, username, password)
        response = algolab.login()
        
        if response and response.get('success'):
            st.session_state.algolab = algolab
            st.session_state.sms_pending = True
            st.session_state.sms_time = datetime.now()  # SMS gönderilme zamanını kaydet
            st.success("Giriş başarılı! SMS kodu bekleniyor...")
            st.rerun()
        else:
            st.error(f"Giriş hatası: {response.get('message', 'Bilinmeyen hata')}")
            
    except Exception as e:
        st.error(f"Giriş hatası: {str(e)}")
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
                order_type = st.selectbox("Emir Tipi", ["LIMIT", "MARKET"])
                side = st.selectbox("İşlem Yönü", ["ALIŞ", "SATIŞ"])
            
            submit_order = st.form_submit_button("Emir Gönder")
            
            if submit_order:
                try:
                    if not symbol:
                        st.error("Lütfen sembol girin")
                        st.stop()  # return yerine st.stop() kullanıyoruz
                        
                    wait_for_api()
                    # API'ye gönderilecek değerleri hazırla
                    side_map = {"ALIŞ": "BUY", "SATIŞ": "SELL"}
                    order = st.session_state.algolab.submit_order(
                        symbol=symbol,
                        quantity=quantity,
                        price=price if order_type == "LIMIT" else None,
                        order_type=order_type,
                        side=side_map[side]
                    )
                    
                    if order and order.get('success'):
                        st.success(f"Emir başarıyla gönderildi! Emir No: {order.get('content', {}).get('orderId', 'N/A')}")
                    else:
                        st.error(f"Emir gönderilemedi: {order.get('message', 'Bilinmeyen hata')}")
                        
                except Exception as e:
                    st.error(f"Emir gönderme hatası: {str(e)}")
    
    # TradingView Webhook Tab'ı
    with tab3:
        st.subheader("TradingView Webhook Entegrasyonu")
        
        # Webhook URL'ini göster
        st.info("📌 **Webhook URL'i**")
        webhook_url = "http://your-domain.com/webhook"  # Gerçek URL'i buraya ekleyin
        st.code(webhook_url, language="text")
        
        # Alert/Sinyal JSON örneği
        st.info("📝 **Alert Mesaj Formatı (JSON)**")
        example_json = {
            "symbol": "GARAN",
            "side": "BUY",  # veya "SELL"
            "quantity": 100,
            "price": 20.50,  # MARKET emirlerde bu alan opsiyonel
            "order_type": "LIMIT",  # veya "MARKET"
            "key": "your-secret-key"  # Güvenlik için özel anahtar
        }
        st.code(json.dumps(example_json, indent=2), language="json")
        
        # Webhook kurulum adımları
        st.info("🔧 **Kurulum Adımları**")
        st.markdown("""
        1. TradingView'da bir alert oluşturun
        2. "Webhook URL" alanına yukarıdaki URL'i yapıştırın
        3. "Message" alanına yukarıdaki JSON formatında bir mesaj yazın
        4. Alert koşullarınızı belirleyin ve kaydedin
        
        **Not:** Webhook mesajlarının güvenliği için:
        - Özel anahtarınızı kimseyle paylaşmayın
        - Her zaman HTTPS kullanın
        - IP kısıtlaması uygulayın
        """)
        
        # Örnek TradingView Pine Script
        st.info("📊 **Örnek Pine Script**")
        pine_script = '''
// TradingView Pine Script v5
strategy("My Trading Bot", overlay=true)

// Örnek strateji sinyalleri
longCondition = crossover(sma(close, 14), sma(close, 28))
shortCondition = crossunder(sma(close, 14), sma(close, 28))

if (longCondition)
    strategy.entry("Long", strategy.long)
    alert("{'symbol': '{{ticker}}', 'side': 'BUY', 'quantity': 100, 'order_type': 'MARKET'}", alert.freq_once_per_bar)

if (shortCondition)
    strategy.entry("Short", strategy.short)
    alert("{'symbol': '{{ticker}}', 'side': 'SELL', 'quantity': 100, 'order_type': 'MARKET'}", alert.freq_once_per_bar)
        '''
        st.code(pine_script, language="pine")
    
    # Çıkış yap butonu
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.sms_pending = False
        st.session_state.algolab = None
        st.session_state.sms_time = None
        st.session_state.last_api_call = None
        st.rerun()
