#Packages

import json
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium import webdriver
import re
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
#Parallelization
from concurrent.futures import ThreadPoolExecutor

os.cpu_count()
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
    def __init__(self,city,start_day,end_day):
        dfolder='./downloads'
        #geko_path='/Users/mikelgallo/repos2/text_mining/Scraping_UN/books/geckodriver'
        geko_path='./driver/geckodriver'
        link='https://www.booking.com/index.es.html'
        self.browser= start_up(dfolder=dfolder,link=link,geko_path=geko_path)
        self.city = city
        #self.cnt_filt = ', barcelona' if self.city == 'Barcelona' else ', valencia'
        self.cnt_filt = f', {self.city.lower()}'
        self.start_day = start_day
        self.end_day = end_day
        self.num_pages = None
        self.df_list = None
        self.df = None
        self.desc_df = None
    
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
        wait = WebDriverWait(self.browser, 2)
        while not loop:
            #Extract dates from table
            time.sleep(1)
            dates_f = self.extract_dates()
            #Loop over dates and click if date of interest is found
            date_found_on_page = False
            # Flag to indicate whether the date is found on the current page
            for date in dates_f:
                if date.get_attribute("data-date") == date_k:
                    time.sleep(1)
                    date.click()
                    #print('click')
                    #print('found in',n_pg+1)
                    loop = True
                    date_found_on_page = True
                    break
            if date_found_on_page:
                #loop = True
                break  # Break out of the while loop if date is found on the current page
               
            n_pg +=1
            #print('date not found in page:',n_pg)
            #print('moving to next page')
            time.sleep(1)
            if n_pg <= 1:
                x_path = '//button[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 f671049264 deab83296e f4552b6561 dc72a8413c f073249358"]'
            else:
                x_path = '//button[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 f671049264 deab83296e f4552b6561 dc72a8413c f073249358"]'

            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, x_path)))
                next_button.click()
            except:
                # If the next button is not clickable, exit the outer loop
                print("Date not found on any page")
                break
            
 
    def search_results(self):
        #my_xpath='/html/body/div[3]/div[2]/div/form/div[1]/div[4]/button/span'
        my_xpath='//div[@class="e22b782521 d12ff5f5bf"]//button[@class="a83ed08757 c21c56c305 a4c1805887 f671049264 d2529514af c082d89982 cceeb8986b"]'

        #Click search button
        check_obscures(self.browser,my_xpath , type='xpath')
        check_and_click(self.browser,my_xpath , type='xpath')

    def result_pages(self):
        num_pages = 0
        a = self.browser.find_elements('xpath','//div[@data-testid="pagination"]//li[@class="b16a89683f"]')
        num_pages = int(a[-1].text)
        return num_pages
    


    def scrape_results(self,max_p):
        self.df_list = []
        wait = WebDriverWait(self.browser, 4)
        for num in range(1, max_p):
            links = []
            hotels_list = []
            prices_list = []
            districts_list = []
            distance_center = []
            ratings_list = []
            comment_list = []
            stars = []
            time.sleep(4)
            #hotel_overview = browser.find_elements('xpath','//div[@class="c066246e13"]')
            hotel_overview = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="c066246e13"]')))
            for hotel in hotel_overview:
                # Retrieve links (URL)
                try:
                    link = hotel.find_elements('xpath', ".//div[@class='d6767e681c']//a")
                    links.append(link[0].get_attribute('href'))
                except NoSuchElementException:
                    links.append(np.nan)
                # Retrieve Hotel names
                try:
                    hotels = hotel.find_elements('xpath', './/div[@class="f6431b446c a15b38c233"]')
                    hotels_list.append(hotels[0].text)
                except NoSuchElementException:
                    hotels_list.append(np.nan)
                # Retrieve Prices
                try:
                    prices = hotel.find_elements('xpath', './/span[@class="f6431b446c fbfd7c1165 e84eb96b1f"]')
                    prices_list.append(prices[0].text)
                except NoSuchElementException:
                    prices_list.append(np.nan)
                #Retrieve Districts
                try:
                    districts = hotel.find_elements('xpath', './/span[@class="aee5343fdb def9bc142a"]')
                    for i in districts:
                        if self.cnt_filt in i.text.lower():
                            districts_list.append(i.text)
                except NoSuchElementException:
                    districts_list.append(np.nan)
                except:
                    districts_list.append(np.nan)
                # Retrieving only center distances
                try:
                    distance = hotel.find_elements('xpath', './/div[@class="abf093bdfe ecc6a9ed89"]//span[@class="f419a93f12"]')
                    for i in distance:
                        if 'centro' in i.text:
                            distance_center.append(i.text)
                except NoSuchElementException:
                    distance_center.append(np.nan)
                except:
                    distance_center.append(np.nan)
                # Retrieve Ratings
                try:
                    ratings = hotel.find_elements('xpath', './/div[@class="a3b8729ab1 d86cee9b25"]')
                    ratings_list.extend([rate.text for rate in ratings])
                except NoSuchElementException:
                    ratings_list.append(np.nan)
                except:
                    ratings_list.append(np.nan)
                # Retrieve comments
                try:
                    comentarios = hotel.find_elements('xpath', './/div[@class="abf093bdfe f45d8e4c32 d935416c47"]')
                    comment_list.append(comentarios[0].text)
                except NoSuchElementException:
                    comment_list.append(np.nan)
                except:
                    comment_list.append(np.nan)
                try:
                    elements = hotel.find_elements('xpath', '//div[@class="b3f3c831be"][@aria-label]')
                    stars = [element.get_attribute('aria-label') for element in elements]
                except NoSuchElementException:
                    stars.append(np.nan)
                except:
                    stars.append(np.nan)
            
            for a, b, c, d, e, f, g, h in zip(hotels_list, distance_center, districts_list, prices_list,ratings_list,stars,comment_list, links):
                row_data = {'Hotels': a, 'Distance': b, 'District': c, 'Price': d, 'Rating': e, 'Stars': f, 'Comments': g, 'Link': h}
                #print(row_data)
                self.df_list.append(row_data)
        
    
            if num == 1:
                wait = WebDriverWait(self.browser, 5)  # Adjust the timeout as needed
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 deab83296e bb803d8689 a16ddf9c57"]')))
                print(f'page {num}')
                next_button.click()
            elif num == max_p:
                print('complete')
                break
            else:
                wait = WebDriverWait(self.browser, 5)  # Adjust the timeout as needed
                next_button = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 deab83296e bb803d8689 a16ddf9c57"]')))
                print(f'page {num}')
                if len(next_button) > 1:
                    next_button[1].click()
                else:
                    print("No more pages to click.")
                    break
                #next_button[1].click()
        self.df = pd.DataFrame(self.df_list)

    def scrape_descriptions(self):
            descriptions = []
            links = self.df['Link'].tolist()

            def process_link(link):
                URL = f'{link}'
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'}
                response = requests.get(URL, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                div = soup.find('div', {'id': 'property_description_content'})

                # Find all p elements with a specific class within the div
                specific_class_p_elements = div.find_all('p', class_='a53cbfa6de b3efd73f69')
                
                for p in specific_class_p_elements:
                    descriptions.append(p.get_text(strip=True))

            # Create a ThreadPoolExecutor to run operations in parallel
            threads = os.cpu_count()
            with ThreadPoolExecutor(max_workers= threads-5) as executor:
                # Use executor.map to apply the process_link function to each URL in parallel
                for i, descr in enumerate(tqdm(executor.map(process_link, links), total=len(links), desc="Processing Links")):
                    print(i,descr)
                    #if (i + 1) % 50 == 0 or (i + 1) == len(links):  # Check for the last batch as well
                        #print(f"Scraped {i + 1} links")
            self.df['descriptions'] = descriptions




    def scrape_descriptions1(self):
            descriptions = []
            links = self.df['Link'].tolist()
            hotels = self.df['Hotels'].tolist()

            def process_link(link):
                    try:
                        URL = f'{link}'
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'}
                        response = requests.get(URL, headers=headers)
                        response.raise_for_status()  # Raises HTTPError for bad responses
                        soup = BeautifulSoup(response.text, 'html.parser')

                        div = soup.find('div', {'id': 'property_description_content'})

                        if div is not None:
                            # Find all p elements with a specific class within the div
                            specific_class_p_elements = div.find_all('p', class_='a53cbfa6de b3efd73f69')

                            for p in specific_class_p_elements:
                                descriptions.append(p.get_text(strip=True))
                        else:
                            print(f"Error: 'property_description_content' div not found on {link}")
                            descriptions.append(np.nan)  # or any value you prefer for NaN
                    except Exception as e:
                        print(f"Error processing link {link}: {e}")
                        descriptions.append(np.nan)  # or any value you prefer for NaN
                    return descriptions

            # Create a ThreadPoolExecutor to run operations in parallel
            threads = os.cpu_count()
            descr_2 = []
            hotels2 = []
            with ThreadPoolExecutor(max_workers= threads-3) as executor:
                # Use executor.map to apply the process_link function to each URL in parallel
                for i, descr in zip(hotels,tqdm(executor.map(process_link, links), total=len(links), desc="Processing Links")):
                    descr_2.append((i,descr))
                    #hotels2.append(hote)
                    #descr_2.append((hote, descr))  # Append a tuple containing hotel and its descriptions
                
                print(descr_2[0])
                print(descr_2[4])
                print(descr_2[10])

    # Create a new DataFrame with the last two columns generated
            #self.desc_df = pd.DataFrame(descr_2, columns=['Hotels', 'Descriptions'])

            
            #self.desc_df = pd.DataFrame({'Hotels': hotels2, 'Descriptions': descr_2})
                    #if (i + 1) % 50 == 0 or (i + 1) == len(links):  # Check for the last batch as well
                    #print(f"Scraped {i + 1} links")
                

            # Unpack sorted descriptions into separate lists
            #sorted_links, sorted_descriptions = zip(*descriptions)

            #self.df['descriptions'] = descriptions
            #self.df['sorted_links'] = sorted_links
            #return descriptions


            # Perform any additional operations with descriptions as needed
