"""Handler Perintah User (Umum)"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command
from utils.messages import (
    get_welcome_message,
    get_about_message,
    get_help_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /start"""
    if await reject_group_command(update):
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    # Jika sudah terdaftar, langsung sapa balik
    if db.user_exists(user_id):
        await update.message.reply_text(
            f"👋 Selamat datang kembali, {full_name}!\n\n"
            "Anda sudah terdaftar di sistem.\n"
            "Ketik /help untuk melihat menu perintah."
        )
        return

    # Cek apakah diundang orang lain (Refferal)
    invited_by: Optional[int] = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            # Pastikan pengundang ada di database
            if not db.user_exists(invited_by):
                invited_by = None
        except Exception:
            invited_by = None

    # Buat User Baru di Database
    if db.create_user(user_id, username, full_name, invited_by):
        welcome_msg = get_welcome_message(full_name, bool(invited_by))
        await update.message.reply_text(welcome_msg)
    else:
        await update.message.reply_text("❌ Gagal mendaftar. Silakan coba lagi nanti.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /about"""
    if await reject_group_command(update):
        return

    await update.message.reply_text(get_about_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /help"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    await update.message.reply_text(get_help_message(is_admin))


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /balance (Cek Saldo)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    await update.message.reply_text(
        f"💰 **Informasi Saldo**\n\n"
        f"Poin Anda: **{user['balance']}** Poin"
    , parse_mode='Markdown')


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /qd (Absen Harian)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    # Cek Level 1: Cek sederhana via Python
    if not db.can_checkin(user_id):
        await update.message.reply_text("❌ Anda sudah absen hari ini. Besok lagi ya!")
        return

    # Cek Level 2: Eksekusi via Database (Atomic Transaction untuk cegah bug double absen)
    if db.checkin(user_id):
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ **Absen Berhasil!**\n\n"
            f"Bonus: +1 Poin\n"
            f"Total Saldo: {user['balance']} Poin"
        , parse_mode='Markdown')
    else:
        # Jika database menolak (berarti sudah absen)
        await update.message.reply_text("❌ Anda sudah absen hari ini. Besok lagi ya!")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /invite (Undang Teman)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"🎁 **Link Undangan Anda:**\n"
        f"`{invite_link}`\n\n"
        f"Setiap mengundang 1 teman baru, Anda akan mendapatkan **2 Poin**."
    , parse_mode='Markdown')


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /use (Redeem Voucher/Card Key)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Cara Penggunaan:**\n"
            "`/use <kode_voucher>`\n\n"
            "Contoh:\n`/use BONUS100`"
        , parse_mode='Markdown')
        return

    key_code = context.args[0].strip()
    result = db.use_card_key(key_code, user_id)

    if result is None:
        await update.message.reply_text("❌ Kode Voucher tidak valid.")
    elif result == -1:
        await update.message.reply_text("❌ Kode Voucher sudah habis (Limit Reached).")
    elif result == -2:
        await update.message.reply_text("❌ Kode Voucher sudah kadaluarsa.")
    elif result == -3:
        await update.message.reply_text("❌ Anda sudah pernah menggunakan kode ini.")
    else:
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"🎉 **Voucher Berhasil!**\n\n"
            f"Ditambahkan: +{result} Poin\n"
            f"Saldo Sekarang: {user['balance']} Poin"
        , parse_mode='Markdown')