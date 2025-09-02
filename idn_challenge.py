import json
import os
import re
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
LOGIN_URL = "https://hiring.idenhq.com/"
INSTRUCTIONS_URL = "https://hiring.idenhq.com/instructions"
CHALLENGE_URL = "https://hiring.idenhq.com/challenge"
SESSION_FILE = "iden_session.json"
OUTPUT_FILE = "products_data.json"

# --- Helper Functions ---

def load_credentials():
    """
    Loads username and password from the config.json file.
    Provides clear error messages if the file is missing or malformed.
    """
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            username = config.get("IDEN_USERNAME")
            password = config.get("IDEN_PASSWORD")
            if not username or not password:
                print("Error: 'IDEN_USERNAME' or 'IDEN_PASSWORD' not found in config.json.")
                sys.exit(1)
            return username, password
    except FileNotFoundError:
        print("Error: config.json not found.")
        print("Please create a 'config.json' file with your credentials.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode config.json. Please ensure it is a valid JSON file.")
        sys.exit(1)

# --- Main Functions ---

def login_and_save_session(context, page, username, password):
    """
    Performs a fresh user login using credentials from config.json and saves the session.
    """
    print("No valid session. Logging in...")
    page.goto(LOGIN_URL)
    
    # Use the credentials passed from the main function
    page.get_by_label("Email").fill(username)
    page.get_by_label("Password").fill(password)
    page.locator("button[type='submit']").click()

    page.wait_for_url(INSTRUCTIONS_URL, timeout=60000)
    print("Login successful.")
    
    context.storage_state(path=SESSION_FILE)
    print(f"Session saved to '{SESSION_FILE}'.")


def navigate_to_products(page):
    """
    Navigates the application's menu system to reveal the product inventory table.
    """
    print("Navigating to product inventory...")
    
    if page.url != CHALLENGE_URL:
        page.goto(CHALLENGE_URL)

    page.get_by_role("button", name="Menu").click()
    page.get_by_text("Data Management").click()
    page.get_by_text("Inventory").click()
    page.get_by_text("View All Products").click()

    page.get_by_role("button", name="Load Product Table").click()
    print("Loading product table...")

    page.wait_for_selector("div.infinite-table", timeout=60000)
    print("Product table loaded.")


def extract_all_products_with_scrolling(page):
    """
    Scrapes all product data from a table that uses infinite scrolling.
    """
    print("Starting scraper...")

    total_products_locator = page.get_by_text(re.compile(r"Showing \d+ of \d+ products"))
    total_products_text = total_products_locator.inner_text()
    total_products = int(re.search(r'of (\d+)', total_products_text).group(1))
    print(f"Target: {total_products} products.")

    all_products = []
    scroll_container_selector = "div.infinite-table"
    
    while len(all_products) < total_products:
        last_count = len(all_products)

        products_on_page = page.evaluate('''() => {
            const products = [];
            const table = document.querySelector('table');
            if (!table) return [];

            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.innerText.trim());
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length === headers.length) {
                    const product = {};
                    headers.forEach((key, index) => {
                        const cell = cells[index];
                        if (key === 'Rating') {
                            const ratingSpan = cell.querySelector('span');
                            product[key] = ratingSpan ? ratingSpan.innerText.trim() : null;
                        } else {
                            product[key] = cell.innerText.trim();
                        }
                    });
                    const uniqueId = Object.values(product).join('-');
                    product['uniqueId'] = uniqueId;
                    products.push(product);
                }
            });
            return products;
        }''')

        current_ids = {p.get('uniqueId') for p in all_products}
        for product in products_on_page:
            if product.get('uniqueId') not in current_ids:
                del product['uniqueId']
                all_products.append(product)
        
        print(f"Scraped {len(all_products)} / {total_products} products", end='\r')
        sys.stdout.flush()

        if len(all_products) == last_count:
            print("\nScroll limit reached. Ending scrape.")
            break
        
        page.evaluate(f'document.querySelector("{scroll_container_selector}").scrollTop = document.querySelector("{scroll_container_selector}").scrollHeight')
        
        page.wait_for_timeout(1000)

    print() 
    return all_products


def main():
    """
    Main function to orchestrate the entire web scraping process.
    """
    # First, securely load credentials from the JSON file.
    username, password = load_credentials()

    with sync_playwright() as playwright:
        browser = None
        try:
            browser = playwright.chromium.launch(headless=False)
            context = None
            
            if os.path.exists(SESSION_FILE):
                print("Session file found. Reusing session.")
                context = browser.new_context(storage_state=SESSION_FILE)
            else:
                print("No session file found.")
                context = browser.new_context()

            page = context.new_page()
            
            try:
                print("Verifying session...")
                page.goto(CHALLENGE_URL, wait_until="networkidle", timeout=10000)
                page.get_by_text("Sign out").wait_for(timeout=5000)
                print("Session is valid.")
            except PlaywrightTimeoutError:
                login_and_save_session(context, page, username, password)

            navigate_to_products(page)
            products_data = extract_all_products_with_scrolling(page)
            
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(products_data, f, indent=4)
            
            print(f"Extraction complete. Saved {len(products_data)} products to {OUTPUT_FILE}.")

        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
        finally:
            if browser:
                browser.close()


if __name__ == "__main__":
    main()

