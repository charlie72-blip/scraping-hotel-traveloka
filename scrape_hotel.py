from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta

# Generate tanggal otomatis (hari ini dan besok)
today = datetime.now()
tomorrow = today + timedelta(days=1)
checkin = today.strftime("%d-%m-%Y")
checkout = tomorrow.strftime("%d-%m-%Y")

AREA_URLS = {
    "Semarang Timur": f"https://www.traveloka.com/id-id/hotel/search?spec={checkin}.{checkout}.1.1.HOTEL_GEO.106587.Semarang.2&basicFilters=STAR_RATING-STAR4",
    "Semarang Utara": f"https://www.traveloka.com/id-id/hotel/search?spec={checkin}.{checkout}.1.1.HOTEL_GEO.106597.Semarang%20Utara.2&basicFilters=STAR_RATING-STAR4",
    "Semarang Tengah": f"https://www.traveloka.com/id-id/hotel/search?spec={checkin}.{checkout}.1.1.HOTEL_GEO.106592.Semarang%20Tengah.2&basicFilters=STAR_RATING-STAR4",
    "Semarang Selatan": f"https://www.traveloka.com/id-id/hotel/search?spec={checkin}.{checkout}.1.1.HOTEL_GEO.106603.Semarang%20Selatan.2&basicFilters=STAR_RATING-STAR4",
    "Semarang Barat": f"https://www.traveloka.com/id-id/hotel/search?spec={checkin}.{checkout}.1.1.HOTEL_GEO.106588.Semarang%20Barat.2&basicFilters=STAR_RATING-STAR4",
}

def scrape_hotel(page, area, url):
    print(f"\n=== Scraping {area} ===")
    page.goto(url)
    print(f"Menunggu halaman hasil {area}...")
    time.sleep(8)

    try:
        page.wait_for_selector('[data-testid="tvat-searchListItem"]', timeout=15000)
        print(f"Halaman berhasil load!")
    except:
        print(f"Tidak ada hasil untuk {area}")
        return []

    # Scroll sampai semua hotel ter-load
    prev_count = 0
    for i in range(20):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        current_count = page.locator('[data-testid="tvat-searchListItem"]').count()
        print(f"  [{area}] Hotel ter-load: {current_count}")
        if current_count == prev_count:
            break
        prev_count = current_count

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    hotels = []
    items = soup.find_all("div", attrs={"data-testid": "tvat-searchListItem"})

    for item in items:
        nama = item.find(attrs={"data-testid": "tvat-hotelName"})
        harga = item.find(attrs={"data-testid": "tvat-hotelPrice"})
        rating = item.find(attrs={"data-testid": "tvat-ratingScore"})
        lokasi = item.find(attrs={"data-testid": "tvat-hotelLocation"})

        hotels.append({
            "Nama Hotel": nama.text.strip() if nama else "N/A",
            "Harga": harga.text.strip() if harga else "N/A",
            "Rating": rating.text.strip() if rating else "N/A",
            "Lokasi": lokasi.text.strip() if lokasi else "N/A",
            "Area Pencarian": area
        })

    print(f"  [{area}] Ditemukan {len(hotels)} hotel bintang 4")
    return hotels

def scrape_semua_area():
    semua_hotel = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['id-ID', 'id', 'en-US']});
        """)

        for area, url in AREA_URLS.items():
            hotels = scrape_hotel(page, area, url)
            semua_hotel.extend(hotels)
            time.sleep(3)

        browser.close()

    df = pd.DataFrame(semua_hotel)
    if not df.empty:
        df = df.drop_duplicates(subset=["Nama Hotel"])
    df.to_csv("hotel_bintang4_semarang_lengkap.csv", index=False)
    print(f"\n✅ Total {len(df)} hotel unik tersimpan di hotel_bintang4_semarang_lengkap.csv")
    print(df)

scrape_semua_area()
