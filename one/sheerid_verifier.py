"""Program Utama Verifikasi Mahasiswa SheerID (MODIFIED WITH PROXY)"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

# Import modul internal
from . import config
from .name_generator import NameGenerator, generate_birth_date
from .img_generator import generate_image, generate_psu_email

# Konfigurasi Log (Pencatat Aktivitas)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID Student Verifier dengan Dukungan Proxy"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # --- MODIFIKASI PROXY (JURUS ANTI FRAUD) ---
        # Mencoba mengambil settingan proxy dari config.py
        # Menggunakan getattr agar tidak error jika variabel belum ada
        proxy_url = getattr(config, 'PROXY_URL', None)
        
        if proxy_url and len(proxy_url) > 5:
            logger.info(f"🛡️ Mengaktifkan Mode Stealth (Proxy Aktif)...")
            self.http_client = httpx.Client(timeout=30.0, proxy=proxy_url)
        else:
            logger.warning("⚠️ PERINGATAN: Proxy tidak disetting! Menggunakan IP VPS (Rawan Ditolak).")
            self.http_client = httpx.Client(timeout=30.0)
        # -------------------------------------------

    def __del__(self):
        """Membersihkan koneksi saat selesai"""
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        """Membuat sidik jari perangkat palsu"""
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Mengambil ID dari Link Verifikasi"""
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """Mengirim Request ke Server SheerID"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            response = self.http_client.request(
                method=method, url=url, json=body, headers=headers
            )
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data, response.status_code
        except Exception as e:
            logger.error(f"Gagal menghubungi SheerID: {e}")
            raise

    def _upload_to_s3(self, upload_url: str, img_data: bytes) -> bool:
        """Upload gambar PNG ke Server (S3)"""
        try:
            headers = {"Content-Type": "image/png"}
            response = self.http_client.put(
                upload_url, content=img_data, headers=headers, timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"Gagal Upload ke S3: {e}")
            return False

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
    ) -> Dict:
        """Jalankan Proses Verifikasi Mahasiswa"""
        try:
            current_step = "initial"

            # Generate Data Mahasiswa Palsu
            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            school_id = school_id or config.DEFAULT_SCHOOL_ID
            school = config.SCHOOLS[school_id]

            if not email:
                # Menggunakan Email Kampus PSU (Penn State)
                email = generate_psu_email(first_name, last_name)
            if not birth_date:
                birth_date = generate_birth_date()

            logger.info(f"Mahasiswa: {first_name} {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"Kampus: {school['name']}")
            logger.info(f"Lahir: {birth_date}")

            # Langkah 1: Bikin Kartu Mahasiswa
            logger.info("Langkah 1/4: Membuat PNG Kartu Mahasiswa...")
            img_data = generate_image(first_name, last_name, school_id)
            file_size = len(img_data)
            logger.info(f"✅ Ukuran PNG: {file_size / 1024:.2f}KB")

            # Langkah 2: Submit Data Diri
            logger.info("Langkah 2/4: Mengirim Data Mahasiswa...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": int(school_id),
                    "idExtended": school["idExtended"],
                    "name": school["name"],
                },
                "deviceFingerprintHash": self.device_fingerprint,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id,
                    "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount",
                },
            }

            step2_data, step2_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
                step2_body,
            )

            if step2_status != 200:
                raise Exception(f"Gagal Langkah 2 (Status {step2_status}): {step2_data}")
            if step2_data.get("currentStep") == "error":
                error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                raise Exception(f"Ditolak SheerID: {error_msg}")

            logger.info(f"✅ Langkah 2 Sukses. Status: {step2_data.get('currentStep')}")
            current_step = step2_data.get("currentStep", current_step)

            # Langkah 3: Skip SSO (Jika muncul)
            if current_step in ["sso", "collectStudentPersonalInfo"]:
                logger.info("Langkah 3/4: Melewati Login Kampus (Bypass SSO)...")
                step3_data, _ = self._sheerid_request(
                    "DELETE",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                )
                logger.info(f"✅ Langkah 3 Selesai.")
                current_step = step3_data.get("currentStep", current_step)

            # Langkah 4: Upload Dokumen
            logger.info("Langkah 4/4: Upload Dokumen Kartu Mahasiswa...")
            step4_body = {
                "files": [
                    {"fileName": "student_card.png", "mimeType": "image/png", "fileSize": file_size}
                ]
            }
            step4_data, step4_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step4_body,
            )
            if not step4_data.get("documents"):
                raise Exception("Gagal mendapatkan link upload dokumen")

            upload_url = step4_data["documents"][0]["uploadUrl"]
            
            if not self._upload_to_s3(upload_url, img_data):
                raise Exception("Gagal Upload ke Server S3")
            logger.info("✅ Upload Sukses")

            step6_data, _ = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
            )
            logger.info(f"✅ Dokumen Terkirim! Status Akhir: {step6_data.get('currentStep')}")
            final_status = step6_data

            return {
                "success": True,
                "pending": True,
                "message": "Dokumen terkirim. Menunggu review SheerID.",
                "verification_id": self.verification_id,
                "redirect_url": final_status.get("redirectUrl"),
                "status": final_status,
            }

        except Exception as e:
            logger.error(f"❌ ERROR FATAL: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """Fungsi Utama (Jika dijalankan lewat Terminal)"""
    import sys

    print("=" * 60)
    print("SheerID Student Verifier (Gemini Version)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan Link Verifikasi SheerID: ").strip()

    if not url:
        print("❌ Error: Link kosong!")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ Error: Format Link Salah (Tidak ada Verification ID)")
        sys.exit(1)

    print(f"✅ ID Ditemukan: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

    print()
    print("=" * 60)
    print("HASIL VERIFIKASI:")
    print("=" * 60)
    print(f"Status: {'✅ SUKSES' if result['success'] else '❌ GAGAL'}")
    print(f"Pesan: {result['message']}")
    if result.get("redirect_url"):
        print(f"Link Sukses: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())