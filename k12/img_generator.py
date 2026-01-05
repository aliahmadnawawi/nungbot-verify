"""Generator Dokumen Bukti Guru (PDF + PNG)"""
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

# Library untuk bikin PDF
from xhtml2pdf import pisa


def _render_template(first_name: str, last_name: str) -> str:
    """
    Membaca template HTML, mengganti Nama/ID/Tanggal, 
    dan membereskan variabel CSS supaya terbaca oleh PDF generator.
    """
    full_name = f"{first_name} {last_name}"
    
    # Generate ID Karyawan Acak (7 digit)
    employee_id = random.randint(1000000, 9999999)
    
    # Format tanggal ala Amerika (Bulan/Tanggal/Tahun)
    current_date = datetime.now().strftime("%m/%d/%Y %I:%M %p")

    # Mencari file card-temp.html di folder yang sama
    template_path = Path(__file__).parent / "card-temp.html"
    
    # Cek apakah file template ada
    if not template_path.exists():
        raise FileNotFoundError(f"Template tidak ditemukan di: {template_path}")

    html = template_path.read_text(encoding="utf-8")

    # Fix CSS Variables (xhtml2pdf tidak bisa baca var(--color), jadi harus diganti manual)
    color_map = {
        "var(--primary-blue)": "#0056b3",
        "var(--border-gray)": "#dee2e6",
        "var(--bg-gray)": "#f8f9fa",
    }
    for placeholder, color in color_map.items():
        html = html.replace(placeholder, color)

    # Mengganti Data Dummy di HTML dengan Data Bot
    # Nama "Sarah J. Connor" di template diganti nama generate
    html = html.replace("Sarah J. Connor", full_name)
    # ID "E-9928104" diganti ID acak
    html = html.replace("E-9928104", f"E-{employee_id}")
    # Masukkan tanggal hari ini
    html = html.replace('id="currentDate"></span>', f'id="currentDate">{current_date}</span>')

    return html


def generate_teacher_pdf(first_name: str, last_name: str) -> bytes:
    """Membuat file PDF dari hasil render HTML."""
    html = _render_template(first_name, last_name)

    output = BytesIO()
    # PISA mengubah HTML jadi PDF
    pisa_status = pisa.CreatePDF(html, dest=output, encoding="utf-8")
    
    if pisa_status.err:
        raise Exception("Gagal membuat file PDF (Pisa Error)")

    pdf_data = output.getvalue()
    output.close()
    return pdf_data


def generate_teacher_png(first_name: str, last_name: str) -> bytes:
    """
    Menggunakan Browser Virtual (Playwright) untuk memotret HTML jadi PNG.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright belum terinstall. Jalankan: pip install playwright && playwright install chromium"
        ) from exc

    html = _render_template(first_name, last_name)

    with sync_playwright() as p:
        # Launch Browser Headless (Tanpa layar monitor)
        browser = p.chromium.launch(headless=True)
        # Buka halaman baru dengan ukuran cukup besar
        page = browser.new_page(viewport={"width": 1200, "height": 1000})
        
        # Masukkan konten HTML ke browser
        page.set_content(html, wait_until="load")
        
        # Tunggu 0.5 detik biar tampilan stabil
        page.wait_for_timeout(500) 
        
        # Cari elemen .browser-mockup (kotak utama) lalu screenshot
        card = page.locator(".browser-mockup")
        png_bytes = card.screenshot(type="png")
        
        browser.close()

    return png_bytes


# Fungsi Kompatibilitas (Jika dipanggil tanpa format, default ke PDF)
def generate_teacher_image(first_name: str, last_name: str) -> bytes:
    return generate_teacher_pdf(first_name, last_name)