# ConvocationDetailsScrapper
import requests
from bs4 import BeautifulSoup

# Define the URL and payload data
url = "https://studentservices.jntuh.ac.in/oss/convocationDetails.html"
payload = {"htno": "20365A0501"}

# Suppress the InsecureRequestWarning by using the 'requests' module's filter
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Make a POST request with certificate verification disabled
response = requests.post(url, data=payload, verify=False)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the desired information (replace this with your specific requirements)
    result_div = soup.find('div', {'align': 'center'})
    table_content = result_div.find('table', {'class': 'transtable'})
    message = table_content.find('span').text

    # Print or use the scraped data as needed
    print(message)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
