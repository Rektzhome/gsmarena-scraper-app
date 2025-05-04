import asyncio
import json
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def scrape_gsmarena(query):
    """
    Scrapes phone details from GSMArena based on a search query using Playwright.

    Args:
        query (str): The search query (e.g., "Xiaomi Redmi 10 2022").

    Returns:
        dict: A dictionary containing phone details, or an error message.
    """
    print(f"Starting scrape for: \"{query}\"") # Added print for Flask console logging
    try:
        async with async_playwright() as p:
            # Using --no-sandbox is often necessary in containerized environments
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()

            # --- Search for the phone ---
            search_url = f"https://www.gsmarena.com/res.php3?sSearch={query.replace(' ', '+')}"
            print(f"Navigating to search URL: {search_url}")
            await page.goto(search_url, wait_until='domcontentloaded') # Wait for DOM content

            search_results_selector = "div.makers ul li a"
            try:
                # Wait for the first link within the results container
                await page.wait_for_selector(search_results_selector, timeout=15000)
            except PlaywrightTimeoutError:
                await browser.close()
                print(f"Search results timeout or no results for query: \"{query}\"")
                return {"error": f"Search results took too long to load or no results found for query: \"{query}\"."}

            first_result_link_element = page.locator(search_results_selector).first
            first_result_title = await first_result_link_element.text_content()
            first_result_link = await first_result_link_element.get_attribute("href")

            if not first_result_link:
                await browser.close()
                print(f"No phone link found for query: \"{query}\"")
                return {"error": f"No phone found or link extraction failed for query: \"{query}\". Please try a different query."}

            # Construct absolute URL
            phone_detail_url = first_result_link
            if not phone_detail_url.startswith('http'):
                base_url = 'https://www.gsmarena.com/'
                phone_detail_url = base_url + phone_detail_url.lstrip('/')

            print(f"Found \"{first_result_title.strip()}\". Navigating to details page: {phone_detail_url}")

            # --- Get phone details ---
            await page.goto(phone_detail_url, wait_until='domcontentloaded')

            specs_list_selector = "#specs-list"
            try:
                await page.wait_for_selector(specs_list_selector, timeout=10000)
            except PlaywrightTimeoutError:
                await browser.close()
                print(f"Details page timeout or specs list not found for: \"{first_result_title.strip()}\"")
                return {"error": f"Details page took too long to load or specs list not found for: \"{first_result_title.strip()}\"."}

            phone_details = {}

            # Get Phone Name
            phone_name_element = page.locator("h1.specs-phone-name-title")
            if await phone_name_element.count() > 0:
                phone_details["Phone Name"] = (await phone_name_element.text_content()).strip()
            else:
                phone_details["Phone Name"] = first_result_title.strip() # Fallback to search result title

            # Get Image URL
            image_element = page.locator(".specs-photo-main a img")
            if await image_element.count() > 0:
                img_src = await image_element.get_attribute("src")
                if img_src:
                    if not img_src.startswith('http'):
                        base_url = 'https://www.gsmarena.com/' # Base URL might differ for images, but usually same domain
                        img_src = base_url + img_src.lstrip('/')
                    phone_details["Image URL"] = img_src

            # Get Specs Table
            specs_list_container = await page.query_selector(specs_list_selector)
            if specs_list_container:
                tables = await specs_list_container.query_selector_all("table")
                for table in tables:
                    category_element = await table.query_selector("th")
                    if not category_element: continue
                    category = (await category_element.text_content()).strip()
                    if not category: continue

                    phone_details[category] = {}
                    rows = await table.query_selector_all("tr")
                    for tr in rows:
                        key_element = await tr.query_selector("td.ttl") # Corrected selector
                        value_element = await tr.query_selector("td.nfo") # Corrected selector
                        if key_element and value_element:
                            key = (await key_element.text_content()).strip()
                            value = (await value_element.text_content()).strip()
                            if key and value:
                                phone_details[category][key] = value
                    if not phone_details[category]: # Remove empty categories
                        del phone_details[category]
            else:
                print(f"Warning: Specs list container ({specs_list_selector}) not found.")

            await browser.close()
            print(f"Scraping successful for: \"{query}\"")
            return phone_details

    except PlaywrightTimeoutError as e:
        print(f"A Playwright timeout error occurred: {e}")
        # Ensure browser is closed in case of timeout during navigation/waiting
        if 'browser' in locals() and await browser.is_connected():
            await browser.close()
        return {"error": f"Scraping process timed out. Query: \"{query}\". Error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        # Ensure browser is closed in case of other errors
        if 'browser' in locals() and await browser.is_connected():
            await browser.close()
        return {"error": f"Scraping process failed: {e}. Query: \"{query}\""}

# Removed the main execution block (if __name__ == "__main__")

