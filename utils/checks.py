"""
Alat Pengecekan Izin & Validasi
Lokasi: utils/checks.py
"""
import logging
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """Cek apakah pesan dikirim dari Grup/Supergroup"""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """
    Menolak perintah sensitif (seperti cek saldo/topup) jika dilakukan di Grup.
    User akan diminta pindah ke Private Chat.
    """
    if is_group_chat(update):
        await update.message.reply_text(
            "🚫 **Akses Ditolak di Grup!**\n\n"
            "Menu ini bersifat pribadi (privasi saldo/akun).\n"
            "Silakan gunakan di **Chat Pribadi (PC)** dengan bot.\n\n"
            "✅ **Perintah yang BISA dipakai di Grup:**\n"
            "• `/verify` s/d `/verify6` (Semua Verifikasi)\n"
            "• `/invite_gpt` (Invite Team)\n"
            "• `/qd` (Absen Harian)\n"
            "• `/getV4Code` (Cek Kode Bolt)",
            parse_mode='Markdown'
        )
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Cek apakah user sudah Subscribe ke Channel Wajib.
    Mengembalikan True jika sudah join atau jika terjadi error (biar bot tidak macet).
    """
    # Jika config channel kosong, lewati pengecekan
    if not CHANNEL_USERNAME or CHANNEL_USERNAME == "YOUR_CHANNEL_HERE":
        return True

    try:
        # Pastikan format username pakai @
        target_channel = CHANNEL_USERNAME if CHANNEL_USERNAME.startswith("@") else f"@{CHANNEL_USERNAME}"
        
        member = await context.bot.get_chat_member(target_channel, user_id)
        
        # Status yang dianggap sudah join
        if member.status in ["member", "administrator", "creator"]:
            return True
        
        # Jika left atau kicked
        return False

    except TelegramError as e:
        # Jika bot bukan admin di channel atau channel tidak ditemukan,
        # kita anggap user lolos saja (fail-safe) agar bot tetap bisa dipakai.
        logger.warning(f"⚠️ Gagal cek membership channel ({CHANNEL_USERNAME}): {e}")
        return True