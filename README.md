# Hanabusa-Automation
Automates the process of uploading a property from https://www.homes.co.jp/ to the Hanabusa Website:
Requires properties to be new built, is within 20 minutes of walking distance to a station, has land rights "Ownership", and transaction mode "mediation".
Steps to use the script:
1. Download the .py file
2. Download the appropriate chromedriver for your chrome web browser from https://chromedriver.chromium.org/downloads
3. Extract the appropriate file and rename is the chromedriver.exe.
4. Copy and paste chromedriver.exe to the same directory containing the .py file.
5. Install Python from https://www.python.org/downloads/
6. Install the following python modules: bs4, selenium, fake-useragent
7. Choose a prefecture from https://www.homes.co.jp/kodate/shinchiku/
8. Choose a city
9. Choose properties that satisfies the aforementioned conditions
10. Copy the link
11. Run the script
12. Enter the state, city, and area
13. Paste the link(s) of the chosen properties
14. Enter the indices of the desired pictures
15. The script will automatically scrape data and pictures off the website and input these data into the Hanabusa website
