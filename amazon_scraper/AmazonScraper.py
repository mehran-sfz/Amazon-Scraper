from bs4 import BeautifulSoup
from captcha.solver import AmazonCaptcha

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode



def separate_url_components(url):
    
    """
    Separate a URL into its components: domain, path, and query parameters.
    :param url: The URL to be separated
    :return: A tuple containing the domain, path, and query parameters as a dictionary.
    """
    
    parsed_url = urlparse(url)
    
    # Domain (netloc)
    domain = parsed_url.netloc
    
    # Path (without query params)
    path = parsed_url.path
    
    # Query Params (as a dictionary)
    query_params = parse_qs(parsed_url.query)
    
    return domain, path, query_params

def construct_url(domain, path, query_params):
    
    """
    Construct a URL from its components: domain, path, and query parameters.
    :param domain: The domain of the URL
    :param path: The path of the URL
    :param query_params: The query parameters as a dictionary
    :return: The constructed URL as a string.
    """
    
    # Convert query_params dictionary to a query string
    query_string = urlencode(query_params, doseq=True)
    
    # Construct the full URL
    full_url = urlunparse(('https', domain, path, '', query_string, ''))
    return full_url



class AmazonScraper:
    
    def __init__(self):
        
        """
        Initialize the Amazon scraper.
        This method sets up the Chrome WebDriver with specific options for headless browsing.
        It also navigates to the Amazon homepage.
        The WebDriver is configured to run in headless mode, meaning it will not display a UI.
        """
        
        self.logged_in = False
        self.driver = None
        
        options = webdriver.ChromeOptions()

        # Add the --headless argument for headless mode (no UI)
        options.add_argument("--disable-notifications")
        options.add_argument("start-maximized")
        options.add_argument("--headless")  # Run in headless mode

        options.add_experimental_option(
            'excludeSwitches', ['disable-logging'])
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)


        print("Starting Chrome...")
        # Start Chrome with the specified options
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)
        print("Chrome started.")

        self.driver.implicitly_wait(20)
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {"User-Agent": "browser1"}})

        print("Navigating to Amazon...")
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get('https://www.amazon.com/')


    def bypass_captcha(self):
        
        """
        Bypass the captcha on Amazon.
        This method checks for the presence of a captcha image on the page.
        If found, it uses the AmazonCaptcha solver to solve the captcha.
        The solution is then entered into the captcha input field and submitted.
        """
        
        if self.driver is None:
            raise Exception("Driver not initialized. Please initialize the driver first.")
        
        if self.logged_in:
            raise Exception("Already logged in. No need to bypass captcha. unless the bypass captcha is not work as expected.")
        
        
        
        print("Bypassing captcha...")
        self.driver.get('https://www.amazon.com/')
        # wait for the page to load
        self.wait.until(ec.presence_of_element_located((By.TAG_NAME, "img")))
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        captcha_input = soup.find_all('img')
        img_captcha = [img['src'] for img in captcha_input if 'Captcha' in img['src']]

        if img_captcha == []:
            return {'success': False, 'message': 'No captcha found'}

        # solve captcha
        captcha = AmazonCaptcha.fromlink(img_captcha[0])
        solution = captcha.solve()
        
        print(f"Captcha solution: {solution}")
        
        # put it in the input field
        # enter and move to next field
        self.driver.find_element(By.ID, "captchacharacters").send_keys(solution)
        # click continue button
        self.driver.find_element(By.ID, "captchacharacters").send_keys(Keys.RETURN)
        
        #chage the logged_in status to true
        self.logged_in = True
        return {'success': True, 'message': 'Captcha solved and submitted'}
    
    
    def get_product_by_search(self, search:str, page_limit:int= 1):
        
        """
        Get product by search term and page limit
        :param search: Search term
        :param page_limit: Page limit
        :return: List of product links
        
        it will return a dictionary with the data-asin as the key and the product link as the value.
        
        Input Example:
        get_product_by_search('laptop', 2)
        
        Output Example:
        
        {
            'B09X1Y5F5D': 'https://www.amazon.com/dp/B09X1Y5F5D...',
            'B09X1Y5F5E': 'https://www.amazon.com/dp/B09X1Y5F5E...',
            'B09X1Y5F5F': 'https://www.amazon.com/dp/B09X1Y5F5F...',
        }
        
        """
        
        
        if self.driver is None:
            raise Exception("Driver not initialized. Please initialize the driver first.")
        if not self.logged_in:
            raise Exception("Not logged in. Please bypass captcha first with bypass_captcha() method.")
        
                
        search = search.replace(' ', '+')
        
        product_link = dict()
        for page in range(1, page_limit+1):
                    
            parameters = {
            'k': search,
            'page': page,
            }

            url = 'https://www.amazon.com/s?k={k}&page={page}'.format(**parameters)

            self.driver.get(url)

            # wait for the page to load
            self.wait.until(ec.presence_of_element_located((By.ID, "search")))

            # scroll down to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # wait for the new products to load
            self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "s-main-slot")))
            
            
            # get the page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # check validation of the page
            validation = soup.find('body')
            if validation is None or validation.text.strip() == '':
                raise Exception(f"Invalid page. Please check the search term and try again. url: {url}")
            
            
            # find all the product links and data asin
            product_list = soup.find_all('div', {'role': 'listitem', 'data-component-type' : 's-search-result'})
            
            if product_list == []:
                break
            
            # get the product links and data asin
            # find all the product links and data asin
            for item in product_list:
                
                data_asin = item['data-asin']
                link = item.find('a', {'class': 'a-link-normal s-no-outline'})
                
                if product_link.get(data_asin) is None:
                
                    product_link[data_asin] = 'https://www.amazon.com' + link['href']

                
        return product_link
            

    def get_detail_product_by_link(self, link:str):
        
        """
        Get product details by link
        :param link: Product link
        :return: Dictionary of product details
        
        Input Example:
        get_detail_product_by_link('https://www.amazon.com/dp/B09X1Y5F5D')
        
        Output Example:
            
            {
                'title': 'Product Title',
                'rating': '4.5 out of 5 stars',
                'reviews': '1000 reviews',
                'about_the_item': 'Product details...',
                'deal_price': '$100.00',
                'product_overview_list': [['Overview 1', 'Overview 2'], ['Overview 3', 'Overview 4']]
            }
        
        """
        
        if self.driver is None:
            raise Exception("Driver not initialized. Please initialize the driver first.")
        if not self.logged_in:
            raise Exception("Not logged in. Please bypass captcha first with bypass_captcha() method.")
        
    
        data_collect = dict()
        self.driver.get(link)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # check validation of the page
        validation = soup.find('body')
        if validation is None or validation.text.strip() == '':
            raise Exception(f"Invalid page. Please check the search term and try again. url: {link}")
        
        
        # get the title
        title = soup.find('span', {'id': 'productTitle'}).text.strip()
        data_collect['title'] = title
        
        
        # get the rating
        rating = soup.find('span', {'id': 'acrPopover'})['title']
        data_collect['rating'] = rating
        
        # get the number of reviews
        reviews = soup.find('span', {'id': 'acrCustomerReviewText'}).text.strip()
        data_collect['reviews'] = reviews
        
        # get the product details
        # Find the div containing feature bullets
        feature_bullets_div = soup.find('div', id='feature-bullets')
        if feature_bullets_div:
            # Join the text of each list item with a separator, ensuring whitespace is stripped
            data_collect['about_the_item'] = "\n>>>".join(
                item.get_text(strip=True) for item in feature_bullets_div.find_all('li', class_='a-spacing-mini')
            )
        else:
            data_collect['about_the_item'] = ""

        # Get the price element from the HTML
        price_div = soup.find('div', id='corePrice_desktop')
        data_collect['deal_price'] = []

        if price_div:
            rows = price_div.find_all('tr')
            for row in rows:
                # Ensure that the row has a colon-separated text value
                parts = row.text.strip().split(':')
                if len(parts) > 1:
                    key = parts[0].strip()
                    # Find the span with the price text
                    price_span = row.find('span', class_='a-offscreen')
                    if price_span:
                        value = price_span.get_text(strip=True)
                        data_collect['deal_price'].append(f"{key}: {value}")
        else:
            # Optionally handle the case where the price div isn't found
            data_collect['deal_price'] = []

    

        # Extract product overview data into a list of rows, where each row is a list of cell texts.
        data_collect['product_overview_list'] = []
        overview_div = soup.find('div', id='poExpander')
        if overview_div:
            table = overview_div.find('table')
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells:
                        # Use a list comprehension with get_text(strip=True) for cleaner extraction.
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        data_collect['product_overview_list'].append(cell_texts)
                        
                        
        return data_collect

            
    def get_product_list_by_link(self, link, page_limit=1):
        
        """
        Get product list by link
        :param link: Product link
        :param page_limit: Page limit
        :return: List of product links
        
        Input Example:
        get_product_list_by_link('https://www.amazon.com/s?k=laptop')
        
        Output Example:
            
            {
                'B09X1Y5F5D': 'https://www.amazon.com/dp/B09X1Y5F5D...',
                'B09X1Y5F5E': 'https://www.amazon.com/dp/B09X1Y5F5E...',
                'B09X1Y5F5F': 'https://www.amazon.com/dp/B09X1Y5F5F...',
            }
            
        """

        
        if self.driver is None:
            raise Exception("Driver not initialized. Please initialize the driver first.")
        if not self.logged_in:
            raise Exception("Not logged in. Please bypass captcha first with bypass_captcha() method.")
        
        

        # Example usage
        domain, path, query_params = separate_url_components(link)
        
        product_link = dict()
        for page in range(1, page_limit+1):
            # Update the page number in the query parameters
            query_params['page'] = page
            
            # Construct the new URL with the updated query parameters
            url = construct_url(domain, path, query_params)

            self.driver.get(url)

            # wait for the page to load
            self.wait.until(ec.presence_of_element_located((By.ID, "search")))

            # scroll down to load more products
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # wait for the new products to load
            self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "s-main-slot")))
            
            
            # get the page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # check validation of the page
            validation = soup.find('body')
            if validation is None or validation.text.strip() == '':
                raise Exception(f"Invalid page. Please check the search term and try again. url: {url}")
            
            
            # find all the product links and data asin
            product_list = soup.find_all('div', {'role': 'listitem', 'data-component-type' : 's-search-result'})
            
            if product_list == []:
                break
            
            # get the product links and data asin
            # find all the product links and data asin
            for item in product_list:
                
                data_asin = item['data-asin']
                link = item.find('a', {'class': 'a-link-normal s-no-outline'})
                
                if product_link.get(data_asin) is None:
                
                    product_link[data_asin] = link['href']

                
        return product_link
                
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    