# ChatGPT Sertifikasi Militer SheerID – Alur Verifikasi

## 📋 Ringkasan

Proses sertifikasi militer ChatGPT berbeda dengan sertifikasi pelajar/guru biasa.
Diperlukan pemanggilan endpoint tambahan terlebih dahulu untuk mengumpulkan informasi status militer, kemudian baru mengirim formulir informasi pribadi.

## 🔄 Alur Sertifikasi

### Langkah Pertama: Mengumpulkan Status Militer (collectMilitaryStatus)

Sebelum mengirim formulir informasi pribadi, endpoint ini harus dipanggil terlebih dahulu untuk menetapkan status militer.

Informasi Permintaan:
- URL: https://services.sheerid.com/rest/v2/verification/{verificationId}/step/collectMilitaryStatus
- Metode: POST
- Parameter:
{
    "status": "VETERAN" // total ada 3 status
}

Contoh Respons:

```json
{
    "verificationId": "{verification_id}",
    "currentStep": "collectInactiveMilitaryPersonalInfo",
    "errorIds": [],
    "segment": "military",
    "subSegment": "veteran",
    "locale": "en-US",
    "country": null,
    "created": 1766539517800,
    "updated": 1766540141435,
    "submissionUrl": "https://services.sheerid.com/rest/v2/verification/{verification_id}/step/collectInactiveMilitaryPersonalInfo",
    "instantMatchAttempts": 0
}
```

Field Kunci:
- submissionUrl: URL pengiriman yang akan digunakan pada langkah berikutnya
- currentStep: Tahapan saat ini, seharusnya berubah menjadi collectInactiveMilitaryPersonalInfo

---

### Langkah Kedua: Mengumpulkan Informasi Pribadi Militer Non-Aktif (collectInactiveMilitaryPersonalInfo)

Gunakan submissionUrl yang dikembalikan pada langkah pertama untuk mengirim informasi pribadi.

Informasi Permintaan:
- URL: Diambil dari submissionUrl pada respons langkah pertama
  Contoh: https://services.sheerid.com/rest/v2/verification/{verificationId}/step/collectInactiveMilitaryPersonalInfo
- Metode: POST
- Parameter:

```json
{
    "firstName": "nama",
    "lastName": "nama",
    "birthDate": "1939-12-01",
    "email": "email_kamu",
    "phoneNumber": "",
    "organization": {
        "id": 4070,
        "name": "Army"
    },
    "dischargeDate": "2025-05-29",
    "locale": "en-US",
    "country": "US",
    "metadata": {
        "marketConsentValue": false,
        "refererUrl": "",
        "verificationId": "",
        "flags": "{\"doc-upload-considerations\":\"default\",\"doc-upload-may24\":\"default\",\"doc-upload-redesign-use-legacy-message-keys\":false,\"docUpload-assertion-checklist\":\"default\",\"include-cvec-field-france-student\":\"not-labeled-optional\",\"org-search-overlay\":\"default\",\"org-selected-display\":\"default\"}",
        "submissionOptIn": "Dengan mengirimkan informasi pribadi di atas, saya menyatakan bahwa informasi pribadi saya dikumpulkan berdasarkan kebijakan privasi OpenAI dan saya memahami bahwa informasi pribadi saya akan dibagikan kepada SheerID sebagai pemroses / penyedia layanan pihak ketiga untuk memverifikasi kelayakan saya atas penawaran khusus. Untuk bantuan lebih lanjut, silakan hubungi OpenAI Support di support@openai.com"
    }
}
```

Penjelasan Field Kunci:
- firstName: Nama depan
- lastName: Nama belakang
- birthDate: Tanggal lahir, format YYYY-MM-DD
- email: Alamat email
- phoneNumber: Nomor telepon (boleh kosong)
- organization: Informasi organisasi militer
- dischargeDate: Tanggal keluar dinas / pensiun, format YYYY-MM-DD
- locale: Regional bahasa, default en-US
- country: Kode negara, default US
- metadata: Informasi metadata dan persetujuan kebijakan privasi

---

## 🎖️ Daftar Organisasi Militer (Organization)

```json
[
    {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    },
    {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY",
        "latitude": 39.7837304,
        "longitude": -100.445882
    }
]
```

Pemetaan ID Organisasi:
- 4070 - Army (Angkatan Darat)
- 4073 - Air Force (Angkatan Udara)
- 4072 - Navy (Angkatan Laut)
- 4071 - Marine Corps (Korps Marinir)
- 4074 - Coast Guard (Penjaga Pantai)
- 4544268 - Space Force (Angkatan Luar Angkasa)

---

## 🔑 Poin Implementasi

1. Harus dijalankan secara berurutan: collectMilitaryStatus lalu collectInactiveMilitaryPersonalInfo
2. Organization wajib berisi id dan name
3. Format tanggal wajib YYYY-MM-DD
4. Metadata submissionOptIn wajib disertakan

---

## 📝 Fitur yang Akan Diimplementasikan

- Implementasi pemanggilan endpoint collectMilitaryStatus
- Implementasi pemanggilan endpoint collectInactiveMilitaryPersonalInfo
- Logika pemilihan organisasi militer
- Pembuatan informasi pribadi (nama, tanggal lahir, email)
- Pembuatan tanggal keluar dinas yang masuk akal
- Penanganan metadata
- Integrasi ke sistem perintah utama bot (misalnya /verify6)
