# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 16:34:33 2020

@author: rutab
The Incognito class avoids personalization using one of the following methods or 
their combination: a) clearing cookies and history after each query 
b) reinitializing the browser driver after each query. The Incognito 
instance stores data on unique id, browser agent options and driver, 
search engine name.
"""
import Control.UtilFn as u
import time
import datetime
import random
import pandas as pd
import uuid
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Incognito_Browser(object):
    
     def __init__(self, searchengine, option_list):
        
        self.id = str(uuid.uuid1()) #unique id
        self.group = "Control_" #personalized group
        self.options = option_list if isinstance(option_list, list) else ["--disable-extensions", "--disable-popup-blocking", "--incognito" ]
        self.search_engine = searchengine
        self.driver = None
        self.filename = '{}{}'.format(self.group, self.id)
       # self.suggestions = []
        
     def exit_all(self):
         self.driver.close()
         self.driver.quit()
         print("Exit successful")
         
     def get_suggestions(self, keywords):
         suggestions = []
         driver = u.create_driver(self.options) 
         self.driver = driver
         driver.get(self.search_engine)
         for keyword in keywords:
            searchbox = self.driver.find_element_by_name("q")
            searchbox.clear()
            searchbox.send_keys(keyword)
            u.sleep(1,1)
         try: 
            elements = self.driver.find_elements_by_xpath("//form[@action='/search' and @role='search']//ul[@role='listbox']//li//span")
            for element in elements:
                if element.text:
                    suggestions.append(element.text)
         except Exception as e:
                print(e)
         df = pd.DataFrame({'Keyword': keyword, 'Suggestions':suggestions})
         return df
         

     def incognito_search(self,keywords):
        
         results = pd.DataFrame([])
         start = datetime.datetime.now()
         assert isinstance(keywords, list), 'Add list of keywords'
         for keyword in keywords:
             try:

                driver = u.create_driver(self.options) 
                self.driver = driver
                u.clear_all(driver) #clears all history
                driver.get(self.search_engine)
                print("Current page: ", driver.current_url)
                input_element = driver.find_element_by_name("q")
                input_element.clear()
                input_element.send_keys(keyword)
                u.sleep(1,3)
                print("Searching for ", keyword)
                time.sleep(random.uniform(2,6))
                #perform search
                input_element.submit()
                #get time and construct file name
                time_stamp = str(datetime.datetime.now())
                #Getting the url search results (SERP)
                urls, titles = u.get_url(self.driver)
                assert len(urls)>0, 'Empty urls'
                assert len(titles)>0, "Empty titles"
                results = u.to_df(driver, results, self.id, time_stamp, keyword, self.group, urls, titles)
                #self.exit_all()
             except Exception as e:
                print(e)
         
         end = datetime.datetime.now()
         print("Start: ", start)
         print("End: ", end)
         print("Elapsed time: ", end-start)
         return results


