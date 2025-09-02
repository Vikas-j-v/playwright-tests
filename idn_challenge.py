import json
import os
import re
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
LOGIN_URL = "https://hiring.idenhq.com/"
INSTRUCTIONS_URL = "https://hiring.idenhq.com/instructions"
CHALLENGE_URL = "https://hiring.idenhq.com/challenge"
USERNAME = "vikas.jv@campusuvce.in"
PASSWORD = "zsI6smuW"
SESSION_FILE = "iden_session.json"
OUTPUT_FILE = "products_data.json"

# --- Main Functions ---

def login_and_save_session(context, page):
    """
    Performs a fresh user login and saves the session state (cookies, local storage)
    to a file for reuse in subsequent runs.

    Args:
        context: The browser context to save the session from.
        page: The Playwright page object to perform login actions on.
    """
    print("No valid session. Logging in...")
    page.goto(LOGIN_URL)
    
    page.get_by_label("Email").fill(USERNAME)
    page.get_by_label("Password").fill(PASSWORD)
    page.locator("button[type='submit']").click()

    # Smart Wait: Wait for the URL to confirm successful navigation after login.
    page.wait_for_url(INSTRUCTIONS_URL, timeout=60000)
    print("Login successful.")
    
    # Save the authenticated state to the session file.
    context.storage_state(path=SESSION_FILE)
    print(f"Session saved to '{SESSION_FILE}'.")

def navigate_to_products(page):
    """
    Navigates the application's menu system to reveal the product inventory table.
    This demonstrates handling a multi-step navigation process.

    Args:
        page: The authenticated Playwright page object.
    """
    print("Navigating to product inventory...")
    
    if page.url != CHALLENGE_URL:
        page.goto(CHALLENGE_URL)

    # Sequence of clicks to navigate through the menu system.
    page.get_by_role("button", name="Menu").click()
    page.get_by_text("Data Management").click()
    page.get_by_text("Inventory").click()
    page.get_by_text("View All Products").click()

    # Handle the intermediate modal dialog.
    page.get_by_role("button", name="Load Product Table").click()
    print("Loading product table...")

    # Smart Wait: Wait for the table's main container to be present in the DOM.
    page.wait_for_selector("div.infinite-table", timeout=60000)
    print("Product table loaded.")

def extract_all_products_with_scrolling(page):
    """
    Scrapes all product data from a table that uses infinite scrolling.
    This demonstrates a robust technique for handling lazy-loaded content.

    Args:
        page: The Playwright page object with the product table visible.

    Returns:
        A list of dictionaries, where each dictionary represents a product.
    """
    print("Starting scraper...")

    # Robust Technique: First, find the element containing the total product count.
    total_products_locator = page.get_by_text(re.compile(r"Showing \d+ of \d+ products"))
    total_products_text = total_products_locator.inner_text()
    total_products = int(re.search(r'of (\d+)', total_products_text).group(1))
    print(f"Target: {total_products} products.")

    all_products = []
    scroll_container_selector = "div.infinite-table"
    
    # Loop until the number of scraped products matches the total count.
    while len(all_products) < total_products:
        last_count = len(all_products)

        # Use page.evaluate to run custom JavaScript in the browser for efficiency.
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

        # Add only new products to the master list.
        current_ids = {p.get('uniqueId') for p in all_products}
        for product in products_on_page:
            if product.get('uniqueId') not in current_ids:
                del product['uniqueId']
                all_products.append(product)
        
        # A clean, single-line progress updater.
        print(f"Scraped {len(all_products)} / {total_products} products", end='\r')
        sys.stdout.flush()

        # Safety break: If scrolling stops loading new products, exit the loop.
        if len(all_products) == last_count:
            print("\nScroll limit reached. Ending scrape.")
            break
        
        # Execute JavaScript to scroll the container to the bottom.
        page.evaluate(f'document.querySelector("{scroll_container_selector}").scrollTop = document.querySelector("{scroll_container_selector}").scrollHeight')
        
        page.wait_for_timeout(1000)

    print() # Final newline after the progress bar is complete.
    return all_products

# --- Main Execution ---

def main():
    """
    Main function to orchestrate the entire web scraping process,
    including session management and error handling.
    """
    # The 'with' statement manages the Playwright lifecycle (startup and shutdown).
    with sync_playwright() as playwright:
        browser = None
        try:
            # All browser operations MUST happen inside the 'with' block.
            browser = playwright.chromium.launch(headless=False)
            context = None
            
            # Proper Session Management: Check -> Load -> Verify -> Fallback
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
                login_and_save_session(context, page)

            # --- Core Scraping Logic ---
            navigate_to_products(page)
            products_data = extract_all_products_with_scrolling(page)
            
            # --- Data Export ---
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