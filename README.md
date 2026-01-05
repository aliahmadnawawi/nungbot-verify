# SheerID Bot Telegram Otomatis - Bahasa Indonesia


![Stars](https://img.shields.io/github/stars/PastKing/tgbot-verify?style=social)
![Forks](https://img.shields.io/github/forks/PastKing/tgbot-verify?style=social)
![Issues](https://img.shields.io/github/issues/PastKing/tgbot-verify)
![License](https://img.shields.io/github/license/PastKing/tgbot-verify)


> 🤖 Bot Telegram untuk menyelesaikan sertifikasi SheerID Pelajar/Guru secara otomatis
> 
> Dikembangkan berdasarkan perbaikan dari kode lama milik GGBond [@auto_sheerid_bot](https://t.me/auto_sheerid_bot)

---

## 📋 Deskripsi Proyek

Ini adalah bot Telegram berbasis Python yang dapat menyelesaikan sertifikasi identitas SheerID untuk berbagai platform (pelajar/guru) secara otomatis.  
Bot ini akan secara otomatis membuat data identitas, menghasilkan dokumen sertifikasi, lalu mengirimkannya ke platform SheerID, sehingga proses verifikasi menjadi jauh lebih sederhana.

> ⚠️ **Peringatan Penting**：
> 
> - **Gemini One Pro**, **ChatGPT Teacher K12**, **Spotify Student**, **YouTube Premium Student**, dan layanan lain **wajib** memperbarui `programId` serta data verifikasi lain di file konfigurasi modul sebelum digunakan. Silakan baca bagian “Wajib Dibaca Sebelum Digunakan”.
> - Proyek ini juga menyediakan **dokumentasi dan alur implementasi sertifikasi militer ChatGPT**. Detail dapat dilihat di `military/README.md` dan dapat diintegrasikan sendiri oleh pengguna.

### 🎯 Layanan Sertifikasi yang Didukung

| Perintah | Layanan | Tipe | Status | Keterangan |
|--------|--------|------|--------|-----------|
| /verify | Gemini One Pro | Guru | ✅ Lengkap | Diskon edukasi Google AI Studio |
| /verify2 | ChatGPT Teacher K12 | Guru | ✅ Lengkap | Diskon edukasi OpenAI |
| /verify3 | Spotify Student | Pelajar | ✅ Lengkap | Paket pelajar Spotify |
| /verify4 | Bolt.new Teacher | Guru | ✅ Lengkap | Diskon edukasi Bolt.new (auto ambil code) |
| /verify5 | YouTube Premium Student | Pelajar | ⚠️ Setengah jadi | Diskon pelajar YouTube Premium |

> ⚠️ **Catatan Khusus YouTube**：
> 
> Fitur sertifikasi YouTube masih dalam status setengah jadi.  
> Sebelum digunakan, harap membaca dokumen `youtube/HELP.MD`.
> 
> **Perbedaan utama**：
> - Format URL YouTube berbeda dari layanan lain
> - Perlu mengambil `programId` dan `verificationId` secara manual dari Network browser
> - Lalu menyusunnya menjadi URL SheerID standar
> 
> **Langkah penggunaan**：
> 1. Buka halaman sertifikasi YouTube Premium Pelajar
> 2. Buka Developer Tools browser (F12) → Network
> 3. Mulai proses sertifikasi, cari request `https://services.sheerid.com/rest/v2/verification/`
> 4. Ambil `programId` dari request dan `verificationId` dari response
> 5. Susun URL: https://services.sheerid.com/verify/{programId}/?verificationId={verificationId}
> 6. Gunakan perintah `/verify5` dengan URL tersebut

> 💡 **Sertifikasi Militer ChatGPT**：
> 
> Proyek ini menyediakan dokumentasi alur sertifikasi militer ChatGPT melalui SheerID.  
> Sertifikasi militer berbeda dari pelajar/guru karena harus memanggil endpoint `collectMilitaryStatus` terlebih dahulu sebelum mengirim data pribadi.  
> Detail dapat dilihat di `military/README.md`.

### ✨ Fitur Utama

- 🚀 Otomatis penuh: generate data → buat dokumen → submit verifikasi
- 🎨 Generasi pintar: otomatis membuat kartu pelajar/guru (PNG)
- 💰 Sistem poin:签到, undangan, penukaran key
- 🔐 Aman & stabil: database MySQL + env config
- ⚡ Kontrol concurrency untuk stabilitas
- 👥 Sistem admin dan manajemen pengguna lengkap

---

## 🛠️ Teknologi

- Bahasa: Python 3.11+
- Framework Bot: python-telegram-bot 20+
- Database: MySQL 5.7+
- Browser Automation: Playwright
- HTTP Client: httpx
- Image Processing: Pillow, reportlab, xhtml2pdf
- Environment: python-dotenv

---

## 🚀 Memulai

### 1. Clone Repository

git clone https://github.com/PastKing/tgbot-verify.git  
cd tgbot-verify

### 2. Install Dependensi

pip install -r requirements.txt  
playwright install chromium

### 3. Konfigurasi Environment

Salin env.example menjadi .env dan isi konfigurasi:

BOT_TOKEN=your_bot_token_here  
CHANNEL_USERNAME=your_channel  
CHANNEL_URL=https://t.me/your_channel  
ADMIN_USER_ID=your_admin_id  

MYSQL_HOST=localhost  
MYSQL_PORT=3306  
MYSQL_USER=root  
MYSQL_PASSWORD=your_password  
MYSQL_DATABASE=tgbot_verify  

### 4. Jalankan Bot

python bot.py

---

## 🐳 Deployment Docker

### Docker Compose (Direkomendasikan)

cp env.example .env  
nano .env  
docker-compose up -d  
docker-compose logs -f  

### Docker Manual

docker build -t tgbot-verify .  

docker run -d \
  --name tgbot-verify \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tgbot-verify

---

## 📖 Panduan Penggunaan

### Perintah Pengguna

/start  
/about  
/balance  
/qd  
/invite  
/use <key>  
/verify <url>  
/verify2 <url>  
/verify3 <url>  
/verify4 <url>  
/verify5 <url>  
/getV4Code <id>  
/help  

### Perintah Admin

/addbalance <user_id> <poin>  
/block <user_id>  
/white <user_id>  
/blacklist  
/genkey <key> <poin> [jumlah] [hari]  
/listkeys  
/broadcast <pesan>  

### Alur Penggunaan

1. Buka halaman sertifikasi layanan
2. Salin URL lengkap (harus mengandung verificationId)
3. Kirim ke bot menggunakan perintah verify
4. Bot akan memproses otomatis
5. Hasil akan dikirim setelah selesai

---

## 📁 Struktur Proyek

(tetap sama, tidak diubah)

---

## ⚠️ Wajib Dibaca Sebelum Digunakan

programId pada SheerID bisa berubah sewaktu-waktu.  
Jika verifikasi gagal, kemungkinan besar programId sudah kadaluarsa.

Silakan update config berikut:
- one/config.py
- k12/config.py
- spotify/config.py
- youtube/config.py
- Boltnew/config.py

---

## 🤝 Pengembangan Lanjutan

- Wajib mencantumkan sumber asli
- Wajib open-source (MIT)
- Penggunaan komersial tanggung jawab sendiri

---

## 📜 Lisensi

MIT License  
Copyright (c) 2025 PastKing

---

## 🙏 Terima Kasih

- @auto_sheerid_bot (GGBond)
- Semua kontributor
- Platform SheerID

---

<p align="center">
  ⭐ Jika proyek ini membantu, silakan beri Star ⭐
</p>

<p align="center">
  Made with ❤️ by PastKing
</p>

