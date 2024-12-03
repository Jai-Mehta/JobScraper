import csv
import json
from time import time, sleep
from datetime import datetime
from random import randint
from requests import get
from warnings import warn
from IPython.core.display import clear_output


def get_all_jobs(pages):
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
        clear_output(wait=True)

        if response.status_code != 200:
            warn(f"Request: {requests}; Status code: {response.status_code}")

        if requests > 108:
            warn("Number of requests exceeded the limit.")
            break

        yield from get_job_infos(response, today)


def get_job_infos(response, today):
    apple_jobs = json.loads(response.text)
    for website in apple_jobs['searchResults']:
        site = 'Apple'
        title = website['postingTitle']
        location = website['locations'][0]['name']
        job_link = 'https://jobs.apple.com/en-us/details/' + website['positionId']

        # Parse the date using the correct format
        posted_date = datetime.strptime(website['postingDate'], "%b %d, %Y").date()

        # Only consider jobs posted today
        if posted_date == today:
            yield site, title, location, job_link, posted_date, "No"  # Default Notify value: "No"


def main():
    pages = [str(i) for i in range(1, 108)]

    # Open the CSV file in write mode (overwrites existing content)
    with open('apple_jobs_today.csv', "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Website", "Title", "Location", "Job URL", "Posted Date", "Notify"])  # Added "Notify" column
        writer.writerows(get_all_jobs(pages))


if __name__ == "__main__":
    main()
