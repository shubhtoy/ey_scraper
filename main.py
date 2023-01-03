# Project: Ey Scraper
# Author: @shubhtoy
# Purpose: To scrape jobs from Ey's career page
# Python Version: 3.10.2


# Importing required libraries
import requests
from bs4 import BeautifulSoup
from lxml import etree
import math
from threading import Thread
import json

# Declaring global variables
scroll_url = "https://careers.ey.com/ey/search/?q=&sortColumn=referencedate&sortDirection=desc&optionsFacetsDD_country=IN&startrow={number}"
base_url = "https://careers.ey.com"

# Declaring file names
INVALID_JOBS_FILE = "error_jobs"
OUTFILE = "jobs"

# Declaring functions
def get_jobs(content, jobs_list):
    soup = BeautifulSoup(content, "html.parser")

    rows = soup.find_all("tr", class_="data-row")

    for row in rows:
        title_row = row.find("td", class_="colTitle").find("span", class_="jobTitle")
        title = title_row.text.strip()
        link = base_url + title_row.find("a")["href"]
        location = row.find("span", class_="jobLocation").text.strip()
        # print(title, link, location)
        # date = row.find("span", class_="jobDate").text.strip()
        jobs_list.append({"title": title, "link": link, "location": location})
    return


def update_jobs_list(job: dict, final_job_list: list):
    try:
        url = job["link"]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        no = soup.findAll("div", class_="joblayouttoken")
        other_sites = (
            no[2]
            .find("span", {"data-careersite-propertyid": "customfield3"})
            .text.strip()
        )
        # print(other_sites)
        # print(requisition_id)
        salary = no[3].find("span", {"lang": "en-US"}).text.strip()
        # print(designation)
        description = no[6].text.strip()
        requisition_id = (
            no[5]
            .find("span", {"data-careersite-propertyid": "customfield5"})
            .text.strip()
        )
        date = no[4].find("span", {"data-careersite-propertyid": "date"}).text.strip()

        # print(description)
        final_job_list.append(
            {
                "title": job["title"],
                "link": job["link"],
                "location": job["location"],
                "date": date,
                "requisition_id": requisition_id,
                "salary": salary,
                "description": description,
                "other_sites": other_sites,
            }
        )

    except Exception as e:
        print(e)

        update_jobs_list(job, final_job_list)
        # with open(f"{INVALID_JOBS_FILE}.txt", "a+") as f:
        #     f.write(f"{job['link']}\n")

    return
    # print(req_id.text.strip())


def get_total_jobs() -> list:
    resp = requests.get(scroll_url.format(number=0))
    soup = BeautifulSoup(resp.text, features="lxml")
    dom = etree.HTML(str(soup))
    no_of_pages = math.ceil(
        int(
            dom.xpath(
                '//*[@id="content"]/div/div[4]/div[1]/div/div/span[1]/b[2]/text()'
            )[0]
        )
        / 25
    )

    # print(no_of_pages)
    resp_list = []

    for i in range(0, no_of_pages):
        resp_list.append(requests.get(scroll_url.format(number=i * 25)).content)
        # break

    return resp_list


def to_json(data: list):

    new_dict = {}
    new_dict["Company"] = "Ey"
    new_dict[
        "Career Page"
    ] = "https://careers.ey.com/ey/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country=IN&optionsFacetsDD_customfield1=&optionsFacetsDD_customfield3="
    new_dict["Jobs"] = data

    with open(f"{OUTFILE}.json", "w") as f:
        json.dump(new_dict, f, indent=4)
    return new_dict


# Main function
def main():

    print("Starting Ey Scraper")
    jobs_list = []
    final_job_list = []

    resp_list = get_total_jobs()

    threads = []
    for content in resp_list:
        t = Thread(target=get_jobs, args=(content, jobs_list))
        threads.append(t)
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    threads = []
    print("Total Jobs: ", len(jobs_list))
    for job in jobs_list:
        t = Thread(target=update_jobs_list, args=(job, final_job_list))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # print(final_job_list)
    updates = to_json(final_job_list)
    # print(len(final_job_list))
    print("Total Jobs Scraped: ", len(final_job_list))
    print("Closed Jobs: ", len(updates["Jobs"]) - len(final_job_list))
    print("Scraping Completed")
    return updates


if __name__ == "__main__":
    main()
