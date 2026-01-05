"""
Generator Dokumen Militer (DD-214 Mockup)
Menggunakan Playwright untuk render HTML ke PNG.
"""
import random
from datetime import datetime

def generate_html(first_name, last_name, discharge_date, branch):
    """Membuat HTML mirip formulir DD-214 sederhana"""
    
    # Format tanggal US
    try:
        d_obj = datetime.strptime(discharge_date, "%Y-%m-%d")
        fmt_discharge = d_obj.strftime("%b %d, %Y").upper()
        
        # Entry date (3-4 tahun sebelum discharge)
        entry_year = d_obj.year - random.randint(3, 6)
        fmt_entry = d_obj.strftime("%b %d").upper() + f", {entry_year}"
        
        dob_year = entry_year - random.randint(18, 20)
        fmt_dob = d_obj.strftime("%b %d").upper() + f", {dob_year}"
        
    except:
        fmt_discharge = "JAN 01, 2020"
        fmt_entry = "JAN 01, 2016"
        fmt_dob = "JAN 01, 1990"

    full_name = f"{last_name}, {first_name}".upper()
    ssn = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: "Courier New", Courier, monospace; background: white; padding: 40px; color: black; }}
            .container {{ border: 2px solid black; padding: 20px; width: 900px; height: 1100px; position: relative; }}
            .header {{ text-align: center; border-bottom: 2px solid black; padding-bottom: 10px; margin-bottom: 10px; }}
            h1 {{ font-size: 18px; margin: 0; }}
            h2 {{ font-size: 14px; margin: 0; font-weight: normal; }}
            .row {{ display: flex; border-bottom: 1px solid black; }}
            .col {{ flex: 1; border-right: 1px solid black; padding: 5px; font-size: 12px; }}
            .col:last-child {{ border-right: none; }}
            .label {{ font-size: 9px; font-weight: bold; display: block; margin-bottom: 2px; }}
            .value {{ font-size: 14px; font-weight: bold; font-family: "Arial", sans-serif; }}
            .checkbox {{ display: inline-block; width: 10px; height: 10px; border: 1px solid black; margin-right: 5px; }}
            .checked {{ background: black; }}
            .footer {{ position: absolute; bottom: 20px; left: 20px; right: 20px; text-align: center; font-size: 10px; border-top: 2px solid black; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CERTIFICATE OF RELEASE OR DISCHARGE FROM ACTIVE DUTY</h1>
                <h2>DD FORM 214</h2>
            </div>
            
            <div class="row">
                <div class="col" style="flex: 2;">
                    <span class="label">1. NAME (Last, First, Middle)</span>
                    <span class="value">{full_name}</span>
                </div>
                <div class="col">
                    <span class="label">2. DEPARTMENT, COMPONENT AND BRANCH</span>
                    <span class="value">{branch.replace('_', ' ')} - US</span>
                </div>
                <div class="col">
                    <span class="label">3. SOCIAL SECURITY NO.</span>
                    <span class="value">{ssn}</span>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <span class="label">4.a. GRADE, RATE OR RANK</span>
                    <span class="value">E-4</span>
                </div>
                <div class="col">
                    <span class="label">4.b. PAY GRADE</span>
                    <span class="value">CPL</span>
                </div>
                <div class="col">
                    <span class="label">5. DATE OF BIRTH</span>
                    <span class="value">{fmt_dob}</span>
                </div>
            </div>
            
            <div class="row">
                <div class="col">
                    <span class="label">6. RESERVE OBLIG. TERM. DATE</span>
                    <span class="value">N/A</span>
                </div>
                <div class="col" style="flex: 2">
                    <span class="label">7.a. PLACE OF ENTRY INTO ACTIVE DUTY</span>
                    <span class="value">MEPS, USA</span>
                </div>
                <div class="col">
                    <span class="label">7.b. HOME OF RECORD AT TIME OF ENTRY</span>
                    <span class="value">PENNSYLVANIA</span>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <span class="label">8.a. LAST DUTY ASSIGNMENT AND MAJOR COMMAND</span>
                    <span class="value">HHC 1-10 IN BN</span>
                </div>
                <div class="col">
                    <span class="label">8.b. STATION WHERE SEPARATED</span>
                    <span class="value">FORT BENNING, GA</span>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <span class="label">9. COMMAND TO WHICH TRANSFERRED</span>
                    <span class="value">US ARMY RESERVE CONTROL GROUP</span>
                </div>
                <div class="col">
                    <span class="label">10. SGLI COVERAGE</span>
                    <span class="value">NONE</span>
                </div>
            </div>
            
            <div style="border-bottom: 1px solid black; background: #eee; font-size: 10px; padding: 2px; text-align: center; font-weight: bold;">
                12. RECORD OF SERVICE
            </div>
            <div class="row">
                <div class="col" style="flex: 3"><span class="label">Title</span></div>
                <div class="col"><span class="label">Year(s)</span></div>
                <div class="col"><span class="label">Month(s)</span></div>
                <div class="col"><span class="label">Day(s)</span></div>
            </div>
            <div class="row">
                <div class="col" style="flex: 3"><span class="label">a. Date Entered AD This Period</span><span class="value">{fmt_entry}</span></div>
                <div class="col"><span class="value">00</span></div>
                <div class="col"><span class="value">00</span></div>
                <div class="col"><span class="value">00</span></div>
            </div>
            <div class="row">
                <div class="col" style="flex: 3"><span class="label">b. Separation Date This Period</span><span class="value">{fmt_discharge}</span></div>
                <div class="col"><span class="value">04</span></div>
                <div class="col"><span class="value">00</span></div>
                <div class="col"><span class="value">00</span></div>
            </div>

            <div class="row" style="height: 100px;">
                <div class="col">
                    <span class="label">13. DECORATIONS, MEDALS, BADGES, CITATIONS AND CAMPAIGN RIBBONS AWARDED OR AUTHORIZED</span>
                    <span class="value">NATIONAL DEFENSE SERVICE MEDAL // GLOBAL WAR ON TERRORISM SERVICE MEDAL // ARMY SERVICE RIBBON // END OF ITEM</span>
                </div>
            </div>
            
            <div class="row" style="height: 50px;">
                <div class="col">
                    <span class="label">23. TYPE OF SEPARATION</span>
                    <span class="value">DISCHARGE</span>
                </div>
                 <div class="col">
                    <span class="label">24. CHARACTER OF SERVICE</span>
                    <span class="value">HONORABLE</span>
                </div>
            </div>

            <div class="footer">
                DD FORM 214, AUG 2009 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; PREVIOUS EDITIONS ARE OBSOLETE.
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_image(first_name, last_name, discharge_date, branch='ARMY'):
    """Render HTML ke PNG"""
    try:
        from playwright.sync_api import sync_playwright
        
        html_content = generate_html(first_name, last_name, discharge_date, branch)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1000, 'height': 1200})
            page.set_content(html_content, wait_until='load')
            screenshot_bytes = page.screenshot(type='png', full_page=True)
            browser.close()
            
        return screenshot_bytes
    except Exception as e:
        raise Exception(f"Gagal generate dokumen: {str(e)}")