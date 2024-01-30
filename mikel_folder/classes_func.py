#Packages

import json
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium import webdriver
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import requests
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Go get geckodriver from : https://github.com/mozilla/geckodriver/releases

def ffx_preferences(dfolder, download=False):
    '''
    Sets the preferences of the firefox browser: download path.
    '''
    profile = webdriver.FirefoxProfile()
    # set download folder:
    profile.set_preference("browser.download.dir", dfolder)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/msword,application/rtf, application/csv,text/csv,image/png ,image/jpeg, application/pdf, text/html,text/plain,application/octet-stream")
    
   # profile.add_extension('/Users/luisignaciomenendezgarcia/Dropbox/CLASSES/class_bse_text_mining/class_scraping_bse/booking/booking/ublock_origin-1.55.0.xpi')


    # this allows to download pdfs automatically
    if download:
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,application/x-pdf")
        profile.set_preference("pdfjs.disabled", True)

    options = Options()
    options.profile = profile
    return options

def start_up(link, dfolder, geko_path,donwload=True):
    # geko_path='/Users/luisignaciomenendezgarcia/Dropbox/CLASSES/class_bse_text_mining/class_scraping_bse/booking/geckodriver'
    # download_path='./downloads'
    os.makedirs(dfolder, exist_ok=True)

    options = ffx_preferences(dfolder,donwload)
    service = Service(geko_path)
    browser = webdriver.Firefox(service=service, options=options)
    # Enter the website address here
    browser.get(link)
    time.sleep(5)  # Adjust sleep time as needed
    return browser

def check_and_click(browser, xpath, type):
    '''
    Function that checks whether the object is clickable and, if so, clicks on
    it. If not, waits one second and tries again.
    '''
    ck = False
    ss = 0
    while ck == False:
        ck = check_obscures(browser, xpath, type)
        time.sleep(1)
        ss += 1
        if ss == 15:
            # warn_sound()
            # return NoSuchElementException
            ck = True
            # browser.quit()

def check_obscures(browser, xpath, type):
    '''
    Function that checks whether the object is being "obscured" by any element so
    that it is not clickable. Important: if True, the object is going to be clicked!
    '''
    try:
        if type == "xpath":
            browser.find_element('xpath',xpath).click()
        elif type == "id":
            browser.find_element('id',xpath).click()
        elif type == "css":
            browser.find_element('css selector',xpath).click()
        elif type == "class":
            browser.find_element('class name',xpath).click()
        elif type == "link":
            browser.find_element('link text',xpath).click()
    except (ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException) as e:
        print(e)
        return False
    return True

# lets open booking:

#dfolder='./downloads'
#geko_path='/Users/mikelgallo/repos2/text_mining/Scraping_UN/books/geckodriver'
#link='https://www.booking.com/index.es.html'

# Starting Booking browser
#browser=start_up(dfolder=dfolder,link=link,geko_path=geko_path)


class Search:
    def __init__(self,city):
        dfolder='./downloads'
        geko_path='/Users/mikelgallo/repos2/text_mining/Scraping_UN/books/geckodriver'
        link='https://www.booking.com/index.es.html'
        self.browser= start_up(dfolder=dfolder,link=link,geko_path=geko_path)
        self.city = city
        self.start_day = None
        self.end_day = None
        self.num_pages = None
        self.df_list = None
        self.df = None
    
    def input_city(self):
        #Find destination button
        self.browser.find_element(by='xpath',value= '//input[@id=":re:"]').click()
        time.sleep(1)
        #Input city name
        search1 = self.browser.find_element(by='xpath',value='//*[@id=":re:"]')
        search1.send_keys(self.city)
        time.sleep(2)
    
    def open_date_box(self):
        #Use CSS Selector Copy
        css='button.ebbedaf8ac:nth-child(2) > span:nth-child(1)'
        self.browser.find_element('css selector',css).click()

    def extract_dates(self):
        dates_f = []
        path='//div[@id="calendar-searchboxdatepicker"]//table[@class="eb03f3f27f"]//tbody//td[@class="b80d5adb18"]//span[@class="cf06f772fa"]'
        dates = self.browser.find_elements('xpath',path)
        for date in dates:
            dates_f.append(date)
        return dates_f
    
        
    def date_selector(self,date_k):   
        loop = False
        n_pg = 0

        while not loop:
            #Extract dates from table
            dates_f = self.extract_dates()
            #Loop over dates and click if date of interest is found
            for date in dates_f:
                if date.get_attribute("data-date") == date_k:
                    date.click()
                    print('click')
                    print('found in',n_pg+1)
                    loop = True
                    break
                    
            n_pg +=1
            print('date not found in page:',n_pg)
            print('moving to next page')
            time.sleep(1)
            if n_pg <= 1:
                x_path = '/html/body/div[3]/div[2]/div/form/div[1]/div[2]/div/div[2]/div/nav/div[2]/div/div[1]/button'
            else:
                x_path = '/html/body/div[3]/div[2]/div/form/div[1]/div[2]/div/div[2]/div/nav/div[2]/div/div[1]/button[2]'
            self.browser.find_element(by='xpath',value=x_path).click()
        
    def search_results(self):
        my_xpath='/html/body/div[3]/div[2]/div/form/div[1]/div[4]/button/span'
        #Click search button
        check_obscures(self.browser,my_xpath , type='xpath')
        check_and_click(self.browser,my_xpath , type='xpath')

    def result_pages(self):
        num_pages = 0
        a = self.browser.find_elements('xpath','//div[@data-testid="pagination"]//li[@class="b16a89683f"]')
        num_pages = int(a[-1].text)
        return num_pages
    
    def scrape_results(self,max_p):
        #Scraping Data and Saving it to a list of dictionaries
            x_path = '/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[4]/div[2]/nav/nav/div/div[3]/button/span/span'
            result_pg = self.result_pages()
            num_pages = 0
            self.df_list = []
            for i in range(1,max_p+1):
                time.sleep(5)
                links = []
                link = self.browser.find_elements('xpath',"//div[@class='d6767e681c']//a")
                for l in link:
                    links.append(l.get_attribute('href'))
                hotels = self.browser.find_elements('xpath','//div[@class="f6431b446c a15b38c233"]')
                ratings = self.browser.find_elements('xpath','//div[@class="a3b8729ab1 d86cee9b25"]')
                prices = self.browser.find_elements('xpath','//span[@class="f6431b446c fbfd7c1165 e84eb96b1f"]')
                districts_list = []
                districts = self.browser.find_elements('xpath','//span[@class="aee5343fdb def9bc142a"]')
                for i in districts:
                    if ', barcelona' in i.text.lower():
                        districts_list.append(i)
                #retrieving only center distances / Confirm why the filter worked despite not having the right span class in all cases
                distance_center = []
                distance = self.browser.find_elements('xpath','//div[@class="abf093bdfe ecc6a9ed89"]//span[@class="f419a93f12"]')
                for i in distance:
                    if 'centro' in i.text:
                        distance_center.append(i)
                for a, b, c, d, e, f in zip(hotels, ratings, distance_center,districts_list, prices, links):
                    try:
                        row_data = {'Hotels': a.text, 'Ratings': b.text, 'Distance': c.text, 'District': d.text, 'Price': e.text, 'Link': f}
                        print(row_data)
                        self.df_list.append(row_data)
                    except Exception as e:
                        row_none = {'Hotels': None, 'Ratings': None, 'Distance': None, 'District': None,'Price':None, 'Link': None}
                        self.df_list.append(row_none)
                        print(row_none)
                wait = WebDriverWait(self.browser, 10)  # Adjust the timeout as needed
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, x_path)))
                next_button.click()
                num_pages += 1
            self.df = pd.DataFrame(self.df_list)
        
    def scrape_results_2(self, max_p, district_filter):
        num_pages = 0
        self.df_list = []
        #Click page path
        x_path = '/html/body/div[4]/div/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[4]/div[2]/nav/nav/div/div[3]/button/span/span'

        for i in range(1, max_p):
            time.sleep(7)
            links = []
            try:
                link = self.browser.find_elements('xpath', "//div[@class='d6767e681c']//a")
                for i in link:
                    links.append(i.get_attribute('href'))
            except NoSuchElementException:
                links.append(np.nan)

            hotels_list = []
            try:
                hotels = self.browser.find_elements('xpath', '//div[@class="f6431b446c a15b38c233"]')
                for hotel in hotels:
                    hotels_list.append(hotel.text)
            except NoSuchElementException:
                hotels_list.append(np.nan)

            prices_list = []
            try:
                prices = self.browser.find_elements('xpath', '//span[@class="f6431b446c fbfd7c1165 e84eb96b1f"]')
                for price in prices:
                    prices_list.append(price.text)
            except NoSuchElementException:
                prices_list.append(np.nan)

            districts_list = []
            try:
                districts = self.browser.find_elements('xpath', '//span[@class="aee5343fdb def9bc142a"]')
                for i in districts:
                    #', valencia'
                    if district_filter in i.text.lower():
                        districts_list.append(i.text)
            except NoSuchElementException:
                districts_list.append(np.nan)
            except:
                districts_list.append(np.nan)

            # Retrieving only center distances
            distance_center = []
            try:
                distance = self.browser.find_elements('xpath', '//div[@class="abf093bdfe ecc6a9ed89"]//span[@class="f419a93f12"]')
                for i in distance:
                    if 'centro' in i.text:
                        distance_center.append(i.text)
            except NoSuchElementException:
                distance_center.append(np.nan)
            except:
                distance_center.append(np.nan)
        ## Ratings and Comments
            ratings_list = []
            try:
                ratings = self.browser.find_elements('xpath', '//div[@class="a3b8729ab1 d86cee9b25"]')
                for rate in ratings:
                    ratings_list.append(rate.text)
            except NoSuchElementException:
                ratings_list.append(np.nan)
            comment_list = []
            try:
                comentarios = self.browser.find_elements('xpath', '//div[@class="abf093bdfe f45d8e4c32 d935416c47"]')
                for com in comentarios:
                    comment_list.append(com.text)
            except:
                comment_list.append(np.nan)

            for a, b, c, d, e, f, g in zip(hotels_list, distance_center, districts_list, prices_list,ratings_list,comment_list, links):
                row_data = {'Hotels': a, 'Distance': b, 'District': c, 'Price': d, 'Rating': e, 'Comments': f, 'Link': g}
                print(row_data)
                self.df_list.append(row_data)

            wait = WebDriverWait(self.browser, 10)  # Adjust the timeout as needed
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, x_path)))
            next_button.click()
            num_pages += 1
        self.df = pd.DataFrame(self.df_list)



    def test1(self):
        descriptions = []
        path = '/Users/mikelgallo/repos2/Bookings/mikel_folder'
        links = self.df['Link'].tolist()
        for i in tqdm(links, desc="Processing Links"):
            URL = f'{i}'

            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'}
            response = requests.get(URL, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            div = soup.find('div', {'id': 'property_description_content'})

            # Find all p elements with a specific class within the div
            specific_class_p_elements = div.find_all('p', class_='a53cbfa6de b3efd73f69')
            
            for p in specific_class_p_elements:
                descriptions.append(p.get_text(strip=True))
        return descriptions