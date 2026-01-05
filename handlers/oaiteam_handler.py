"""
Handler untuk Perintah Invite ChatGPT Team
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from database_mysql import Database
from utils.messages import get_insufficient_balance_message

# Import dari folder oaiteam (bukan config utama)
from oaiteam.invite import ChatGPTInviter, OAITEAM_COST

logger = logging.getLogger(__name__)

async def invite_gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /invite_gpt <email>"""
    user_id = update.effective_user.id

    # 1. Cek Blokir & Registrasi
    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun diblokir.")
        return
    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Ketik /start dulu.")
        return

    # 2. Cek Argumen
    if not context.args:
        await update.message.reply_text(
            "ℹ️ **Cara Invite ChatGPT Team**\n\n"
            "Format:\n`/invite_gpt <email_tujuan>`\n\n"
            "Contoh:\n`/invite_gpt budi@gmail.com`\n\n"
            f"💰 Biaya: {OAITEAM_COST} Poin",
            parse_mode='Markdown'
        )
        return

    target_email = context.args[0].strip()

    # 3. Cek Saldo
    user = db.get_user(user_id)
    if user["balance"] < OAITEAM_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"]),
            parse_mode='Markdown'
        )
        return

    # 4. Potong Saldo
    if not db.deduct_balance(user_id, OAITEAM_COST):
        await update.message.reply_text("❌ Gagal transaksi.")
        return

    msg = await update.message.reply_text(
        f"⏳ **Mengirim Undangan...**\n"
        f"📧 Email: `{target_email}`\n"
        f"💰 Biaya: {OAITEAM_COST} Poin",
        parse_mode='Markdown'
    )

    try:
        # Jalankan invite
        inviter = ChatGPTInviter()
        result = await asyncio.to_thread(inviter.invite, target_email)

        if result["success"]:
            # Simpan log
            db.add_verification(
                user_id, "openai_invite", "invite_gpt", 
                "success", f"Invited: {target_email}"
            )
            
            await msg.edit_text(
                f"✅ **Undangan Terkirim!**\n\n"
                f"📧 Ke: `{target_email}`\n"
                f"Silakan cek Inbox/Spam email tersebut.",
                parse_mode='Markdown'
            )
        else:
            # Refund jika gagal
            db.add_balance(user_id, OAITEAM_COST)
            await msg.edit_text(
                f"❌ **Gagal Mengirim Undangan**\n\n"
                f"Penyebab: {result.get('message')}\n"
                f"♻️ {OAITEAM_COST} Poin dikembalikan.",
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Invite Error: {e}")
        db.add_balance(user_id, OAITEAM_COST)
        await msg.edit_text(f"❌ Error Sistem: {e}")