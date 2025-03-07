import asyncio
from playwright.async_api import async_playwright, Response
import os
import aiohttp
import re
import requests
from datetime import datetime
import json
import time

async def scrape_x_images(username:str, max_images: int, base_dir:str):
    """
    scrape images from x profile
    """
    
    image_urls = set()
    _xhr_calls = []

    today = datetime.now().strftime('%Y-%m-%d')
    save_dir = os.path.join(base_dir, today)
    os.makedirs(save_dir, exist_ok=True)

    def intercept_response(response):
        """Capture all API responses"""
        if response.request.resource_type == "xhr" and "UserMedia" in response.url:
            _xhr_calls.append(response)
        return response

    async with async_playwright() as pw:
        # TODO: set headless to true when done with debugging
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        #TODO: Add slow motion for debugging (remove in production)
        context.set_default_timeout(120000)

        page = await context.new_page()
        page.on("response", intercept_response)

        try:
            profile_url = f"https://x.com/{username}/media"
            print(f"Navigating to {profile_url}")
            await page.goto(profile_url, wait_until="domcontentloaded")

            login_prompt = await page.query_selector('div[aria-label="Sign in"]')
            if login_prompt:
                print("Detected login wall, trying to work around it...")
                # Sometimes clicking outside or pressing Escape helps
                await page.mouse.click(10, 10)
                await page.keyboard.press("Escape")
                await asyncio.sleep(2)

            try:
                await page.wait_for_selector("[data-testid='primaryColumn']", timeout=45000)
                print(f"Loaded profile: {username}")
            except Exception as e:
                print(f"Couldn't find primary column, but continuing anyway: {e}")

            print("Starting to scroll to find images...")
            last_height = await page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10

            while len(image_urls) < max_images and scroll_attempts < max_scroll_attempts:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)

                img_elements = await page.query_selector_all('img[src*="pbs.twimg.com/media"]')
                for img in img_elements:
                    src = await img.get_attribute('src')
                    if src and "pbs.twimg.com/media" in src:
                        if "?" in src:
                            full_res_url = re.sub(r'(https://pbs.twimg.com/media/.+?)\?.*', r'\1?format=jpg&name=orig', src)
                    else:
                        full_res_url = f"{src}?format=jpg&name=orig"
                    image_urls.add(full_res_url)

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height

                print(f"Found {len(image_urls)} images so far...")

                if len(image_urls) >= max_images:
                    break
                
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            await page.screenshot(path=os.path.join(save_dir, "debug_screenshot.png"))
            await browser.close()

    image_urls_list = list(image_urls)[:max_images]
    print(f"Total unique images found: {len(image_urls_list)}")

    downloaded_paths = []

    async def download_image(url, index):
        try:
            media_id = re.search(r'/media/([^?]+)', url).group(1)
            filename = f"{media_id}.jpg"
            filepath = os.path.join(save_dir, filename)

            # Check if file already exists before downloading
            if os.path.exists(filepath):
                print(f"Skipping existing file: {filepath}")
                return filepath

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()

                        with open(filepath, 'wb') as f:
                            f.write(content)

                        print(f"Downloaded: {filepath}")
                        return filepath
                    else:
                        print(f"Failed to download: {url}")
                        return None
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    semaphore = asyncio.Semaphore(5)

    async def bounded_download(url, index):
        async with semaphore:
            return await download_image(url, index)

    bounded_tasks = [bounded_download(url, i)for i, url in enumerate(image_urls_list)]
    results = await asyncio.gather(*bounded_tasks)

    downloaded_paths = [path for path in results if path]

    return downloaded_paths
