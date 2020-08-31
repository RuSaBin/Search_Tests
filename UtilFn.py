# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 15:18:48 2020

@author: rutab

"""
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from bs4.element import Tag
import csv
import time
import random
from selenium.webdriver.common.keys import Keys
from selenium import webdriver  
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
from os.path import isfile
import pickle
from urllib.parse import urlsplit


    
def dump_cookies(cookies):
    try:
        pickle.dump( cookies , open("cookies.pkl","wb"))
    except Exception as e:
        print(e)
   
#finds only organic results
def get_url(driver): #gets SERP urls 
    soup = BeautifulSoup(driver.page_source,'lxml')
    serp = soup.find_all('div', attrs={'class': 'g'})
    

    urls = []#page urls
    titles = []#page titles
    for r in serp:
        
        try:
            url = r.find('a', href=True)
            title = None
            title = r.find('h3')
    
            if isinstance(title,Tag):
                title = title.get_text()
    
      
            if url != '' or title != '':
               
                 url = url['href']
                 if "/search?q" not in url:
                      urls.append(url)
                      titles.append(title)
        except Exception as e:
            print(e)
            continue
        
    return urls, titles



#gets all serp results
def getall_url(driver):
    results = driver.find_elements_by_tag_name('a')
    urls = []#page urls
    titles = []#page titles
    for item in results:
        
        try:
            url = item.get_attribute('href')
            title = ""
            title = item.text
      
            if url != '' or title != '':
                urls.append(url)
                titles.append(title)
      
        except Exception as e:
            print(e)
            continue
        
    return urls, titles
    

def read_tolist(path): #gets list of keywords or linsk from the csv file
    list = []
    if isfile(path):
        try:
            with open(path) as f:
               reader = csv.reader(f)
               for lines in reader:
                   if len(lines)>0:
                       list.append(lines[0])
                 
    
        except Exception as e:
                print(e)
                
    return list
   
#clears all history      
def clear_all(driver):
    driver.delete_all_cookies() #clear cookies
    try:
        driver.get('chrome://settings/clearBrowserData')
        time.sleep(random.uniform(2,4))
        driver.find_element_by_xpath('//settings-ui').send_keys(Keys.ENTER)
        time.sleep(random.uniform(2,4))
        print("History is cleared")
    except Exception as e:
                print(e)

def create_driver(option_list):
    option_list = option_list
    options = webdriver.ChromeOptions()
    if option_list is not None:
        for opt in option_list:
            try:
                options.add_argument(opt)
            except Exception as e:
                    print(e)

    #options.add_argument("--headless")
    options.add_argument('disable-infobars')
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--enable-automation")
    options.add_argument("--disable-infobar")
    options.add_argument("--disable-impl-side-painting")
    options.add_argument("--lang=en-GB")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("safebrowsing_for_trusted_sources_enabled")
    #options.add_argument("--incognito")
    #options.add_argument('--proxy-server=1.2.3.4:8080')
    #options.add_argument('--disable-gpu') if os.name == 'nt' else None # Windows workaround
    #options.add_argument("--verbose")
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    return driver
 

# set geo location
def set_geolocation(driver, lat, long, acc):
     
    params = {"latitude": lat, "longitude": long,"accuracy": acc}
    
    driver.execute_cdp_cmd("Page.setGeolocationOverride", params)
    time.sleep(random.uniform(2,6))
    print("geolocation is set to ", lat, long, acc)
    
    

def to_df(driver, results, id, time_stamp, keyword, group, urls, titles):
    try:
        data = pd.DataFrame({'ID': id, 'Group': group, 'Time_Stamp': time_stamp,'Keyword': keyword, 'Urls': urls, 'Titles': titles})
        assert isinstance(data, object), "Empty data"
        if results.empty: 
            results_new = data
        else:
            frames = [results, data] #add to existing df
            results_new = pd.concat(frames)
        
        return results_new
            
    except Exception as e:
                print(e) 
    
def sleep(x,y):
    t = random.uniform(x,y)          
    print("Will sleep for: ", t)
    time.sleep(t) 
    
def search_click(driver, search, keyword, clicked_pages):
    in_page = None
    if search:
        keys = ["q", "search"]
        for key in keys:
             try:
                #find searchbox
                searchbox = driver.find_element_by_name(key)
                searchbox.clear()
                searchbox.send_keys(keyword)
                print("Searching for ", keyword)
                sleep(2,6)         
                #perform search
                searchbox.submit()            
                sub_page = driver.find_element_by_partial_link_text(keyword)
                sub_page.click()
                in_page = driver.current_url
                clicked_pages.append(in_page)
             except Exception:
                continue
    if in_page is None:
        print("Did not click in page")
    else:
        print("Clicked on ", in_page)
         
    
def get_domain(string):
    domain = domain = "{0.netloc}".format(urlsplit(string))
    return domain

'''    
def get_topstories(driver):
    serp = soup.find_all('g-inner-card', attrs={'class': 'kno-fb-ctx stOtnd cv2VAd'})
    serp[0]
    serp[1]
    serp[2]
'''