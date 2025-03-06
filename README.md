# Project Scape

An automated tool that scrapes images from X (Twitter) profiles and reposts them to Instagram as carousels.

## Overview

This project automates the process of:

1. Scraping images from specific X (Twitter) accounts
2. Saving them with proper organization
3. Posting them to Instagram as carousel posts (in groups of 3)
4. Tracking which images have been posted to avoid duplicates

The system runs on a scheduled basis and can be deployed as a containerized application.

## Features

- **X/Twitter Scraping**:
  - Extracts full-resolution images from specified profiles
  - Uses Playwright for reliable browser automation
  - Handles scrolling and media extraction with proper error recovery

- **Image Organization**:
  - Saves images in dated folders (YYYY-MM-DD)
  - Tracks which images have been posted
  - Avoids duplicates across runs

- **Instagram Posting**:
  - Automatically posts images as carousels
  - Credits original creators
  - Handles rate limits with exponential backoff
  - Posts images in batches with appropriate delays
  - Includes relevant hashtags for better visibility

- **Deployment**:
  - Docker containerization for easy deployment
  - Scheduled execution using cron
  - Persistent storage for images

## Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- X (Twitter) account to scrape
- Instagram account for posting

## Installation

### Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/The-True-Hooha/project-scape
   cd project-scape
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Create a `.env` file with your credentials:

   ```bash
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```

### Docker Setup

1. Build the Docker image:

   ```bash
   docker build -t project-scape .
   ```

2. Run the container:

   ```bash
   docker run -d --name twitter-scraper \
     -v ./images:/app/images \
     -e INSTAGRAM_USERNAME=your_instagram_username \
     -e INSTAGRAM_PASSWORD=your_instagram_password \
     project-scape
   ```

## Usage

### Configuration

Edit the `main.py` file to set up your target X profiles and other parameters:

```python
# Example configuration
X_USERNAMES = ["egeberkina"]  # Twitter accounts to scrape
MAX_IMAGES = 30               # Maximum images to scrape per account
BASE_DIR = "images"           # Base directory for storage
INSTAGRAM_CREDITS = "egeberkina"  # Account to credit in posts
```

### Running Manually

```bash
python main.py
```

### Scheduled Execution

The Docker container includes a cron job that runs daily at 8:00 AM UTC. You can modify the schedule in the Dockerfile.

## Project Structure

```bash
project-scape/
├── main.py                # Main entry point
├── actions/               # Core functionality
│   ├── twitter_action.py  # X/Twitter scraping logic
│   └── instagram_action.py# Instagram posting logic
├── Dockerfile             # Container definition
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
└── images/                # Storage for scraped images
    └── YYYY-MM-DD/        # Date-organized folders
```

## Important Notes

- **Account Safety**: Automation of Instagram actions can risk account suspension. Use with caution.
- **Rate Limits**: The code includes delays to respect rate limits, don't remove these.
- **Terms of Service**: Be aware that this project operates in a gray area of X and Instagram's Terms of Service.
- **Attribution**: Do well to mention me when if that works

## Customization

You can customize the posting schedule, caption text, hashtags, and other parameters in the code.

## License

MIT License

## Disclaimer

This project is for educational purposes only. Use at your own risk and responsibility.
