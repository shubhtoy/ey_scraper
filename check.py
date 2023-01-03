import requests
from bs4 import BeautifulSoup
from lxml import etree
from threading import Thread


def update_jobs_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    no = soup.findAll("div", class_="joblayouttoken")
    other_sites = (
        no[2].find("span", {"data-careersite-propertyid": "customfield3"}).text.strip()
    )
    # print(other_sites)
    # print(requisition_id)
    salary = no[3].find("span", {"lang": "en-US"}).text.strip()
    # print(designation)
    description = no[6].text.strip()
    requisition_id = (
        no[5].find("span", {"data-careersite-propertyid": "customfield5"}).text.strip()
    )
    date = no[4].find("span", {"data-careersite-propertyid": "date"}).text.strip()
    # print(description)
    print(other_sites, salary, description, requisition_id, date)

    return


update_jobs_list(
    "https://careers.ey.com/ey/job/Trivandrum-DET_Security-%2B-Network-specialist_GDSF02-KL-695581/870371601/"
)
