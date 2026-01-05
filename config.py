"""
File Konfigurasi Utama Bot
Mengatur Token dan Harga Poin.
"""
import os
from dotenv import load_dotenv

# Memuat file .env
load_dotenv()

# --- 1. KONFIGURASI BOT TELEGRAM ---
# (Biarkan kosong, bot akan ambil otomatis dari .env)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# --- 2. KONFIGURASI HARGA (SERBA 1 POIN) ---
# Biaya Verifikasi (Spotify, YouTube, Gemini, dll)
VERIFY_COST = 1 

# --- 3. KONFIGURASI BONUS (REWARD) ---
# Bonus saat User Baru Daftar
REGISTER_REWARD = 1

# Bonus Absen Harian (/qd)
CHECKIN_REWARD = 1

# Bonus Mengundang Teman (/invite)
INVITE_REWARD = 2

# --- 4. INFO CHANNEL & BANTUAN ---
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "bahlilbotverify")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/bahlilbotverify")

# Link Bantuan
HELP_NOTION_URL = "https://t.me/bahlilbotverify"

# Folder Log
LOG_DIR = "logs"