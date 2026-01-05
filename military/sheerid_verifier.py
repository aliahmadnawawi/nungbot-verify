"""Engine Verifikasi Military (Veteran) - OpenAI Spec
Mengikuti alur: collectMilitaryStatus -> collectInactiveMilitaryPersonalInfo"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_email, generate_birth_date, generate_discharge_date
from .img_generator import generate_image

# Konfigurasi Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheerIDVerifier:
    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Setup Proxy
        proxy_url = getattr(config, 'PROXY_URL', None)
        if proxy_url and len(proxy_url) > 5:
            self.http_client = httpx.Client(timeout=30.0, proxy=proxy_url)
        else:
            self.http_client = httpx.Client(timeout=30.0)

    def __del__(self):
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    def _sheerid_request(self, method, url, body=None):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = self.http_client.request(method, url, json=body, headers=headers)
            try:
                return resp.json(), resp.status_code
            except:
                return resp.text, resp.status_code
        except Exception as e:
            logger.error(f"Request Error: {e}")
            raise

    def _upload_s3(self, url, data):
        """Upload PNG ke S3"""
        try:
            resp = self.http_client.put(url, content=data, headers={"Content-Type": "image/png"})
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.error(f"S3 Upload Error: {e}")
            return False

    def verify(self):
        try:
            # --- 1. PERSIAPAN DATA ---
            # Generate data palsu tapi valid
            name_data = NameGenerator.generate()
            first_name = name_data['first_name']
            last_name = name_data['last_name']
            
            email = generate_email(first_name, last_name)
            birth_date = generate_birth_date()
            discharge_date = generate_discharge_date(birth_date)
            
            # Pilih Organisasi Acak (Army, Navy, dll) dari Config
            org_data = random.choice(config.MILITARY_ORGS)
            
            logger.info(f"🪖 Veteran Profile: {first_name} {last_name}")
            logger.info(f"🎂 DOB: {birth_date} | 🚪 Discharge: {discharge_date}")
            logger.info(f"🎖️ Branch: {org_data['name']}")

            # --- 2. LANGKAH 1: collectMilitaryStatus ---
            # Sesuai README: Kirim status VETERAN dulu
            step1_url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus"
            step1_body = {
                "status": "VETERAN"
            }
            
            logger.info("📡 Langkah 1: Mengirim Status Veteran...")
            step1_resp, code = self._sheerid_request("POST", step1_url, step1_body)
            
            if code != 200:
                raise Exception(f"Gagal Set Status Veteran. Code: {code}")
            
            # Ambil URL untuk langkah selanjutnya dari respon
            submission_url = step1_resp.get("submissionUrl")
            if not submission_url:
                # Fallback jika submissionUrl tidak ada di respon json (kadang terjadi)
                submission_url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectInactiveMilitaryPersonalInfo"
            
            logger.info(f"✅ Status OK. Lanjut ke Submission URL.")

            # --- 3. LANGKAH 2: collectInactiveMilitaryPersonalInfo ---
            # Mengirim data lengkap ke URL yang didapat tadi
            
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "", # Boleh kosong
                "organization": {
                    "id": org_data['id'],
                    "name": org_data['name']
                },
                "dischargeDate": discharge_date,
                "locale": "en-US",
                "country": "US",
                "deviceFingerprintHash": self.device_fingerprint,
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"https://services.sheerid.com/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id,
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy."
                }
            }

            logger.info("📡 Langkah 2: Mengirim Data Pribadi...")
            step2_resp, code2 = self._sheerid_request("POST", submission_url, step2_body)

            if code2 != 200:
                raise Exception(f"Gagal Submit Data Pribadi. Code: {code2} | Msg: {step2_resp}")

            current_step = step2_resp.get("currentStep")
            logger.info(f"🔄 Current Step: {current_step}")

            if current_step == "error":
                error_msg = step2_resp.get('errorIds', ['Unknown Error'])
                raise Exception(f"Data Ditolak: {error_msg}")

            # --- 4. LANGKAH 3: Upload Dokumen (DD-214) ---
            if current_step == "docUpload":
                logger.info("🎨 Membuat Dokumen DD-214 Palsu...")
                # Generate gambar
                img_bytes = generate_image(first_name, last_name, discharge_date, org_data['name'])
                file_size = len(img_bytes)
                
                logger.info(f"📤 Upload Dokumen ({file_size} bytes)...")
                
                # Minta URL Upload ke SheerID
                doc_body = {
                    "files": [
                        {"fileName": "DD214_Certificate.png", "mimeType": "image/png", "fileSize": file_size}
                    ]
                }
                doc_url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload"
                doc_resp, _ = self._sheerid_request("POST", doc_url, doc_body)
                
                if "documents" not in doc_resp:
                    raise Exception("Gagal mendapatkan link upload S3")
                
                upload_url = doc_resp["documents"][0]["uploadUrl"]
                
                # Upload File Fisik ke S3
                if self._upload_s3(upload_url, img_bytes):
                    logger.info("✅ Upload S3 Berhasil. Konfirmasi ke SheerID...")
                    
                    # Konfirmasi selesai upload
                    final_url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload"
                    final_resp, _ = self._sheerid_request("POST", final_url)
                    
                    return {
                        "success": True,
                        "pending": True,
                        "message": "Dokumen DD-214 Berhasil Dikirim",
                        "redirect_url": final_resp.get("redirectUrl"),
                        "status": final_resp
                    }
                else:
                    raise Exception("Gagal Upload file ke Server S3")

            elif current_step == "success":
                # Langsung lolos (Hoki)
                return {
                    "success": True, 
                    "pending": False,
                    "message": "Verifikasi Instan Berhasil!",
                    "redirect_url": step2_resp.get("redirectUrl")
                }
                
            else:
                return {"success": False, "message": f"Step tidak dikenal: {current_step}"}

        except Exception as e:
            logger.error(f"❌ Military Verify Error: {e}")
            return {"success": False, "message": str(e)}