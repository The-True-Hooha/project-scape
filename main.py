import asyncio
import http.server
import socketserver
import threading

from actions.twitter_action import scrape_x_images

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


async def main():
    
    username = "egeberkina"
    max_images = 10
    base_dir = "images"

    downloaded_images = await scrape_x_images(
        username=username,
        max_images=max_images,
        base_dir=base_dir
    )
    print(f"Total images downloaded: {len(downloaded_images)}")


async def get_only_new_images(username, max_images=20):
    # Get the list of all filenames in today's directory
    today = datetime.now().strftime('%Y-%m-%d')
    user_dir = os.path.join("scraped-images", username, today)

    # Get list of existing files (will be empty if no folder yet)
    existing_files = []
    if os.path.exists(user_dir):
        existing_files = os.listdir(user_dir)

    existing_media_ids = [os.path.splitext(f)[0] for f in existing_files]

    # Run the scraper but download only files with IDs not in our list
    return await scrape_x_images(username, max_images, "images",existing_media_ids)


if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    asyncio.run(main())