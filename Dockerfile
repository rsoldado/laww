## List updater

# Use python as base image
FROM python:3.9-slim

# Copy all files
WORKDIR /usr/src/app
COPY crontab .
COPY laww.py .
COPY requirements.txt .
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y cron

# Configure and execute cron
COPY crontab /etc/cron.d/laww-cron
RUN chmod 0644 /etc/cron.d/laww-cron
RUN crontab /etc/cron.d/laww-cron
RUN touch /var/log/cron.log
CMD python /usr/src/app/laww.py && cron && tail -f /var/log/cron.log