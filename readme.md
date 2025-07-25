# 🌱 GrowAGarden Discord Bot

Bot ini terhubung ke WebSocket dari [GrowAGarden](https://growagardenpro.com/) dan mengirim notifikasi ke Discord melalui **webhook** maupun **DM user**, apabila ada item spesial seperti **Gear**, **Eggs**, dan **Event Items** yang muncul.  
Notifikasi dikirim hanya saat terjadi perubahan atau setelah cooldown tertentu berakhir.

---

## 🚀 Fitur Utama

- 🎯 Deteksi Otomatis item spesial dari WebSocket GrowAGarden.
- 📩 Mengirim Webhook ke channel Discord dengan informasi lengkap.
- 📬 Kirim DM pribadi ke user jika item spesial terdeteksi.
- 🔔 Mention user tertentu saat item spesial muncul.
- ⏱️ Cooldown notifikasi:
  - **Eggs**: 20 menit
  - **Event Items**: 60 menit
- 🧹 Perintah untuk menghapus DM lama dari bot.

---

## 📦 Item Spesial yang Dideteksi

```python
ITEM_SPESIAL = {
    "gear": {"Master Sprinkler", "Godly Sprinkler", "Level Up Lollipop", "Medium Treat", "Medium Toy"},
    "eggs": {"Paradise Egg", "Bug Egg", "Bee Egg"},
    "event": {"Zen Egg", "Koi"}
}
```

## 📜 Cara Menjalankan
1. Install Dependensi
Pastikan kamu sudah menggunakan virtual environment, lalu jalankan:
```
pip install -r requirements.txt
```

## 2. Konfigurasi
Edit variabel di bagian atas gagapi.py:
```
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/...."
DISCORD_TOKEN = "TOKEN_DISCORD_MU"
TOKEN = "TOKEN_WS_KALAU_PERLU"
MENTION_USER_ID = [1234567890]        # ID User yang akan ditag saat item spesial muncul
TARGET_USER_ID = [1234567890, ...]    # ID User yang akan menerima DM
```

## 3. Jalankan Bot
Menjalankan services:
```
python gagapi.py
```

## 🧹 Perintah Slash (Optional)
| Perintah    | Fungsi                            |
| ----------- | --------------------------------- |
| `/hello`    | Menyapa pengguna                  |
| `/clear_dm` | Menghapus semua pesan DM dari bot |


## 🔄 Cooldown Notifikasi
| Tipe Item   | Waktu Reset |
| ----------- | ----------- |
| Eggs        | 20 menit    |
| Event Items | 60 menit    |
Setelah cooldown habis, item yang sama bisa dikirim ulang notifikasinya jika muncul kembali.


## 👨‍💻 Created by
By: Rafly Anggara Putra  
Referensi: GrowAGarden Pro  
Support Team: ChatGPT - OpenAI  
