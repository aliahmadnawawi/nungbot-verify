# File Konfigurasi Military (ChatGPT Veteran)
# Lokasi: /military/config.py

# SheerID Program ID untuk OpenAI / ChatGPT Military
PROGRAM_ID = '66e0160f4ee8a543f458641a' 

SHEERID_BASE_URL = 'https://services.sheerid.com'

# --- KONFIGURASI PROXY ---
# Format: "http://user:pass@ip:port"
PROXY_URL = "" 
# -------------------------

# Batasan Ukuran File
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Daftar Organisasi Militer (Sesuai README)
# ID ini PENTING agar verifikasi valid
MILITARY_ORGS = [
    {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY"
    },
    {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY"
    },
    {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY"
    },
    {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY"
    },
    {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY"
    },
    {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY"
    }
]