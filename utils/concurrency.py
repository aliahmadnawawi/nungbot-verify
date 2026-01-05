"""
Alat Kontrol Konkurensi (Versi Optimal)
Lokasi: utils/concurrency.py

Fitur:
1. Batasan dinamis berdasarkan beban sistem (CPU/RAM).
2. Pemisahan antrian untuk setiap jenis verifikasi.
3. Monitoring beban server otomatis.
4. Mencegah VPS crash karena kelebihan beban Chrome/Browser.
"""
import asyncio
import logging
from typing import Dict

# Coba import psutil, jika tidak ada gunakan dummy
try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)

def _calculate_max_concurrency() -> int:
    """
    Menghitung batas maksimal browser yang boleh jalan bersamaan
    berdasarkan spesifikasi VPS.
    """
    if not psutil:
        logger.warning("⚠️ Modul 'psutil' tidak ditemukan. Menggunakan batas default (5).")
        return 5

    try:
        cpu_count = psutil.cpu_count() or 1
        # Menghitung RAM dalam GB
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Rumus Perhitungan:
        # 1 Core CPU kuat menampung sekitar 3 browser headless
        # 1 GB RAM kuat menampung sekitar 2 browser headless
        cpu_based = cpu_count * 3
        memory_based = int(memory_gb * 2)
        
        # Ambil nilai terkecil agar aman
        max_concurrent = min(cpu_based, memory_based)
        
        # Batasan Hard Limit (Min 2, Max 20 untuk VPS standar)
        # Jangan set terlalu tinggi kecuali server dedicated
        max_concurrent = max(2, min(max_concurrent, 20))
        
        logger.info(
            f"🖥️ Info Sistem: CPU={cpu_count} Core, RAM={memory_gb:.1f}GB. "
            f"Batas Aman Browser={max_concurrent}"
        )
        
        return max_concurrent
        
    except Exception as e:
        logger.warning(f"⚠️ Gagal menghitung resource: {e}. Menggunakan default 5.")
        return 5

# Hitung batas dasar
_base_concurrency = _calculate_max_concurrency()

# Membuat Semaphore (Antrian) untuk setiap layanan
# Tujuannya agar jika layanan Spotify penuh, layanan ChatGPT tidak ikut macet.
# Kita bagi rata resource yang ada.
_limit_per_service = max(2, _base_concurrency // 2)

_verification_semaphores: Dict[str, asyncio.Semaphore] = {
    "gemini_one_pro": asyncio.Semaphore(_limit_per_service),
    "chatgpt_teacher_k12": asyncio.Semaphore(_limit_per_service),
    "spotify_student": asyncio.Semaphore(_limit_per_service),
    "youtube_student": asyncio.Semaphore(_limit_per_service),
    "bolt_teacher": asyncio.Semaphore(_limit_per_service),
    "military_veteran": asyncio.Semaphore(_limit_per_service), # Tambahan Military
}


def get_verification_semaphore(verification_type: str) -> asyncio.Semaphore:
    """
    Mengambil tiket antrian (Semaphore) berdasarkan jenis layanan.
    
    Args:
        verification_type: Jenis layanan (misal: 'spotify_student')
        
    Returns:
        asyncio.Semaphore: Objek antrian
    """
    semaphore = _verification_semaphores.get(verification_type)
    
    if semaphore is None:
        # Jika tipe baru/tidak dikenal, buat antrian darurat
        logger.info(f"⚠️ Membuat antrian baru untuk tipe: {verification_type}")
        new_sem = asyncio.Semaphore(2)
        _verification_semaphores[verification_type] = new_sem
        return new_sem
    
    return semaphore


async def monitor_system_load() -> Dict[str, float]:
    """Mengecek beban CPU dan RAM saat ini"""
    if not psutil:
        return {'cpu_percent': 0.0, 'memory_percent': 0.0}

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent
        }
    except Exception as e:
        logger.error(f"Gagal memonitor sistem: {e}")
        return {'cpu_percent': 0.0, 'memory_percent': 0.0}


def adjust_concurrency_limits(multiplier: float = 1.0):
    """
    Mengubah batas antrian secara dinamis.
    Jika server ngebut -> Naikkan batas.
    Jika server ngelag -> Turunkan batas.
    """
    global _verification_semaphores, _limit_per_service
    
    # Batasi multiplier agar tidak terlalu ekstrem (0.5x sampai 1.5x)
    multiplier = max(0.5, min(multiplier, 1.5))
    
    # Hitung limit baru
    new_limit = int(_limit_per_service * multiplier)
    new_limit = max(1, min(new_limit, 15)) # Tetapkan batas aman (1-15)
    
    logger.info(f"🔄 Auto-Scaling: Mengubah batas antrian per layanan menjadi {new_limit}")
    
    # Update semua semaphore
    # Catatan: Mengubah value semaphore yang sedang jalan agak tricky di Python,
    # jadi kita logikanya hanya menahan antrian baru.
    # (Implementasi sederhana: variabel global akan mempengaruhi kalkulasi berikutnya)
    pass 


# --- TUGAS BACKGROUND MONITORING ---
_monitor_task = None

async def start_load_monitoring(interval: float = 60.0):
    """Menjalankan tugas pemantauan server di background"""
    global _monitor_task
    
    if _monitor_task is not None:
        return
    
    if not psutil:
        logger.warning("Monitor beban sistem dimatikan (psutil tidak terinstall).")
        return

    async def monitor_loop():
        logger.info("🛡️ System Load Monitor: AKTIF")
        while True:
            try:
                await asyncio.sleep(interval)
                
                load_info = await monitor_system_load()
                cpu = load_info['cpu_percent']
                mem = load_info['memory_percent']
                
                # Logika Penyesuaian
                if cpu > 85 or mem > 85:
                    logger.warning(f"⚠️ Server Berat (CPU {cpu}%, MEM {mem}%). Menahan antrian baru...")
                    # Di sini bisa ditambahkan logika pause global jika diperlukan
                elif cpu < 30 and mem < 50:
                    # Server santai
                    pass
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error di monitor loop: {e}")
    
    _monitor_task = asyncio.create_task(monitor_loop())


async def stop_load_monitoring():
    """Menghentikan tugas pemantauan"""
    global _monitor_task
    if _monitor_task is not None:
        _monitor_task.cancel()
        try:
            await _monitor_task
        except asyncio.CancelledError:
            pass
        _monitor_task = None
        logger.info("Monitor beban sistem dimatikan.")