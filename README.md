# playwright-tests
Iden Challenge - Product Scraper
This project contains a Python script that uses the Playwright library to automate the process of logging into the Iden Hiring Challenge website, navigating to the product inventory, and scraping all product data from a table with infinite scrolling.

How It Works
The script is designed to be robust and efficient, incorporating session management to avoid unnecessary logins on subsequent runs.

The main workflow is as follows:

Session Management: The script first checks for a saved session file (iden_session.json).

If a valid session file exists, it loads it into the browser context, skipping the login step.

If the session is invalid or the file doesn't exist, the script performs a full login using the provided credentials and saves the new session state (cookies, local storage) to iden_session.json for future use.

Navigation: Once authenticated, the script navigates through the application's menu system (Menu > Data Management > Inventory > View All Products) to access the product table.

Data Extraction: The core of the script handles the infinite-scrolling table.

It first identifies the total number of products listed on the page.

It then enters a loop, scraping the currently visible products and scrolling down to load more.

This process continues until the number of scraped products matches the total count, ensuring all data is captured.

Output: All the extracted product data is saved into a neatly formatted JSON file named products_data.json.

Prerequisites
Before you run the script, make sure you have the following installed:

Python 3.8+

pip (Python package installer)

Setup and Installation
Clone the repository (or download the files):

git clone <your-repository-url>
cd <your-repository-name>

Create a virtual environment (recommended):

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install the required Python packages:
This project uses Playwright. You can install it using pip.

pip install playwright

Install Playwright browsers:
Playwright requires browser binaries to be installed. Run the following command to install them (this will download Chromium, Firefox, and WebKit).

playwright install

Set Credentials:
The script requires a username and password to log in. These are currently hardcoded in idn_challenge.py.

USERNAME = "vikas.jv@campusuvce.in"
PASSWORD = "zsI6smuW"

Ensure these are correct before running. For better security, it's recommended to load these from environment variables instead of hardcoding them.

How to Run the Script
Once the setup is complete, you can run the scraper with the following command:

python idn_challenge.py

You will see log messages in your terminal indicating the script's progress. By default, the script runs in "headed" mode, so you will see the browser window open and perform the automated steps.

Upon successful completion, a file named products_data.json will be created in the same directory, containing all the scraped product information.
