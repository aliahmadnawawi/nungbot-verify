# Gunakan Image Python 3.11 Resmi (Versi Ringan/Slim)
FROM python:3.11-slim

# Tentukan folder kerja di dalam container
WORKDIR /app

# Install dependensi sistem (Wajib untuk menjalankan Browser/Playwright)
# Ini berisi daftar "onderdil" Linux yang dibutuhkan supaya Chrome bisa jalan
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    build-essential gcc pkg-config libcairo2-dev libpango1.0-dev libgdk-pixbuf-2.0-dev libffi-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Salin file daftar library (requirements.txt) ke dalam container
COPY requirements.txt .

# Install library Python (Tanpa cache agar hemat tempat)
RUN pip install --no-cache-dir -r requirements.txt

# Install Browser Chromium (PENTING untuk generate screenshot)
RUN playwright install chromium

# Salin semua file project bot ke dalam container
# (.dockerignore akan otomatis membuang file sampah/cache)
COPY . .

# Bersihkan semua cache Python lama (Supaya kode terbaru yang terbaca)
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
RUN find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Setting Variabel Lingkungan
# PYTHONDONTWRITEBYTECODE=1: Jangan bikin file .pyc (sampah)
# PYTHONUNBUFFERED=1: Tampilkan log error secara langsung (real-time)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Konfigurasi MySQL
# (Biasanya diatur lewat docker-compose.yml, jadi tidak ditulis mati di sini)

# Cek Kesehatan Bot (Healthcheck)
# Setiap 30 detik, sistem akan mengecek apakah "bot.py" masih jalan
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "python.*bot.py" || exit 1

# Perintah Terakhir: JALANKAN BOT!
CMD ["python", "-u", "bot.py"]