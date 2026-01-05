# Panduan Link Verifikasi YouTube Student

Link verifikasi YouTube sedikit berbeda dari link SheerID biasanya.
Contoh link asli dari YouTube:
`https://offers.sheerid.com/youtube/student/?yrdup=https%3A%2F%2Fwww.youtube.com...`

Link di atas **TIDAK** memuat `programId` dan `verificationId` yang dibutuhkan bot. Oleh karena itu, Anda perlu mengambilnya secara manual (Sniffing/Inspect).

### Cara Mengambil ID (Manual):

1. Buka Browser PC (Chrome/Edge) dan tekan `F12` (Developer Tools).
2. Masuk ke tab **Network**.
3. Lakukan proses verifikasi di halaman YouTube sampai loading.
4. Di kolom filter Network, cari kata kunci:
   `https://services.sheerid.com/rest/v2/verification/`
5. Klik request tersebut dan cari data berikut:
   * **programId**: Ada di dalam tab **Payload** (Request Body).
   * **verificationId**: Ada di dalam tab **Response**.

### Cara Menyusun Link untuk Bot:

Setelah mendapatkan kedua ID tersebut, susunlah link baru dengan format:

`https://services.sheerid.com/verify/[programId]/?verificationId=[verificationId]`

**Keterangan:**
* `[programId]` = ID Program yang Anda dapatkan dari Payload (biasanya `5f2066...`).
* `[verificationId]` = ID Verifikasi yang Anda dapatkan dari Response.

**Contoh Link Jadi:**
`https://services.sheerid.com/verify/5f20660609b7e716949359e9/?verificationId=67c8c14f5f17a83b745e3f82`

Gunakan link yang sudah disusun ini untuk perintah `/verify5`.