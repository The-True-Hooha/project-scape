import os
import random
import asyncio
from datetime import datetime
from pathlib import Path
from instagrapi import Client


async def post_images(username: str, password: str, base_dir: str, credits: str):
    loop = asyncio.get_event_loop()

    client = Client()
    try:
        print(f"Logging into the account")

        await loop.run_in_executor(
            None, lambda: client.login(username=username, password=password)
        )
        print("login success")
    except Exception as e:
        print(f"Failed to login: {e}")
        return []

    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = os.path.join(base_dir, today)

    if not os.path.exists(today_dir):
        print(f"No images found for today ({today_dir})")
        return []

    all_image_files = [f for f in os.listdir(today_dir) if f.endswith('.jpg') and not f.startswith('debug')]
    posted_files = [f.replace('.posted', '') for f in os.listdir(today_dir) if f.endswith('.posted')]
    unposted_images = [img for img in all_image_files if img not in posted_files]

    if not unposted_images:
        print("All images have been posted already")
        return []

    print(f"Found {len(unposted_images)} unposted images")

    
    batches = []
    for i in range(0, len(unposted_images), 3):
        batch = unposted_images[i:i+3]
        batches.append(batch)

    successful_posts = []

    
    hashtags = "#fashion #style #photography #model #instagood #photooftheday #beautiful #art #instagram #photo #beauty #like #follow #picoftheday #portrait #photoshoot #instadaily #photographer #love #fashionblogger"

    for batch_number, batch in enumerate(batches):
        batch_paths = [os.path.join(today_dir, img) for img in batch]

        valid_paths = []
        for path in batch_paths:
            if os.path.exists(path) and os.access(path, os.R_OK):
                file_size = os.path.getsize(path)
                if file_size < 100:
                    print(f"Warning: Image {path} is very small ({file_size} bytes), skipping")
                    continue
                valid_paths.append(path)
            else:
                print(f"Warning: Cannot access image at {path}")

        if not valid_paths:
            print(f"No valid images in batch {batch_number+1}, skipping")
            continue

        caption = f"Check out these amazing photos from @{credits} 🔥\n\nBatch {batch_number+1}/{len(batches)}\n\n{hashtags}"

        try:
            if len(valid_paths) == 1:
                print(f"Posting single image from batch {batch_number+1}")

                media = await loop.run_in_executor(
                    None, lambda: client.photo_upload(valid_paths[0], caption)
                )
            else:
                print(
                    f"Posting carousel with {len(valid_paths)} images (batch {batch_number+1})")
                media = await loop.run_in_executor(
                    None, lambda: client.album_upload(valid_paths, caption)
                )

            for img_path in valid_paths:
                Path(img_path + ".posted").touch()

            print(f"Successfully posted batch {batch_number+1} to Instagram! Media ID: {media.id}")
            successful_posts.append(media.id)

            if batch_number < len(batches) - 1:
                delay = random.randint(180, 300)
                print(f"Waiting {delay} seconds before next post...")
                await asyncio.sleep(delay)

        except Exception as e:
            print(f"Error posting batch {batch_number+1} to Instagram: {e}")

            if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():

                backoff_time = 15 * (2 ** min(batch_number, 4))
                print(
                    f"Rate limit detected, backing off for {backoff_time} minutes")
                await asyncio.sleep(backoff_time * 60)

                try:
                    if len(valid_paths) == 1:
                        media = await loop.run_in_executor(
                            None, lambda: client.photo_upload(
                                valid_paths[0], caption)
                        )
                    else:
                        media = await loop.run_in_executor(
                            None, lambda: client.album_upload(
                                valid_paths, caption)
                        )

                    for img_path in valid_paths:
                        Path(img_path + ".posted").touch()

                    print(f"Successfully posted batch {batch_number+1} after retry!")
                    successful_posts.append(media.id)
                except Exception as retry_error:
                    print(f"Retry also failed: {retry_error}")

    print(f"Posted {len(successful_posts)} batches out of {len(batches)}")

    session_file = f"{username}_session.json"
    client.dump_settings(session_file)

    return successful_posts