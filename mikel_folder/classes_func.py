#Packages

import json
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium import webdriver
import os
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
            self.df = []
            for i in range(1,max_p+1):
                time.sleep(5)
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
                for a, b, c, d, e in zip(hotels, ratings, distance_center,districts_list, prices):
                    try:
                        row_data = {'Hotels': a.text, 'Ratings': b.text, 'Distance': c.text, 'District': d.text, 'Price': e.text}
                        print(row_data)
                        self.df.append(row_data)
                    except Exception as e:
                        row_none = {'Hotels': None, 'Ratings': None, 'Distance': None, 'District': None,'Price':None}
                        self.df.append(row_none)
                        print(row_none)
                wait = WebDriverWait(self.browser, 10)  # Adjust the timeout as needed
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, x_path)))
                next_button.click()
                num_pages += 1