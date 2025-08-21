"""
CapCut Template Scraper
----------------------
Scrapes template data from https://capcuttemplate.co.in/all-free-capcut-template/
Extracts: URLs, Titles, Paragraph Content, Template image, Video source, and Links.

Requirements:
- selenium
- beautifulsoup4
- chromedriver (or Brave browser, see below)

Usage:
1. Install requirements: pip install selenium beautifulsoup4
2. Download ChromeDriver and ensure it matches your browser version.
3. (Optional) To use Brave, set the brave_path variable to your Brave executable.
4. Run: python capcuttemplate_scraper_exportable.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

# Set to your Brave browser path or leave as None to use Chrome
brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Change if needed

BASE_URL = "https://capcuttemplate.co.in/all-free-capcut-template/"


def get_driver():
    options = Options()
    if os.path.exists(brave_path):
        options.binary_location = brave_path
    # Comment out headless if you want to see the browser
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver


def close_popups(driver, silent=False):
    # Try to close known popups (including Google vignette ads)
    time.sleep(2)
    closed_any = False
    try:
        close_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "dismiss-button"))
        )
        close_btn.click()
        if not silent:
            print("Popup closed by id.")
        time.sleep(0.5)
        closed_any = True
    except Exception:
        pass
    try:
        close_btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Close'], [id*='dismiss'], [class*='close'], svg[viewBox*='38 12.83']"))
        )
        close_btn.click()
        if not silent:
            print("Popup closed by generic selector.")
        time.sleep(0.5)
        closed_any = True
    except Exception:
        pass
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Close ad'], .close-button, .close")
                close_btn.click()
                if not silent:
                    print("Closed Google vignette ad.")
                driver.switch_to.default_content()
                time.sleep(0.5)
                closed_any = True
                break
            except Exception:
                driver.switch_to.default_content()
    except Exception:
        pass
    if not closed_any and not silent:
        if not hasattr(close_popups, 'warned'):
            print("No popup closed or none found.")
            close_popups.warned = True


def extract_templates(soup, limit=None):
    templates = []
    cards = soup.select('.pt-cv-content-item')
    print(f"Found {len(cards)} template cards with .pt-cv-content-item.")
    for i, card in enumerate(cards):
        if limit and i >= limit:
            break
        thumb_link = card.select_one('div.pt-cv-thumb-wrapper a.pt-cv-href-thumbnail')
        url = thumb_link['href'] if thumb_link and thumb_link.has_attr('href') else None
        img_elem = card.select_one('img.pt-cv-thumbnail')
        image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else None
        title_elem = card.select_one('h2.pt-cv-title a')
        title = title_elem.get_text(strip=True) if title_elem else None
        fallback_name = f"Template {i+1}"
        paragraph = None
        video_src = None
        extra_links = []
        print(f"Processing {i+1}/{len(cards)}: {title or fallback_name}")
        if url:
            try:
                if 'detail_driver' not in globals():
                    global detail_driver
                    detail_driver = get_driver()
                detail_driver.get(url)
                WebDriverWait(detail_driver, 5).until(
                    lambda d: d.find_elements(By.TAG_NAME, 'body')
                )
                close_popups(detail_driver, silent=True)
                try:
                    h1 = detail_driver.find_element(By.TAG_NAME, "h1")
                    title = h1.text.strip() if h1 and h1.text.strip() else title
                except Exception:
                    pass
                detail_soup = BeautifulSoup(detail_driver.page_source, "html.parser")
                para_elem = detail_soup.select_one(".elementor-widget-container p, .entry-content p")
                paragraph = para_elem.get_text(strip=True) if para_elem else paragraph
                video = detail_soup.find("video")
                if video and video.get("src"):
                    video_src = video["src"]
                for a2 in detail_soup.select("a"):
                    link = a2.get("href")
                    if link and ("capcut-yt.onelink.me" in link or "capcut://" in link):
                        extra_links.append(link)
            except Exception as e:
                print(f"Error loading detail page {url}: {e}")
        if not title:
            title = fallback_name
        templates.append({
            "title": title,
            "url": url,
            "paragraph": paragraph,
            "image": image_url,
            "video": video_src,
            "links": extra_links
        })
    if 'detail_driver' in globals():
        detail_driver.quit()
        del globals()['detail_driver']
    print(f"Finished processing {len(templates)} templates.")
    return templates


def scrape_capcut_templates(output_all_json=True, per_template_json=False, limit=None):
    driver = get_driver()
    driver.get(BASE_URL)
    close_popups(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    templates = extract_templates(soup, limit=limit)
    if output_all_json:
        with open("capcut_templates.json", "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        print(f"Saved all templates to capcut_templates.json ({len(templates)} templates)")
    if per_template_json:
        for template in templates:
            name = template["title"] or "template"
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
    return templates


if __name__ == "__main__":
    # For Colab or production, scrape all templates and output a single JSON file
    scrape_capcut_templates(output_all_json=True, per_template_json=False, limit=None)
