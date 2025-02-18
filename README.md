# Algolab Trading Bot

Bu proje, Algolab API'sini kullanarak TradingView sinyallerini otomatik olarak alım-satım emirlerine dönüştüren bir webhook servisi ve kullanıcı arayüzü sunar.

## Özellikler

- Streamlit tabanlı kullanıcı dostu dashboard
- TradingView webhook entegrasyonu
- Algolab API entegrasyonu
- Gerçek zamanlı alım-satım emirleri
- İşlem geçmişi görüntüleme

## Kurulum

1. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

2. config.py dosyasında Algolab API bilgilerinizi ayarlayın.

3. Uygulamayı başlatın:
```bash
streamlit run app.py
```

## Webhook Kullanımı

TradingView'dan webhook gönderirken şu formatı kullanın:

```json
{
    "symbol": "BTCUSDT",
    "side": "BUY",  // veya "SELL"
    "quantity": 1.0
}
```

## Lisans

MIT
