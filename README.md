# Search_Tests
The system designed to test the effects of search engine personalization. It allows performing search with the browser agent designed to trigger personalization and the incognito browser agent and compare the results.
The system consists of two classes: Personal_Browser and Incognito_Browser.  

Personal class can be personalized with one of the following methods or their combination: a) visiting websites from the list, searching within the domain and collecting cookies; c) using domain URLs as search queries; d) searching for keywords from the list and clicking on specified domains if present in the SERP results. Personal instance stores data on unique id, group name, browser agent options and driver, search engine name, collected cookies, clicked pages from SERP.

Incognito class avoids personalization using one of the following methods or their combination: by a) clearing cookies and history after each query b) reinitializing browser driver after each query; Incognito instance stores data on unique id, group name, browser agent, browser agent options and driver, search engine name.
The search methods of Personal and Incognito instances return the results for the query in a Pandas data frame format.
