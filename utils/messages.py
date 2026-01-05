"""Template Pesan Bot (Bahasa Indonesia)"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL

# 🔥 AMBIL DARI MODULNYA SENDIRI (Bukan config.py)
try:
    from oaiteam.invite import OAITEAM_COST
except ImportError:
    OAITEAM_COST = 1 # Fallback biar gak error kalau modul belum siap

# ... (Sisanya ke bawah sama persis dengan kode kamu)


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Pesan Selamat Datang (/start)"""
    msg = (
        f"🎉 **Selamat Datang, {full_name}!**\n\n"
        "✅ Anda berhasil terdaftar dan mendapatkan **1 Poin Gratis**.\n"
    )
    if invited_by:
        msg += "🎁 Terima kasih telah bergabung lewat undangan teman (Bonus Referral diberikan).\n"

    msg += (
        "\n🤖 **Bot Verifikasi Otomatis SheerID**\n"
        "Saya bisa membantu Anda memverifikasi status Pelajar/Guru/Veteran secara instan.\n\n"
        "**Menu Cepat:**\n"
        "📜 /about - Fitur Bot\n"
        "💰 /balance - Cek Saldo Poin\n"
        "❓ /help - Daftar Perintah Lengkap\n\n"
        "**Cara Dapat Poin:**\n"
        "📅 /qd - Absen Harian (+1 Poin)\n"
        "🤝 /invite - Undang Teman (+2 Poin)\n"
        f"📢 Info Update: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Pesan Tentang Bot (/about)"""
    return (
        "🤖 **Tentang Bot SheerID Auto-Verify**\n\n"
        "**Fitur Unggulan:**\n"
        "✅ Verifikasi Otomatis (Auto-Submit Dokumen)\n"
        "✅ Support Proxy (Anti-Detect/Anti-Fraud)\n"
        "✅ Layanan: Gemini, ChatGPT, Spotify, YouTube, Bolt.new, Veteran\n\n"
        "**Sistem Poin:**\n"
        "🔹 Daftar Baru: **+1 Poin**\n"
        "🔹 Absen Harian (/qd): **+1 Poin**\n"
        "🔹 Undang Teman (/invite): **+2 Poin**\n"
        "🔹 Voucher (/use): **Sesuai Nominal**\n\n"
        f"📢 Channel Resmi: {CHANNEL_URL}\n\n"
        "**Cara Penggunaan:**\n"
        "1. Buka halaman verifikasi SheerID di browser.\n"
        "2. Copy Link Verifikasi (URL) yang ada `verificationId`-nya.\n"
        "3. Kirim ke bot sesuai layanan (contoh: `/verify <link>`).\n"
        "4. Tunggu bot memproses dokumen (1-2 menit)."
    )


def get_help_message(is_admin: bool = False) -> str:
    """Pesan Bantuan (/help)"""
    msg = (
        "📖 **PANDUAN LENGKAP**\n\n"
        "**👤 Perintah User:**\n"
        "/start - Daftar/Menu Utama\n"
        "/balance - Cek Sisa Poin\n"
        "/qd - Absen Harian (+1 Poin)\n"
        "/invite - Link Referral (+2 Poin)\n"
        "/use <kode> - Redeem Voucher Poin\n\n"
        "**✅ Layanan Verifikasi:**\n"
        f"🔹 `/verify <link>` - Gemini One Pro (-{VERIFY_COST} Poin)\n"
        f"🔹 `/verify2 <link>` - ChatGPT Teacher (-{VERIFY_COST} Poin)\n"
        f"🔹 `/verify3 <link>` - Spotify Student (-{VERIFY_COST} Poin)\n"
        f"🔹 `/verify4 <link>` - Bolt.new Teacher (-{VERIFY_COST} Poin)\n"
        f"🔹 `/verify5 <link>` - YouTube Student (-{VERIFY_COST} Poin)\n"
        f"🔹 `/verify6 <link>` - ChatGPT Veteran (-{VERIFY_COST} Poin)\n\n"
        "**🛠️ Alat Bantu:**\n"
        f"🔹 `/invite_gpt <email>` - Invite ke Tim ChatGPT (-{OAITEAM_COST} Poin)\n"
        "🔹 `/getV4Code <id>` - Cek Kode Bolt.new Manual\n"
    )

    if is_admin:
        msg += (
            "\n👮 **Perintah Admin:**\n"
            "/addbalance <ID> <Jml> - Tambah Poin User\n"
            "/block <ID> - Blokir User\n"
            "/white <ID> - Buka Blokir\n"
            "/blacklist - Daftar Blokir\n"
            "/genkey <Kode> <Poin> - Buat Voucher\n"
            "/listkeys - Daftar Voucher Aktif\n"
            "/broadcast <Pesan> - Kirim Pesan Massal\n"
        )
    
    msg += f"\n🆘 **Bantuan Lanjut:**\n{HELP_NOTION_URL}"

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Pesan Saldo Kurang"""
    return (
        f"❌ **Saldo Tidak Cukup!**\n\n"
        f"Saldo Anda: **{current_balance}** Poin\n"
        f"Biaya Layanan: **{VERIFY_COST}** Poin\n\n"
        "💡 **Cara Tambah Poin:**\n"
        "👉 Absen Harian: `/qd`\n"
        "👉 Undang Teman: `/invite`\n"
        "👉 Pakai Voucher: `/use <kode>`"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Panduan Cara Pakai Perintah Verifikasi"""
    return (
        f"ℹ️ **Panduan: {service_name}**\n\n"
        f"**Format:**\n`{command} <Link_SheerID>`\n\n"
        "**Contoh:**\n"
        f"`{command} https://services.sheerid.com/verify/xxx/?verificationId=abcdef12345`\n\n"
        "**Langkah-langkah:**\n"
        f"1. Buka halaman verifikasi {service_name}.\n"
        "2. Isi data awal sampai masuk ke halaman upload.\n"
        "3. Copy URL lengkap dari browser.\n"
        "4. Paste ke bot menggunakan perintah di atas."
    )