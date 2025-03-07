import asyncio
import http.server
import socketserver
import threading
import os
from dotenv import load_dotenv

from actions.twitter_action import scrape_x_images
from actions.instagram_action import post_images

load_dotenv()

def run_http_server():
    class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
                return
            http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    PORT = int(os.environ.get('PORT', 8080))
    handler = HealthCheckHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving health check at port {PORT}")
    httpd.serve_forever()


async def get_only_new_images(username, max_images=20, base_dir="images"):
    today = datetime.now().strftime('%Y-%m-%d')
    user_dir = os.path.join(base_dir, today)

    existing_files = []
    if os.path.exists(user_dir):
        existing_files = os.listdir(user_dir)

    existing_media_ids = [os.path.splitext(f)[0] for f in existing_files]
    return await scrape_x_images(username, max_images, base_dir, existing_media_ids)


async def main():
    X_USERNAME = "egeberkina"
    MAX_IMAGES = 10
    BASE_DIR = "images"

    INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        print("Instagram credentials not found in environment variables")
        return

    print(f"Starting scrape from X account: {X_USERNAME}")
    downloaded_images = await scrape_x_images(
        username=X_USERNAME,
        max_images=MAX_IMAGES,
        base_dir=BASE_DIR
    )
    print(f"Total images downloaded: {len(downloaded_images)}")

    if downloaded_images:
        print(f"Starting to post images to Instagram as @{INSTAGRAM_USERNAME}")
        posted_media = await post_images(
            username=INSTAGRAM_USERNAME,
            password=INSTAGRAM_PASSWORD,
            base_dir=BASE_DIR,
            credits=X_USERNAME
        )
        print(f"Posted {len(posted_media)} batches to Instagram")
    else:
        print("No new images to post to Instagram")

if __name__ == "__main__":

    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()

    asyncio.run(main())
