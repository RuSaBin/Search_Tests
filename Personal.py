# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 14:56:34 2020

@author: rutab
The Personal class can be personalized by searching for keywords from the provided list and clicking on 
specified domains or links containing specified keywords if they are present in 
the SERP results. Personal instance stores data on unique id, browser agent 
options and driver, search engine name, collected cookies. 
The search method of the Personal class can perform search and collect SERP 
results or autocomplete suggestions without clicking on the SERP results if specified.
We use this option in all the control runs of experiments.
"""

import Control.UtilFn as u
import time
import datetime
import random
import pandas as pd
import uuid
from retry import retry
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class Personal_Browser(object):
    
     def __init__(self, searchengine, option_list):
        
        assert isinstance(option_list, list), 'Add list of string options'
        self.id = str(uuid.uuid1()) #unique id
        self.group = "Personal_" #personalized group
        self.options = option_list if isinstance(option_list, list) else ['--disable-web-security', '--allow-running-insecure-content',  "profile.managed.second_custodian_email",  "media_feeds_background_fetching_enabled", "restore-last-session", "--profile-directory=Default" ]
        self.search_engine = searchengine
        self.driver = u.create_driver(self.options)# initialize driver
        self.filename = '{}{}'.format(self.group, self.id)
        self.clicked_serp=[]
        self.cookies = []
        #self.suggestions = []
      
        
                     
     
        
     #logging in   
     def login(self, username, password):
         try:
            self.driver.get("https://accounts.google.com/signin")
            u.sleep(3,5)
            field = self.driver.find_element_by_id("identifierId")
            field.send_keys(username)
            button = self.driver.find_element_by_id("identifierNext")
            button.click()
            field = self.driver.find_element_by_name("password")
            field.send_keys(password)
            u.sleep(3,5)
            button = self.driver.find_element_by_id("passwordNext")
            button.click()
            print("Logged in successfuly")
            self.new_tab(self)
         except Exception as e:
                print(e)
                
                
     # close window and driver          
     def exit_all(self):
         self.driver.close()
         self.driver.quit()
         print("Exit successful")
    
     def cookies_fromlist(self, path):
        try:
            cookies = pickle.load(open(path, "rb"))
            self.cookies = cookies
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
                print(e)
        return print("Added cookies")
    
     
    
    
    #browses pages from list. If search is true, searches for keyword
     def browse_pages(self,url_p):
         visited = []
         start = datetime.datetime.now()
         url_p = url_p
         l = len(url_p)
         print("Number of pages to visit: ", l)
         #randomize the sequence of pages
         indices = random.sample(range(l), l)
         for i in range(l):
             print(i+1, " out of ", l)
             page_num = indices[i]
             page = url_p[page_num]
             try:
                self.driver.get(page)
                visited.append(page)
                print("Now on page: ", page)
                self.cookies.append(self.driver.get_cookies())
                u.sleep(10,20)
             except Exception as e:
                    print(e)
                    continue
             
         end = datetime.datetime.now()
         print("Start: ", start)
         print("End: ", end)
         print("Elapsed tim: ", end-start)
         return visited
         
        
        
    
    
     def personal_search(self,keywords, url_p): 
         url_p = url_p
         results = pd.DataFrame([])
         start = datetime.datetime.now()
         try:
             if self.search_engine not in self.driver.current_url:
                 self.driver.get(self.search_engine)
                 print("Current page: ", self.driver.current_url)
         except Exception as e:
                print(e)  
         print("Number of keywords: ", len(keywords))
         i = 1
    
         for keyword in keywords:
                 
            try:
                time.sleep(random.uniform(1,5)) 
                searchbox = self.driver.find_element_by_name("q")
                searchbox.clear()
                searchbox.send_keys(keyword)
                print("Searching for ",i, keyword)
                i = i+1
                u.sleep(10,20)
                #perform search
                searchbox.submit()
                #get time and construct file name
                time_stamp = str(datetime.datetime.now())
                time.sleep(random.uniform(1,5)) 
                urls, titles = u.get_url(self.driver)
                results = u.to_df(self.driver, results, self.id, time_stamp, keyword, self.group, urls, titles)
                #check if links in result and click if found
                if url_p is not None:
                    self.click_fromlist(url_p, keyword)
            except Exception as e:
                print(e)
                input("A problem occured. Resolve and press Enter to continue...")#check to resolve the problem manually
                time.sleep(random.uniform(1,5))
                continue
         end = datetime.datetime.now()
         print("Start: ", start)
         print("End: ", end)
         print("Elapsed time: ", end-start)
         return results
     
    
     def get_suggestions(self, keywords):
        suggestions = []
        try:
            if self.search_engine not in self.driver.current_url:
                self.driver.get(self.search_engine)
                print("Current page: ", self.driver.current_url)
        except Exception as e:
                print(e)  
        print("Number of keywords: ", len(keywords))
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
        
     @retry(exceptions=Exception, tries=3, delay=1)
     def click_fromlist(self, list, keyword):
         
         for link in list:
             try:
                 url = self.driver.find_element_by_partial_link_text(link)# check if name is in link
                 u.sleep(2,6)
             except Exception:
                     #print("Did not find ", link)
                     continue
             if url is not None:
                 try:
                     url.click()
                     print("Clicked on ", self.driver.current_url)
                     case = {'Keyword': keyword, 'Url': self.driver.current_url, 'Title': self.driver.title}
                     self.clicked_serp.append(case)
                     u.sleep(10,25)
                 except Exception as e:
                     print(e)
                     self.driver.back() 
                     continue
                 self.driver.back() 
                 
                 
     def new_tab(self):
         
         self.driver.execute_script("window.open('','_blank');")
         self.driver.switch_to_window(self.driver.window_handles[1]) 
         
