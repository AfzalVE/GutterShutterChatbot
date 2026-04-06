from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

visited = set()
data = []

# 🔁 Your website
BASE_URL = "https://www.guttershutterofthetriangle.com/"

def is_valid_url(url):
    return urlparse(url).netloc == urlparse(BASE_URL).netloc

# ✅ Setup Selenium
options = Options()
options.add_argument("--headless")  # remove this line if you want to see browser
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def scrape_page(url):
    if url in visited:
        return

    print(f"Scraping: {url}")
    visited.add(url)

    try:
        driver.get(url)
        time.sleep(3)  # wait for JS to load

        soup = BeautifulSoup(driver.page_source, "html.parser")

        page_data = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "headings": [],
            "paragraphs": []
        }

        # 📌 Extract headings
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text:
                    page_data["headings"].append(text)

        # 📌 Extract paragraphs
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                page_data["paragraphs"].append(text)

        data.append(page_data)

        # 🔗 Find internal links
        for link in soup.find_all("a", href=True):
            next_url = urljoin(BASE_URL, link["href"])

            if is_valid_url(next_url) and next_url not in visited:
                scrape_page(next_url)

        time.sleep(1)

    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")


# 🚀 Start scraping
scrape_page(BASE_URL)

# 💾 Save data
with open("website_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

driver.quit()

print("\n✅ Scraping complete! Data saved to website_data.json")
print(f"📊 Total pages scraped: {len(data)}")