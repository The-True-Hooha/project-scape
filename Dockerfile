FROM python:3.12-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    cron \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser
RUN playwright install chromium --with-deps

# Copy app files
COPY . /app/

# Create directory for images
RUN mkdir -p /app/images

# Setup cron job
RUN echo "0 8 * * * cd /app && python main.py > /app/cron.log 2>&1" > /app/crontab
RUN crontab /app/crontab

# Create entrypoint
RUN echo '#!/bin/bash\nservice cron start\necho "Scheduler started!"\ntail -f /app/cron.log' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]