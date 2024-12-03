import csv
import asyncio
import os
from telegram import Bot
import nest_asyncio

# Apply nest_asyncio to allow nested event loops in environments like Jupyter
nest_asyncio.apply()

# Use environment variables for Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_telegram_message(bot, message):
    """Send a message via Telegram asynchronously."""
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def process_jobs(csv_file):
    """Process jobs from the CSV file and send Telegram messages for new jobs."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    jobs = []

    # Read jobs from the CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Notify'] == "No":  # Only process jobs not yet notified
                jobs.append(row)

    # Notify and update the Notify column
    for job in jobs:
        company = job['Website']
        title = job['Title']
        location = job['Location']
        job_link = job['Job URL']
        posted_date = job['Posted Date']

        # Prepare and send Telegram message
        message = (
            f"Company: {company}\n"
            f"Job Title: {title}\n"
            f"Location: {location}\n"
            f"Job Link: {job_link}\n"
            f"Posted Date: {posted_date}"
        )
        await send_telegram_message(bot, message)

        # Update the Notify status in the CSV file
        job['Notify'] = "Yes"

    # Rewrite the CSV file with updated Notify values
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['Website', 'Title', 'Location', 'Job URL', 'Posted Date', 'Notify']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

        print(f"Sent notifications for {len(jobs)} new jobs.")

def main():
    csv_file = 'apple_jobs_today.csv'
    asyncio.run(process_jobs(csv_file))

if __name__ == "__main__":
    main()
