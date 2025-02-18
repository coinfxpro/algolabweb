# AlgolabWeb API

AlgolabWeb, Algolab trading platformu için geliştirilmiş bir REST API'dir.

## Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git

## Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/coinfxpro/algolabweb.git
cd algolabweb
```

2. (Önerilen) Virtual environment oluşturun:
```bash
# Linux/Mac için
python3 -m venv venv
source venv/bin/activate

# Windows için
python -m venv venv
.\venv\Scripts\activate
```

3. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

## Çalıştırma

### Geliştirme Ortamı
```bash
python3 app.py
```

### Production Ortamı
```bash
# Gunicorn ile çalıştırma (önerilen)
pip install gunicorn
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Uygulama varsayılan olarak `http://localhost:8000` adresinde çalışacaktır.

## API Endpoints

- `POST /login`: Kullanıcı girişi
- `POST /verify-sms`: SMS doğrulama
- `GET /account-info`: Hesap bilgilerini alma
- `POST /submit-order`: Emir gönderme
- `POST /webhook`: TradingView webhook'u
- `POST /logout`: Çıkış yapma

## Sunucu Kurulumu

### Sistem Gereksinimleri
- Minimum 1 CPU
- En az 2GB RAM
- 20GB disk alanı
- Ubuntu 20.04 LTS veya üzeri (önerilen)

### Sistem Servisi Olarak Çalıştırma (Ubuntu/Debian)

1. Servis dosyası oluşturun:
```bash
sudo nano /etc/systemd/system/algolabweb.service
```

2. Aşağıdaki içeriği ekleyin:
```ini
[Unit]
Description=AlgolabWeb FastAPI Application
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/algolabweb
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

3. Servisi başlatın:
```bash
sudo systemctl start algolabweb
sudo systemctl enable algolabweb
```

### Güvenlik Önerileri
- UFW veya benzeri bir firewall kullanın
- Sadece gerekli portları açın (8000)
- Reverse proxy (nginx) kullanın
- SSL sertifikası ekleyin

## API Kullanımı

Örnek bir login isteği:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
