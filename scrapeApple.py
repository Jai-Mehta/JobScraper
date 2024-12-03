import csv
import json
from time import time, sleep
from datetime import datetime
from random import randint
from requests import get
from warnings import warn


def get_all_jobs(pages, existing_jobs):
    requests = 0
    start_time = time()
    total_runtime = datetime.now()
    today = datetime.now().date()

    for page in pages:
        response = get('https://jobs.apple.com/api/v1/search/page?location=seattle-SEA'
                       '%20los-angeles-metro-area-LAMETRO%20san-francisco-bay-area-SFMETRO'
                       '%20south-san-francisco-SSF%20san-diego-SDO&page={}'.format(page))

        # Monitor the frequency of requests
        requests += 1
        sleep(randint(8, 15))  # Pause to avoid being rate-limited
        current_time = time()
        elapsed_time = current_time - start_time
        print(f"Apple Request:{requests}; Frequency: {requests / elapsed_time:.2f} req/s; Total Run Time: {datetime.now() - total_runtime}")

        if response.status_code != 200:
            warn(f"Request: {requests}; Status code: {response.status_code}")

        if requests > 10:
            warn("Number of requests exceeded the limit.")
            break

        yield from get_job_infos(response, today, existing_jobs)


def get_job_infos(response, today, existing_jobs):
    apple_jobs = json.loads(response.text)
    for website in apple_jobs['searchResults']:
        site = 'Apple'
        title = website['postingTitle']
        location = website['locations'][0]['name']
        job_link = 'https://jobs.apple.com/en-us/details/' + website['positionId']

        # Parse the date using the correct format
        posted_date = datetime.strptime(website['postingDate'], "%b %d, %Y").date()

        # Only consider jobs posted today and avoid duplicates
        if posted_date == today and job_link not in existing_jobs:
            yield site, title, location, job_link, posted_date, "No"  # Default Notify value: "No"


def load_existing_jobs(csv_file):
    """Load existing job links from the CSV file."""
    existing_jobs = set()
    try:
        with open(csv_file, 'r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_jobs.add(row['Job URL'])  # Use Job URL as a unique identifier
    except FileNotFoundError:
        print(f"{csv_file} not found. Starting fresh.")
    return existing_jobs


# def save_jobs_to_csv(csv_file, jobs):
#     """Append new jobs to the CSV file."""
#     with open(csv_file, 'a', newline='', encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerows(jobs)
def save_jobs_to_csv(csv_file, jobs):
    """Append only new jobs to the CSV file."""
    existing_jobs = load_existing_jobs(csv_file)  # Load existing job links to avoid duplicates
    with open(csv_file, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        for job in jobs:
            # Append job only if it's not in existing jobs
            if job[3] not in existing_jobs:  # Job URL is the unique identifier (job[3] is job_link)
                writer.writerow(job)



def main():
    csv_file = 'apple_jobs_today.csv'
    pages = [str(i) for i in range(1, 108)]

    # Load existing jobs
    existing_jobs = load_existing_jobs(csv_file)

    # Get new jobs and avoid duplicates
    new_jobs = list(get_all_jobs(pages, existing_jobs))

    if new_jobs:
        # Write headers if the file is new
        try:
            with open(csv_file, 'r', encoding="utf-8") as file:
                pass
        except FileNotFoundError:
            with open(csv_file, 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Website", "Title", "Location", "Job URL", "Posted Date", "Notify"])  # Header

        # Save new jobs
        save_jobs_to_csv(csv_file, new_jobs)
        print(f"Added {len(new_jobs)} new jobs to {csv_file}.")
    else:
        print("No new jobs found.")


if __name__ == "__main__":
    main()

