from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_hotel(page, kota):
    page.goto("https://www.traveloka.com/id-id/hotel")
    time.sleep(4)

    page.wait_for_selector('input[data-testid="autocomplete-field"]')
    page.click('input[data-testid="autocomplete-field"]')
    page.fill('input[data-testid="autocomplete-field"]', "")
    page.type('input[data-testid="autocomplete-field"]', kota, delay=100)
    time.sleep(3)

    page.wait_for_selector('[data-testid="accom_autocomplete_item_0"]')
    page.click('[data-testid="accom_autocomplete_item_0"]')
    time.sleep(2)

    page.wait_for_selector('[data-testid="search-submit-button"]')
    page.click('[data-testid="search-submit-button"]')
    print(f"Menunggu halaman hasil {kota}...")
    time.sleep(8)

    try:
        page.wait_for_selector('[data-testid="tvat-searchListItem"]', timeout=15000)
    except:
        print(f"Tidak ada hasil untuk {kota}")
        return []

    try:
        page.wait_for_selector('[data-testid="STAR4"]', timeout=5000)
        page.click('[data-testid="STAR4"]')
        time.sleep(4)
    except:
        print(f"Filter bintang tidak ditemukan untuk {kota}")

    prev_count = 0
    for i in range(20):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        current_count = page.locator('[data-testid="tvat-searchListItem"]').count()
        print(f"  [{kota}] Hotel ter-load: {current_count}")
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
            "Area Pencarian": kota
        })

    print(f"  [{kota}] Ditemukan {len(hotels)} hotel bintang 4")
    return hotels

def scrape_semua_area():
    area_semarang = [
        "Semarang Utara",
        "Semarang Tengah",
        "Semarang Selatan",
        "Semarang Barat",
        "Semarang Timur",
        "Semarang"
    ]

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

        # Sembunyikan tanda-tanda bot
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['id-ID', 'id', 'en-US']});
        """)

        for area in area_semarang:
            print(f"\n=== Scraping {area} ===")
            hotels = scrape_hotel(page, area)
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
