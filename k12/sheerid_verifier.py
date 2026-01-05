"""
Program Utama Verifikasi Guru SheerID (DENGAN DUKUNGAN PROXY)
Diterjemahkan & Dimodifikasi untuk Support Proxy
"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

# Mendukung impor sebagai paket atau skrip langsung
try:
    from . import config  # type: ignore
    from .name_generator import NameGenerator, generate_email, generate_birth_date  # type: ignore
    from .img_generator import generate_teacher_pdf, generate_teacher_png  # type: ignore
except ImportError:
    import config  # type: ignore
    from name_generator import NameGenerator, generate_email, generate_birth_date  # type: ignore
    from img_generator import generate_teacher_pdf, generate_teacher_png  # type: ignore

# Impor Konstanta Konfigurasi
PROGRAM_ID = config.PROGRAM_ID
SHEERID_BASE_URL = config.SHEERID_BASE_URL
MY_SHEERID_URL = config.MY_SHEERID_URL
SCHOOLS = config.SCHOOLS
DEFAULT_SCHOOL_ID = config.DEFAULT_SCHOOL_ID

# Konfigurasi Log (Pencatat Aktivitas)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID Verifier dengan Dukungan Proxy"""

    def __init__(self, verification_id: str):
        """
        Inisialisasi Verifier (Persiapan Awal)
        """
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # --- MODIFIKASI PROXY (JURUS ANTI FRAUD) ---
        # Mengambil settingan proxy dari config.py
        proxy_url = getattr(config, 'PROXY_URL', None)
        
        if proxy_url and len(proxy_url) > 5:
            logger.info(f"🛡️ Mengaktifkan Mode Stealth (Proxy Aktif)...")
            # Menggunakan Proxy untuk menyamarkan IP VPS
            self.http_client = httpx.Client(timeout=30.0, proxy=proxy_url)
        else:
            logger.warning("⚠️ PERINGATAN: Proxy tidak disetting! Menggunakan IP VPS (Rawan Ditolak SheerID).")
            self.http_client = httpx.Client(timeout=30.0)
        # -------------------------------------------

    def __del__(self):
        """Membersihkan Client HTTP saat selesai"""
        if hasattr(self, 'http_client'):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        """Membuat sidik jari perangkat palsu (Biar dikira HP/Laptop asli)"""
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Mengambil ID Verifikasi dari Link"""
        match = re.search(r'verificationId=([a-f0-9]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _sheerid_request(self, method: str, url: str,
                          body: Optional[Dict] = None) -> Tuple[Dict, int]:
        """
        Mengirim Request ke Server SheerID
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            response = self.http_client.request(
                method=method,
                url=url,
                json=body,
                headers=headers
            )

            try:
                data = response.json()
            except Exception:
                data = response.text

            return data, response.status_code
        except Exception as e:
            logger.error(f"Gagal menghubungi server SheerID: {e}")
            raise

    def _upload_to_s3(self, upload_url: str, content: bytes, mime_type: str) -> bool:
        """
        Upload dokumen ke Server Penyimpanan (S3)
        """
        try:
            headers = {
                'Content-Type': mime_type,
            }
            response = self.http_client.put(
                upload_url,
                content=content,
                headers=headers,
                timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"Gagal Upload Dokumen: {e}")
            return False

    def verify(self, first_name: str = None, last_name: str = None,
               email: str = None, birth_date: str = None,
               school_id: str = None,
               hcaptcha_token: str = None, turnstile_token: str = None) -> Dict:
        """
        Jalankan Proses Verifikasi Guru
        """
        try:
            current_step = 'initial'

            # Generate Data Guru Palsu (Jika tidak diisi manual)
            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name['first_name']
                last_name = name['last_name']

            school_id = school_id or DEFAULT_SCHOOL_ID
            school = SCHOOLS[school_id]

            if not email:
                email = generate_email()

            if not birth_date:
                birth_date = generate_birth_date()

            logger.info(f"Identitas: {first_name} {last_name} | {email}")
            logger.info(f"Target Sekolah: {school['name']}")

            # Langkah 1: Bikin Dokumen Palsu
            logger.info("Langkah 1/4: Membuat Dokumen Bukti Guru (PDF & PNG)...")
            pdf_data = generate_teacher_pdf(first_name, last_name)
            png_data = generate_teacher_png(first_name, last_name)
            pdf_size = len(pdf_data)
            png_size = len(png_data)
            logger.info(f"✓ Ukuran File: PDF={pdf_size/1024:.1f}KB, PNG={png_size/1024:.1f}KB")

            # Langkah 2: Submit Data Diri
            logger.info("Langkah 2/4: Mengirim Data Diri ke SheerID...")
            step2_body = {
                'firstName': first_name,
                'lastName': last_name,
                'birthDate': birth_date,
                'email': email,
                'phoneNumber': '',
                'organization': {
                    'id': school['id'],
                    'idExtended': school['idExtended'],
                    'name': school['name']
                },
                'deviceFingerprintHash': self.device_fingerprint,
                'locale': 'en-US',
                'metadata': {
                    'marketConsentValue': False,
                    'refererUrl': f"{SHEERID_BASE_URL}/verify/{PROGRAM_ID}/?verificationId={self.verification_id}",
                    'verificationId': self.verification_id,
                    # Teks di bawah ini Bahasa Inggris Legal (JANGAN DIUBAH agar valid)
                    'submissionOptIn': 'By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount'
                }
            }

            step2_data, step2_status = self._sheerid_request(
                'POST',
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectTeacherPersonalInfo",
                step2_body
            )

            if step2_status != 200:
                raise Exception(f"Gagal di Langkah 2 (Code {step2_status}): {step2_data}")

            if step2_data.get('currentStep') == 'error':
                error_msg = ', '.join(step2_data.get('errorIds', ['Error tidak diketahui']))
                raise Exception(f"SheerID Menolak Data: {error_msg}")

            logger.info(f"✓ Langkah 2 Sukses. Status: {step2_data.get('currentStep')}")
            current_step = step2_data.get('currentStep', current_step)

            # Langkah 3: Skip SSO (Jika muncul)
            if current_step in ['sso', 'collectTeacherPersonalInfo']:
                logger.info("Langkah 3/4: Melewati Login Kampus (Bypass SSO)...")
                step3_data, _ = self._sheerid_request(
                    'DELETE',
                    f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                )
                logger.info(f"✓ Langkah 3 Selesai.")
                current_step = step3_data.get('currentStep', current_step)

            # Langkah 4: Upload Dokumen
            logger.info("Langkah 4/4: Mengupload Dokumen Palsu...")
            step4_body = {
                'files': [
                    {
                        'fileName': 'teacher_document.pdf',
                        'mimeType': 'application/pdf',
                        'fileSize': pdf_size
                    },
                    {
                        'fileName': 'teacher_document.png',
                        'mimeType': 'image/png',
                        'fileSize': png_size
                    }
                ]
            }

            step4_data, step4_status = self._sheerid_request(
                'POST',
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step4_body
            )

            documents = step4_data.get('documents') or []
            if len(documents) < 2:
                raise Exception("Gagal mendapatkan link upload dokumen dari SheerID")

            pdf_upload_url = documents[0]['uploadUrl']
            png_upload_url = documents[1]['uploadUrl']

            if not self._upload_to_s3(pdf_upload_url, pdf_data, 'application/pdf'):
                raise Exception("Gagal Upload PDF ke Server")
            if not self._upload_to_s3(png_upload_url, png_data, 'image/png'):
                raise Exception("Gagal Upload PNG ke Server")
            
            logger.info("✓ Upload Dokumen Berhasil")

            # Finalisasi (Konfirmasi Selesai)
            step6_data, _ = self._sheerid_request(
                'POST',
                f"{SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload"
            )
            final_status = step6_data

            return {
                'success': True,
                'pending': True,
                'message': 'Dokumen terkirim. Menunggu review SheerID.',
                'verification_id': self.verification_id,
                'redirect_url': final_status.get('redirectUrl'),
                'status': final_status
            }

        except Exception as e:
            logger.error(f"✗ ERROR FATAL: {e}")
            return {
                'success': False,
                'message': str(e),
                'verification_id': self.verification_id
            }