"""
Engine Invite ChatGPT Team (Mandiri)
Mengurus logika invite dan konfigurasi harga sendiri.
"""
import os
import httpx
import logging
from dotenv import load_dotenv

# Load file .env
load_dotenv()
logger = logging.getLogger(__name__)

# --- KONFIGURASI HARGA (PENTING: Jangan Dihapus) ---
OAITEAM_COST = 1  
# ---------------------------------------------------

class ChatGPTInviter:
    """Kelas untuk mengurus undangan OpenAI Team"""
    
    def __init__(self):
        # Ambil token langsung dari .env
        self.account_id = os.getenv("OAITEAM_ACCOUNT_ID")
        self.token = os.getenv("OAITEAM_TOKEN")
        
        if not self.account_id or not self.token:
            logger.warning("⚠️ Config OAITEAM belum lengkap di .env!")

    def invite(self, email: str) -> dict:
        """
        Mengirim request invite ke API ChatGPT
        Returns: Dict {'success': bool, 'message': str}
        """
        if not self.account_id or not self.token:
            return {
                "success": False, 
                "message": "Gagal: Token/Account ID belum diisi di .env"
            }

        url = f"https://chatgpt.com/backend-api/organizations/{self.account_id}/users"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        payload = {
            "email": email,
            "role": "standard"
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    return {"success": True, "message": "Invited"}
                else:
                    try:
                        err_msg = response.json().get('detail', response.text)
                    except:
                        err_msg = response.text
                    
                    return {
                        "success": False, 
                        "message": f"Ditolak OpenAI ({response.status_code}): {err_msg}"
                    }
                    
        except Exception as e:
            return {"success": False, "message": f"Network Error: {str(e)}"}