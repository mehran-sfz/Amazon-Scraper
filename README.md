# Amazon Product Scraper

This project is a powerful web scraping tool designed to extract data from **Amazon**. Whether you're looking to gather details about a specific product, collect lists of products based on search keywords, or fetch product listings from a direct URL — this scraper handles it all, including automatic CAPTCHA solving.

---

## 🔍 Features

- **Search by keyword**: Provide a search term and specify how many pages to scrape. It will return all matching products from the given number of pages.
- **Get product details**: Supply a product URL and receive detailed information like:
  - Title
  - Price
  - Description
  - Features
  - Rating
  - Number of reviews
- **Extract product list by link**: Given a category or listing page URL, it fetches all the product entries up to the page limit.
- **Automatic CAPTCHA Bypass**: Solves Amazon CAPTCHAs automatically to allow seamless scraping.

---

## 🚀 Technologies Used

- **Selenium**: For browser automation and interaction with dynamic content.
- **BeautifulSoup**: For parsing and extracting data from HTML content.
- **Pillow (PIL)**: Used to process and solve CAPTCHA images.

---

## 📖 How to Use

### 1. Initialize the Scraper
```python
from amazon_scraper import AmazonScraper

scraper = AmazonScraper()  # Initializes and runs the Chrome driver
```

### 2. Solve CAPTCHA
```python
scraper.bypass_captcha()
```
When you see the success message, the CAPTCHA is solved and you can proceed to use the other methods.

### 3. Search Products by Keyword
```python
results = scraper.get_product_by_search("laptop", page_limit=2)
```
This will return a dictionary of products found in the first 2 pages for the search term "laptop".

### 4. Get Product List by Link
```python
product_list = scraper.get_product_list_by_link("https://www.amazon.com/s?k=smartphones", page_limit=2)
```
Scrapes product listings from the given URL up to 2 pages.

### 5. Get Detailed Product Info
```python
product_details = scraper.get_detail_product_by_link("https://www.amazon.com/dp/B0...example")
```
Returns detailed product information such as title, price, rating, features, and more.

---

## 🙏 Support and Contributions

If you have a feature request or find a bug, feel free to open an issue or pull request on GitHub. I’m actively maintaining this project and happy to improve it based on your feedback.

If you find this project helpful, please consider giving it a ⭐ on GitHub — it means a lot!

---

Happy Scraping! 🤖
