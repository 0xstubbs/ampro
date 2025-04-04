import requests

# URL of the ZIP file
url = "https://registry.faa.gov/database/ReleasableAircraft.zip"
filename = "ReleasableAircraft.zip"

# Send a GET request to the URL
headers = {"user-agent": "rubber-ducky/0.0.1"}
response = requests.get(url, headers=headers, allow_redirects=True)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print(response.headers)
    print(f"Saving to {filename}")
    # Open a local file in write-binary mode and save the content of the ZIP file
    with open(filename, "wb") as file:
        file.write(response.content)
    print("Download completed successfully.")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")
