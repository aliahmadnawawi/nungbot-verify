"""
Program Utama Bot Telegram (Versi Final)
Mengintegrasikan Semua Layanan: Gemini, ChatGPT, Spotify, YouTube, Bolt, Military, & OpenAI Team.
"""
import logging
from functools import partial

from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN
from database_mysql import Database
from utils.concurrency import start_load_monitoring, stop_load_monitoring

# Import Handlers (Pengendali Perintah)
from handlers.user_commands import (
    start_command,
    about_command,
    help_command,
    balance_command,
    checkin_command,
    invite_command,
    use_command,
)
from handlers.verify_commands import (
    verify_command,     # Gemini One
    verify2_command,    # ChatGPT K12
    verify3_command,    # Spotify Student
    verify4_command,    # Bolt.new
    verify5_command,    # YouTube Student (BARU)
    verify6_command,    # Military Veteran (BARU)
    getV4Code_command,  # Cek Kode Bolt
)
from handlers.oaiteam_handler import invite_gpt_command # Invite ChatGPT Team (BARU)

from handlers.admin_commands import (
    addbalance_command,
    block_command,
    white_command,
    blacklist_command,
    genkey_command,
    listkeys_command,
    broadcast_command,
)

# Konfigurasi Log (Pencatat Aktivitas)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """Penanganan Error Global (Kalau ada error, lapor di sini)"""
    logger.exception("⚠️ Terjadi error saat memproses update: %s", context.error)


async def post_init(application: Application) -> None:
    """Dijalankan otomatis saat bot baru menyala"""
    logger.info("🖥️ Menyalakan Monitor Beban Sistem (CPU/RAM Protection)...")
    await start_load_monitoring()


async def post_shutdown(application: Application) -> None:
    """Dijalankan otomatis saat bot dimatikan"""
    logger.info("🛑 Mematikan Monitor Sistem...")
    await stop_load_monitoring()


def main():
    """Fungsi Utama"""
    # 1. Inisialisasi Database
    db = Database()

    # 2. Membangun Aplikasi Bot
    # concurrent_updates(True) = Bot bisa melayani banyak orang sekaligus
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True) 
        .post_init(post_init)         # Hook saat start
        .post_shutdown(post_shutdown) # Hook saat stop
        .build()
    )

    # --- A. PERINTAH USER (UMUM) ---
    application.add_handler(CommandHandler("start", partial(start_command, db=db)))
    application.add_handler(CommandHandler("about", partial(about_command, db=db)))
    application.add_handler(CommandHandler("help", partial(help_command, db=db)))
    application.add_handler(CommandHandler("balance", partial(balance_command, db=db)))
    application.add_handler(CommandHandler("qd", partial(checkin_command, db=db))) 
    application.add_handler(CommandHandler("invite", partial(invite_command, db=db)))
    application.add_handler(CommandHandler("use", partial(use_command, db=db)))

    # --- B. PERINTAH VERIFIKASI (INTI) ---
    application.add_handler(CommandHandler("verify", partial(verify_command, db=db)))       # One/Gemini
    application.add_handler(CommandHandler("verify2", partial(verify2_command, db=db)))     # K12/ChatGPT
    application.add_handler(CommandHandler("verify3", partial(verify3_command, db=db)))     # Spotify
    application.add_handler(CommandHandler("verify4", partial(verify4_command, db=db)))     # Bolt.new
    application.add_handler(CommandHandler("verify5", partial(verify5_command, db=db)))     # YouTube (BARU)
    application.add_handler(CommandHandler("verify6", partial(verify6_command, db=db)))     # Military (BARU)
    
    # Perintah Bantu Verifikasi
    application.add_handler(CommandHandler("getV4Code", partial(getV4Code_command, db=db)))

    # --- C. PERINTAH OPENAI TEAM (BARU) ---
    application.add_handler(CommandHandler("invite_gpt", partial(invite_gpt_command, db=db)))

    # --- D. PERINTAH ADMIN (OWNER) ---
    application.add_handler(CommandHandler("addbalance", partial(addbalance_command, db=db)))
    application.add_handler(CommandHandler("block", partial(block_command, db=db)))
    application.add_handler(CommandHandler("white", partial(white_command, db=db)))
    application.add_handler(CommandHandler("blacklist", partial(blacklist_command, db=db)))
    application.add_handler(CommandHandler("genkey", partial(genkey_command, db=db)))
    application.add_handler(CommandHandler("listkeys", partial(listkeys_command, db=db)))
    application.add_handler(CommandHandler("broadcast", partial(broadcast_command, db=db)))

    # Penanganan Error
    application.add_error_handler(error_handler)

    logger.info("🚀 Bot Verifikasi SheerID SIAP MELUNCUR! (Mode: Concurrent)")
    
    # Jalankan Bot
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()