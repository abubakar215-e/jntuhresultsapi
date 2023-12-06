# import requests
# import redis
# import json
# from bs4 import BeautifulSoup
# from datetime import timedelta
# import os
# from dotenv import load_dotenv


# # load_dotenv()
# # redis_url=os.environ.get("REDIS_URL")
# # redis_client = redis.from_url(redis_url)

# def get_notifications():
#     # Load environment variables from .env file

#     # redis_response = redis_client.get("notifications")
#     # if redis_response is not None:
#     #     data = json.loads(redis_response)
#     #     return data["data"]
#     url = "http://results.jntuh.ac.in/jsp/home.jsp"
#     #url="http://202.63.105.184/results/jsp/home.jsp"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     results=[]
#     for i in range(0,6):
#         jntuh_notifications = soup.find_all("table")[i].find_all("tr")
        
#         for result in jntuh_notifications:
#             result_link = result.find_all("td")[0].find_all("a")[0]["href"]
#             result_text = result.get_text()
#             result_text_index=result_text.find("Results")+7
#             json_appendded={
#                 "Result_title":result_text[:result_text_index],
#                 "Link":"http://results.jntuh.ac.in"+result_link,
#                 "Date":result_text[result_text_index:]
#             }
#             results.append(json_appendded)
#     # redis_client.set("notifications", json.dumps({"data": results}))
#     # redis_client.expire("notifications", timedelta(minutes=15))
#     return results




# import requests
# from bs4 import BeautifulSoup
# import json

# def get_notifications():
#     url = "http://results.jntuh.ac.in/jsp/home.jsp"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "html.parser")
#     results = {}

#     categories = ["btech", "bpharmacy", "mtech", "mpharmacy", "mba"]

#     for i in range(0, 5):
#         category_notifications = soup.find_all("table")[i].find_all("tr")

#         for result in category_notifications:
#             result_link = result.find_all("td")[0].find_all("a")[0]["href"]
#             result_text = result.get_text()
#             result_text_index = result_text.find("Results") + 7

#             category_key = categories[i]
#             json_appended = {
#                 "Result_title": f"{category_key.capitalize()} Results",
#                 "Link": f"http://results.jntuh.ac.in{result_link}",
#                 "Date": result_text[result_text_index:]
#             }

#             if category_key not in results:
#                 results[category_key] = []

#             results[category_key].append(json_appended)

#     # Save results to a JSON file
#     with open('results.json', 'w') as json_file:
#         json.dump(results, json_file, indent=2)

# # Call the function to get notifications and save them in a JSON file
# get_notifications()


import requests
from bs4 import BeautifulSoup
import json

def get_notifications():
    url = "http://results.jntuh.ac.in/jsp/home.jsp"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    results = []

    for i in range(0, 5):
        jntuh_notifications = soup.find_all("table")[i].find_all("tr")

        for result in jntuh_notifications:
            result_link = result.find_all("td")[0].find_all("a")[0]["href"]
            result_text = result.get_text()
            result_text_index = result_text.find("Results") + 7
            json_appended = {
                "Result_title": result_text[:result_text_index],
                "Link": "http://results.jntuh.ac.in" + result_link,
                "Date": result_text[result_text_index:]
            }
            results.append(json_appended)

    # Save results to a JSON file
    with open('results.json', 'w') as json_file:
        json.dump(results, json_file, indent=2)

# Call the function to get notifications and save them in a JSON file
get_notifications()
