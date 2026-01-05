"""Handler Perintah Verifikasi"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
# Import Modul Verifikasi dari folder masing-masing
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
# 🔥 IMPORT BARU UNTUK MILITARY
from military.sheerid_verifier import SheerIDVerifier as MilitaryVerifier

from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# Mencoba import kontrol konkurensi (antrian), jika gagal pakai dummy
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    # Jika import gagal, buat implementasi sederhana agar tidak error
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir. Tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid. Periksa kembali link Anda.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin. Silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"⏳ **Memproses Verifikasi Gemini One Pro...**\n"
        f"🆔 ID: `{verification_id}`\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "Mohon tunggu, proses memakan waktu 1-2 menit..."
    , parse_mode='Markdown')

    try:
        verifier = OneVerifier(verification_id)
        # Menjalankan verifikasi di thread terpisah agar bot tidak macet
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ **Verifikasi Sukses!**\n\n"
            if result.get("pending"):
                result_msg += "📝 Dokumen terkirim, menunggu review manual.\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 **Link Sukses:**\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            # Refund poin jika gagal
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ **Verifikasi Gagal:** {result.get('message', 'Error tidak diketahui')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            , parse_mode='Markdown')
    except Exception as e:
        logger.error("Error Verifikasi Gemini: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify2 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin.")
        return

    processing_msg = await update.message.reply_text(
        f"⏳ **Memproses Verifikasi ChatGPT Teacher K12...**\n"
        f"🆔 ID: `{verification_id}`\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "Mohon tunggu sebentar..."
    , parse_mode='Markdown')

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ **Verifikasi Sukses!**\n\n"
            if result.get("pending"):
                result_msg += "📝 Dokumen terkirim, menunggu review manual.\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 **Link Sukses:**\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ **Verifikasi Gagal:** {result.get('message', 'Error tidak diketahui')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            , parse_mode='Markdown')
    except Exception as e:
        logger.error("Error Verifikasi K12: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify3 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 **Memproses Verifikasi Spotify Student...**\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "📝 Membuat data mahasiswa...\n"
        "🎨 Membuat kartu mahasiswa...\n"
        "📤 Mengirim dokumen..."
    , parse_mode='Markdown')

    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ **Spotify Student Sukses!**\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen terkirim, menunggu review SheerID\n"
                result_msg += "⏱️ Estimasi waktu: Beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 **Link Sukses:**\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ **Verifikasi Gagal:** {result.get('message', 'Error tidak diketahui')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            , parse_mode='Markdown')
    except Exception as e:
        logger.error("Error Verifikasi Spotify: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify4 - Bolt.new Teacher (Auto Code)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 **Memproses Verifikasi Bolt.new Teacher...**\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "📤 Sedang mengirim dokumen..."
    , parse_mode='Markdown')

    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # Tahap 1: Submit Dokumen
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Gagal mengirim dokumen: {result.get('message', 'Unknown Error')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Gagal mendapatkan Verification ID.\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            )
            return
        
        # Update Status
        await processing_msg.edit_text(
            f"✅ **Dokumen Terkirim!**\n"
            f"📋 ID: `{vid}`\n\n"
            f"🔍 Sedang mengambil Kode Voucher secara otomatis...\n"
            f"(Maksimal menunggu 20 detik)"
        , parse_mode='Markdown')
        
        # Tahap 2: Auto Get Code (Maks 20 detik)
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)
        
        if code:
            result_msg = (
                f"🎉 **Verifikasi Sukses!**\n\n"
                f"✅ Dokumen Terkirim\n"
                f"✅ Lolos Review\n"
                f"✅ Kode Diterima\n\n"
                f"🎁 **Kode Voucher:** `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Link: {result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
            
            # Simpan log sukses
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            # Jika timeout 20 detik, suruh user cek manual
            await processing_msg.edit_text(
                f"✅ **Dokumen Berhasil Dikirim!**\n\n"
                f"⏳ Kode Voucher belum keluar (Review butuh 1-5 menit).\n\n"
                f"📋 ID: `{vid}`\n\n"
                f"💡 Silakan cek manual nanti dengan perintah:\n"
                f"`/getV4Code {vid}`\n\n"
                f"⚠️ *Catatan: Poin sudah terpakai, cek manual GRATIS.*"
            , parse_mode='Markdown')
            
            # Simpan log pending
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid
            )
            
    except Exception as e:
        logger.error("Error Verifikasi Bolt: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    """Helper: Auto ambil kode (Polling ringan)"""
    import time
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            
            if elapsed >= max_wait:
                logger.info(f"Auto-code timeout ({elapsed}s). User must check manually.")
                return None
            
            try:
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    
                    if current_step == "success":
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Auto-code success: {code}")
                            return code
                    elif current_step == "error":
                        logger.warning(f"Verification rejected: {data.get('errorIds', [])}")
                        return None
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Auto-code error: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify5 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 **Memproses Verifikasi YouTube Student...**\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "📝 Membuat data mahasiswa...\n"
        "🎨 Membuat kartu mahasiswa...\n"
        "📤 Mengirim dokumen..."
    , parse_mode='Markdown')

    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ **YouTube Student Sukses!**\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen terkirim, menunggu review SheerID\n"
                result_msg += "⏱️ Estimasi waktu: Beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 **Link Sukses:**\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ **Verifikasi Gagal:** {result.get('message', 'Error tidak diketahui')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            , parse_mode='Markdown')
    except Exception as e:
        logger.error("Error Verifikasi YouTube: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def verify6_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /verify6 - ChatGPT Veterans"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("⛔ Akun Anda diblokir.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Silakan ketik /start untuk mendaftar.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify6", "ChatGPT Veterans")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = MilitaryVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Link SheerID tidak valid.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Gagal memotong poin.")
        return

    processing_msg = await update.message.reply_text(
        f"🪖 **Memproses Verifikasi ChatGPT Veterans...**\n"
        f"🆔 ID: `{verification_id}`\n"
        f"💰 Terpotong: {VERIFY_COST} Poin\n\n"
        "🎖️ Membuat data veteran...\n"
        "📤 Mengirim dokumen..."
    , parse_mode='Markdown')

    semaphore = get_verification_semaphore("chatgpt_veteran")

    try:
        async with semaphore:
            verifier = MilitaryVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_veteran",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ **ChatGPT Veterans Sukses!**\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen terkirim, menunggu review SheerID\n"
                result_msg += "⏱️ Estimasi waktu: Beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 **Link Sukses:**\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ **Verifikasi Gagal:** {result.get('message', 'Error tidak diketahui')}\n\n"
                f"♻️ {VERIFY_COST} Poin telah dikembalikan."
            , parse_mode='Markdown')
    except Exception as e:
        logger.error("Error Verifikasi Military: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan sistem: {str(e)}\n\n"
            f"♻️ {VERIFY_COST} Poin telah dikembalikan."
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Handle perintah /getV4Code - Cek Kode Bolt.new Manual"""
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
            "`/getV4Code <verification_id>`\n\n"
            "Contoh:\n`/getV4Code 6929436b50d7dc18638890d0`\n\n"
            "💡 *Verification ID didapat setelah melakukan /verify4*"
        , parse_mode='Markdown')
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 **Mengecek status verifikasi...**"
    , parse_mode='Markdown')

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Gagal mengecek status (HTTP {response.status_code}).\n"
                    "Silakan coba lagi nanti."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ **Verifikasi Sukses!**\n\n"
                result_msg += f"🎁 **Kode Voucher:** `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"🔗 Link: {redirect_url}"
                await processing_msg.edit_text(result_msg, parse_mode='Markdown')
            
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ **Masih Pending**\n\n"
                    "Dokumen sedang ditinjau oleh SheerID.\n"
                    "Biasanya butuh 1-5 menit. Cek lagi nanti."
                , parse_mode='Markdown')
            
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    f"❌ **Verifikasi Ditolak**\n\n"
                    f"Alasan: {', '.join(error_ids) if error_ids else 'Tidak diketahui'}"
                , parse_mode='Markdown')
            
            else:
                await processing_msg.edit_text(
                    f"⚠️ **Status: {current_step}**\n\n"
                    "Kode belum keluar. Coba lagi nanti."
                , parse_mode='Markdown')

    except Exception as e:
        logger.error("Error GetV4Code: %s", e)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan: {str(e)}"
        )