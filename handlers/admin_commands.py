"""Handler Perintah Admin"""
import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command

logger = logging.getLogger(__name__)


async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /addbalance - Menambah poin user manual"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "ℹ️ **Cara Penggunaan:**\n"
            "`/addbalance <User_ID> <Jumlah_Poin>`\n\n"
            "Contoh:\n`/addbalance 123456789 10`"
        , parse_mode='Markdown')
        return

    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("❌ User ID tidak ditemukan di database.")
            return

        if db.add_balance(target_user_id, amount):
            user = db.get_user(target_user_id)
            await update.message.reply_text(
                f"✅ **Berhasil Menambah Poin!**\n\n"
                f"Target: `{target_user_id}`\n"
                f"Jumlah: +{amount}\n"
                f"Saldo Sekarang: {user['balance']} Poin"
            , parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Gagal. Silakan coba lagi.")
    except ValueError:
        await update.message.reply_text("❌ Format salah. Harap masukkan angka.")


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /block - Memblokir user (Banned)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Cara Penggunaan:**\n"
            "`/block <User_ID>`\n\n"
            "Contoh:\n`/block 123456789`"
        , parse_mode='Markdown')
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("❌ User ID tidak ditemukan.")
            return

        if db.block_user(target_user_id):
            await update.message.reply_text(f"✅ User `{target_user_id}` berhasil **DIBLOKIR**.", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Gagal memblokir user.")
    except ValueError:
        await update.message.reply_text("❌ Format salah. Masukkan User ID yang valid.")


async def white_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /white - Membuka blokir user (Unbanned)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Cara Penggunaan:**\n"
            "`/white <User_ID>`\n\n"
            "Contoh:\n`/white 123456789`"
        , parse_mode='Markdown')
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("❌ User ID tidak ditemukan.")
            return

        if db.unblock_user(target_user_id):
            await update.message.reply_text(f"✅ User `{target_user_id}` berhasil **DILEPAS** dari blokir.", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Gagal membuka blokir.")
    except ValueError:
        await update.message.reply_text("❌ Format salah. Masukkan User ID yang valid.")


async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /blacklist - Melihat daftar user yang diblokir"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    blacklist = db.get_blacklist()

    if not blacklist:
        await update.message.reply_text("✅ Daftar Hitam kosong (Tidak ada user yang diblokir).")
        return

    msg = "📋 **DAFTAR HITAM (BLACKLIST):**\n\n"
    for user in blacklist:
        msg += f"🆔 ID: `{user['user_id']}`\n"
        msg += f"👤 User: @{user['username']}\n"
        msg += f"📝 Nama: {user['full_name']}\n"
        msg += "---\n"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /genkey - Membuat Kode Voucher (Card Key)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "ℹ️ **Cara Membuat Voucher:**\n"
            "`/genkey <Kode> <Poin> [Max_Pakai] [Expired_Hari]`\n\n"
            "**Contoh:**\n"
            "1️⃣ `/genkey BONUS20 20`\n"
            "(Kode BONUS20 isi 20 Poin, cuma bisa dipake 1 orang, aktif selamanya)\n\n"
            "2️⃣ `/genkey VIP50 50 10`\n"
            "(Kode VIP50 isi 50 Poin, bisa dipake oleh 10 orang)\n\n"
            "3️⃣ `/genkey FLASH100 100 1 7`\n"
            "(Kode FLASH100 isi 100 Poin, 1 orang, hangus dalam 7 hari)"
        , parse_mode='Markdown')
        return

    try:
        key_code = context.args[0].strip()
        balance = int(context.args[1])
        max_uses = int(context.args[2]) if len(context.args) > 2 else 1
        expire_days = int(context.args[3]) if len(context.args) > 3 else None

        if balance <= 0:
            await update.message.reply_text("❌ Poin harus lebih dari 0.")
            return

        if max_uses <= 0:
            await update.message.reply_text("❌ Jumlah penggunaan harus lebih dari 0.")
            return

        if db.create_card_key(key_code, balance, user_id, max_uses, expire_days):
            msg = (
                "✅ **Voucher Berhasil Dibuat!**\n\n"
                f"🎟️ Kode: `{key_code}`\n"
                f"💰 Isi Poin: {balance}\n"
                f"👥 Kuota: {max_uses} orang\n"
            )
            if expire_days:
                msg += f"⏳ Expired: {expire_days} hari lagi\n"
            else:
                msg += "⏳ Expired: Selamanya (Permanen)\n"
            
            msg += f"\n💡 **Cara Pakai (Member):**\n`/use {key_code}`"
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Gagal. Kode mungkin sudah ada, coba nama lain.")
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan Poin/Kuota adalah angka.")


async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /listkeys - Melihat daftar Voucher aktif"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    keys = db.get_all_card_keys()

    if not keys:
        await update.message.reply_text("📂 Belum ada voucher yang dibuat.")
        return

    msg = "📋 **DAFTAR VOUCHER:**\n\n"
    for key in keys[:20]:  # Batasi tampilan 20 voucher agar chat tidak kepanjangan
        msg += f"🎟️ Kode: `{key['key_code']}`\n"
        msg += f"💰 Poin: {key['balance']}\n"
        msg += f"👥 Terpakai: {key['current_uses']} / {key['max_uses']}\n"

        if key["expire_at"]:
            expire_time = datetime.fromisoformat(key["expire_at"])
            if datetime.now() > expire_time:
                msg += "🔴 Status: **EXPIRED**\n"
            else:
                days_left = (expire_time - datetime.now()).days
                msg += f"🟢 Status: Aktif ({days_left} hari lagi)\n"
        else:
            msg += "🟢 Status: Permanen\n"

        msg += "---\n"

    if len(keys) > 20:
        msg += f"\n*(Hanya menampilkan 20 voucher terbaru dari total {len(keys)})*"

    await update.message.reply_text(msg, parse_mode='Markdown')


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle /broadcast - Kirim pesan massal ke semua member"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin Admin.")
        return

    # Ambil teks dari argumen perintah atau dari reply pesan
    text = " ".join(context.args).strip() if context.args else ""
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""

    if not text:
        await update.message.reply_text(
            "ℹ️ **Cara Broadcast:**\n"
            "1. `/broadcast Halo semua, bot sedang maintenance`\n"
            "2. Atau Reply sebuah pesan lalu ketik `/broadcast`"
        , parse_mode='Markdown')
        return

    user_ids = db.get_all_user_ids()
    if not user_ids:
        await update.message.reply_text("❌ Belum ada user di database.")
        return

    success, failed = 0, 0
    status_msg = await update.message.reply_text(f"📢 **Memulai Broadcast...**\nTarget: {len(user_ids)} User", parse_mode='Markdown')

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
            await asyncio.sleep(0.05)  # Delay dikit biar gak kena limit Telegram
        except Exception as e:
            logger.warning("Gagal kirim ke %s: %s", uid, e)
            failed += 1

    await status_msg.edit_text(
        f"✅ **Broadcast Selesai!**\n\n"
        f"📨 Terkirim: {success}\n"
        f"❌ Gagal: {failed}"
    , parse_mode='Markdown')