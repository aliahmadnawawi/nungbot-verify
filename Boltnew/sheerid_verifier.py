"""
Program Utama Verifikasi Guru SheerID (Bolt.new)
Termasuk fitur Auto-Proxy & Bahasa Indonesia
"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

# Import modul internal
from . import config
from .name_generator import NameGenerator, generate_birth_date
from .img_generator import generate_images, generate_psu_email

# Konfigurasi Log
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID Teacher Verifier (Bolt.new) dengan Dukungan Proxy"""

    def __init__(self, install_page_url: str, verification_id: Optional[str] = None):
        """Inisialisasi Verifier"""
        self.install_page_url = self.normalize_url(install_page_url)
        self.verification_id = verification_id
        self.external_user_id = self.parse_external_user_id(self.install_page_url)
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # --- MODIFIKASI PROXY (ANTI FRAUD) ---
        # Mengambil settingan proxy dari config.py
        proxy_url = getattr(config, 'PROXY_URL', None)
        
        if proxy_url and len(proxy_url) > 5:
            logger.info(f"🛡️ Mengaktifkan Mode Stealth (Proxy Aktif)...")
            self.http_client = httpx.Client(timeout=30.0, proxy=proxy_url)
        else:
            logger.warning("⚠️ PERINGATAN: Proxy tidak disetting! Menggunakan IP VPS (Rawan Ditolak).")
            self.http_client = httpx.Client(timeout=30.0)
        # -------------------------------------

    def __del__(self):
        """Membersihkan client HTTP"""
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        """Membuat sidik jari perangkat palsu"""
        chars = "0123456789abcdef"
        return "".join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Mengambil Verification ID dari URL"""
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def parse_external_user_id(url: str) -> Optional[str]:
        """Mengambil External User ID dari URL (Penting untuk Bolt.new)"""
        match = re.search(r"externalUserId=([^&]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def create_verification(self) -> str:
        """
        Membuat sesi verifikasi baru jika hanya punya installPageUrl
        (Biasanya Bolt.new memberikan link, lalu kita harus request ID dulu)
        """
        body = {
            "programId": config.PROGRAM_ID,
            "installPageUrl": self.install_page_url,
        }
        data, status = self._sheerid_request(
            "POST", f"{config.MY_SHEERID_URL}/rest/v2/verification/", body
        )
        
        if status != 200 or not isinstance(data, dict) or not data.get("verificationId"):
            raise Exception(f"Gagal membuat sesi verifikasi (Status {status}): {data}")

        self.verification_id = data["verificationId"]
        logger.info(f"✅ Berhasil membuat Verification ID: {self.verification_id}")
        return self.verification_id

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """Mengirim Request ke API SheerID"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = self.http_client.request(
            method=method, url=url, json=body, headers=headers
        )
        try:
            data = response.json()
        except Exception:
            data = response.text
        return data, response.status_code

    def _upload_to_s3(self, upload_url: str, img_data: bytes) -> bool:
        """Upload gambar PNG ke Server S3"""
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
        """
        Jalankan Proses Verifikasi Guru (Bolt.new)
        """
        try:
            current_step = "initial"

            # Generate Data Guru Palsu
            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            school_id = school_id or config.DEFAULT_SCHOOL_ID
            school = config.SCHOOLS[school_id]

            if not email:
                email = generate_psu_email(first_name, last_name)
            if not birth_date:
                birth_date = generate_birth_date()
            if not self.external_user_id:
                # Jika link tidak ada externalUserId, buat fake ID acak
                self.external_user_id = str(random.randint(1000000, 9999999))

            # Pastikan punya Verification ID
            if not self.verification_id:
                logger.info("Membuat sesi verifikasi baru...")
                self.create_verification()

            logger.info(f"Guru: {first_name} {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"Sekolah: {school['name']}")
            logger.info(f"ID Verifikasi: {self.verification_id}")

            # Langkah 1: Buat Dokumen Palsu
            logger.info("Langkah 1/5: Membuat Dokumen Guru (PNG)...")
            assets = generate_images(first_name, last_name, school_id)
            for asset in assets:
                logger.info(f"  - {asset['file_name']} ({len(asset['data'])/1024:.2f}KB)")

            # Langkah 2: Submit Data Diri
            logger.info("Langkah 2/5: Mengirim Data Diri...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": "", # Bolt teacher biasanya tidak butuh tanggal lahir di form awal
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": int(school_id),
                    "idExtended": school["idExtended"],
                    "name": school["name"],
                },
                "deviceFingerprintHash": self.device_fingerprint,
                "externalUserId": self.external_user_id,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": True,
                    "refererUrl": self.install_page_url,
                    "externalUserId": self.external_user_id,
                    "flags": '{"doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","include-cvec-field-france-student":"not-labeled-optional","org-search-overlay":"default","org-selected-display":"default"}',
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount",
                },
            }

            step2_data, step2_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectTeacherPersonalInfo",
                step2_body,
            )

            if step2_status != 200:
                raise Exception(f"Gagal Langkah 2 (Status {step2_status}): {step2_data}")
            
            # Cek Error dari Response
            if isinstance(step2_data, dict) and step2_data.get("currentStep") == "error":
                error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                raise Exception(f"Ditolak SheerID: {error_msg}")

            logger.info(f"✅ Langkah 2 Sukses. Status: {getattr(step2_data, 'get', lambda k, d=None: d)('currentStep')}")
            
            current_step = (
                step2_data.get("currentStep", current_step) if isinstance(step2_data, dict) else current_step
            )

            # Langkah 3: Skip SSO (Jika muncul)
            if current_step in ["sso", "collectTeacherPersonalInfo"]:
                logger.info("Langkah 3/5: Melewati SSO...")
                step3_data, _ = self._sheerid_request(
                    "DELETE",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                )
                logger.info(f"✅ Langkah 3 Selesai.")
                current_step = (
                    step3_data.get("currentStep", current_step) if isinstance(step3_data, dict) else current_step
                )

            # Langkah 4: Upload Dokumen
            logger.info("Langkah 4/5: Meminta Link Upload...")
            step4_body = {
                "files": [
                    {
                        "fileName": asset["file_name"],
                        "mimeType": "image/png",
                        "fileSize": len(asset["data"]),
                    }
                    for asset in assets
                ]
            }
            step4_data, step4_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step4_body,
            )
            
            if step4_status != 200 or not isinstance(step4_data, dict) or not step4_data.get("documents"):
                raise Exception(f"Gagal mendapatkan link upload: {step4_data}")

            documents = step4_data["documents"]
            if len(documents) != len(assets):
                raise Exception("Jumlah slot upload tidak sesuai dengan jumlah file.")

            # Upload setiap file
            for doc, asset in zip(documents, assets):
                upload_url = doc.get("uploadUrl")
                if not upload_url:
                    raise Exception("Link upload kosong.")
                
                if not self._upload_to_s3(upload_url, asset["data"]):
                    raise Exception(f"Gagal Upload ke S3: {asset['file_name']}")
                
                logger.info(f"✅ Berhasil Upload: {asset['file_name']}")

            # Langkah 5: Finalisasi Upload
            step6_data, _ = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
            )
            logger.info(f"✅ Dokumen Terkirim! Status Akhir: {getattr(step6_data, 'get', lambda k, d=None: d)('currentStep')}")

            # Cek Hasil Akhir (Apakah langsung dapat kode?)
            final_status, _ = self._sheerid_request(
                "GET",
                f"{config.MY_SHEERID_URL}/rest/v2/verification/{self.verification_id}",
            )
            
            reward_code = None
            if isinstance(final_status, dict):
                reward_code = final_status.get("rewardCode") or final_status.get("rewardData", {}).get("rewardCode")

            return {
                "success": True,
                "pending": final_status.get("currentStep") != "success" if isinstance(final_status, dict) else True,
                "message": "Dokumen terkirim. Menunggu review."
                if not isinstance(final_status, dict) or final_status.get("currentStep") != "success"
                else "Verifikasi Sukses!",
                "verification_id": self.verification_id,
                "redirect_url": final_status.get("redirectUrl") if isinstance(final_status, dict) else None,
                "reward_code": reward_code,
                "status": final_status,
            }

        except Exception as e:
            logger.error(f"❌ ERROR FATAL: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """Fungsi Utama (Untuk Test Manual di Terminal)"""
    import sys

    print("=" * 60)
    print("SheerID Teacher Verifier (Bolt.new)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan Link Verifikasi Bolt.new (ada externalUserId): ").strip()

    if not url:
        print("❌ Error: Link kosong!")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    verifier = SheerIDVerifier(url, verification_id=verification_id)

    print(f"👉 Link Install: {verifier.install_page_url}")
    if verifier.verification_id:
        print(f"ID Ditemukan: {verifier.verification_id}")
    if verifier.external_user_id:
        print(f"User ID Eksternal: {verifier.external_user_id}")
    print()

    result = verifier.verify()

    print()
    print("=" * 60)
    print("HASIL VERIFIKASI:")
    print("=" * 60)
    print(f"Status: {'✅ SUKSES' if result['success'] else '❌ GAGAL'}")
    print(f"Pesan: {result['message']}")
    if result.get("reward_code"):
        print(f"🎁 Kode Voucher: {result['reward_code']}")
    if result.get("redirect_url"):
        print(f"🔗 Link: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())