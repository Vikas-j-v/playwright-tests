# Playwright Tests - Iden Challenge Product Scraper

A robust Python web scraping solution using Playwright to automate login, navigation, and data extraction from infinite-scrolling product tables.

## 🚀 Features

- **Session Management**: Intelligent session caching to avoid repeated logins
- **Infinite Scroll Handling**: Automated scrolling and data extraction from dynamic tables
- **Robust Error Handling**: Comprehensive error management and retry logic
- **JSON Output**: Clean, structured data export
- **Headless/Headed Mode Support**: Flexible browser execution options

## 📋 Prerequisites

Before running the script, ensure you have the following installed:

- **Python 3.8+**
- **pip** (Python package installer)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Vikas-j-v/playwright-tests.git
cd playwright-tests
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install playwright
```

### 4. Install Playwright Browsers

```bash
playwright install
```

This command downloads the necessary browser binaries (Chromium, Firefox, and WebKit).

## ⚙️ Configuration

### Set Credentials

Create a `config.json` file in the project root with your credentials:

```json
{
  "IDEN_USERNAME": "your_email@example.com",
  "IDEN_PASSWORD": "your_password"
}
```

The script will automatically load credentials from this file using the `load_credentials()` function.

**Security Note**: 
- Add `config.json` to your `.gitignore` file to prevent accidentally committing credentials
- For production use, consider using environment variables or secure credential management systems

## 🏃‍♂️ Usage

### Basic Usage

```bash
python idn_challenge.py
```

The script will:
1. Check for existing session (`iden_session.json`)
2. Login if no valid session exists
3. Navigate to the product inventory
4. Scrape all product data with infinite scroll handling
5. Save results to `products_data.json`

## 📁 Project Structure

```
playwright-tests/
├── idn_challenge.py          # Main scraping script
├── config.json               # Configuration file (create this)
├── iden_session.json         # Session cache (auto-generated)
├── products_data.json        # Output data file (auto-generated)
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
└── README.md                # Project documentation
```

## 🔄 How It Works

### Session Management
- **First Run**: Performs full login and saves session state
- **Subsequent Runs**: Loads saved session to skip login process
- **Session Validation**: Automatically detects invalid sessions and re-authenticates

### Navigation Flow
1. **Session Verification**: Attempts to load existing session and verify access
2. **Login Process**: If session invalid, performs fresh login to hiring.idenhq.com
3. **Menu Navigation**: Navigates through: Menu → Data Management → Inventory → View All Products
4. **Table Loading**: Clicks "Load Product Table" and waits for infinite table to appear

### Data Extraction Process
1. **Product Count Detection**: Reads total count from "Showing X of Y products" text
2. **Table Scraping**: Uses JavaScript evaluation to extract table headers and row data
3. **Infinite Scroll Handling**: Automatically scrolls container to load more products
4. **Duplicate Prevention**: Uses unique ID system to avoid duplicate entries
5. **Progress Tracking**: Real-time progress display during extraction
6. **Data Export**: Saves complete dataset to JSON with UTF-8 encoding

## 📊 Output Format

The script generates `products_data.json` with the following structure:

```json
[
  {
    "product_id": "12345",
    "name": "Product Name",
    "category": "Category",
    "price": "$99.99",
    "stock": "Available",
    "description": "Product description..."
  }
]
```

## 🔧 Customization Options

### Run in Headless Mode

Modify the browser launch options in `idn_challenge.py`:

```python
browser = playwright.chromium.launch(headless=True)  # Change to True
```

### Adjust Scroll Timing

Customize scroll delays in the `extract_all_products_with_scrolling()` function:

```python
page.wait_for_timeout(1000)  # Adjust timing as needed
```

### Change Timeout Values

Modify timeout values for different network conditions:

```python
page.wait_for_url(INSTRUCTIONS_URL, timeout=60000)  # Login timeout
page.wait_for_selector("div.infinite-table", timeout=60000)  # Table load timeout
```

## 🐛 Troubleshooting

### Common Issues

1. **Configuration Errors**
   ```
   Error: config.json not found.
   Error: 'IDEN_USERNAME' or 'IDEN_PASSWORD' not found in config.json.
   ```
   - Ensure `config.json` exists with correct field names
   - Verify JSON syntax is valid

2. **Login Failures**
   - Check credentials in `config.json`
   - Verify website accessibility
   - Delete `iden_session.json` and retry

3. **Incomplete Data Extraction**
   - Script shows progress: "Scraped X / Y products"
   - Check network connectivity
   - Increase timeout values if needed

4. **Session Issues**
   - Script will automatically handle invalid sessions
   - Session verification happens before navigation

### Debug Mode

Run with additional logging:

```python
# Add to script for detailed debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Web testing and automation framework
- [Python](https://python.org/) - Programming language

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Vikas-j-v/playwright-tests/issues) section
2. Create a new issue with detailed information
3. Include error logs and system information

---

**Happy Scraping!** 🎯

##working video link - 
https://drive.google.com/file/d/1QX7OeQ4GDpQ8NUTFxXqloIT0r8VAAujU/view?usp=sharing
