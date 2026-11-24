# Scraping Hotel Traveloka

Script Python untuk mengambil data hotel bintang 4 dari Traveloka per area (Semarang Timur, Utara, Tengah, Selatan, Barat), dengan tanggal check-in hari ini dan check-out besok. Hasilnya disimpan sebagai file CSV.

## Teknologi
Python, Playwright, BeautifulSoup, pandas, GitHub Actions.

## Cara menjalankan
```bash
pip install playwright beautifulsoup4 pandas
playwright install chromium
python scrape_hotel.py
```

## Otomatisasi
Workflow GitHub Actions (`.github/workflows/scrape.yml`) menjalankan scraper setiap hari pukul 01.00 UTC.

## Contoh hasil
`hotel_bintang4_semarang.csv`, `hotel_bintang4_semarang_lengkap.csv`, `hotel_bintang4_jakarta.csv`, `hotel_jakarta.csv`.
