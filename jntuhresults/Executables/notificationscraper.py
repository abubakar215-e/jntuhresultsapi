import requests
import json
from bs4 import BeautifulSoup

def get_notifications():
    # Fetch notifications from the website
    url = "http://results.jntuh.ac.in/jsp/RCRVInfo.jsp"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    results = []

    # Find all <h3> tags with class "highlightme"
    notifications = soup.find_all("h3")

    # Iterate over the notifications and extract relevant information
    for notification in notifications:
        notification_data = {}

        # Extract title
        title = notification.text.strip()

        # Extract date
        date_start_index = title.find("(") + 1
        date_end_index = title.find(")")
        date = title[date_start_index:date_end_index]

        # Remove date from the title
        title = title.replace("(" + date + ")", "").strip()

        # Remove asterisk (*) from the title
        title = title.replace("*", "").strip()

        # Check if the notification is related to B.Tech or B.Pharmacy or mtech or mpharm or mba(case-insensitive)
        if "b.tech" in title.lower() or "b.pharmacy" in title.lower() or "b.pharm" in title.lower() or "m.tech" in title.lower() or "m.pharmacy" in title.lower() or "m.pharm" in title.lower() or "mba" in title.lower():
            notification_data["notification_description"] = title
            notification_data["notification_date"] = date

            results.append(notification_data)

    return results

# Call the function to get the notifications
notifications = get_notifications()
# print(json.dumps(notifications, indent=2))
