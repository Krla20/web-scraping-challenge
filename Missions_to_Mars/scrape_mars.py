# Declare dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pandas as pd
import os
import time
import requests

def init_browser():
    # added path to my chromedrive since on the exc #10 that's the only way it ran
    executable_path = {"executable_path": "/Users/Owner/.wdm/drivers/chromedriver/win32/88.0.4324.96/chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

# NASA Mars News

def scrape():

    # Initiate browser
    browser = init_browser()
    mars_dict = {}
    


    # Visit NASA News url through splinter module

    # URL of page to scrape "https://mars.nasa.gov/news/"
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # HTML object
    html= browser.html

    # Parse HTML with bs
    soup= bs(html,'lxml')

# Retrieve the latest element that contains news title and news_paragraph
# review here why it gets stuck the 1st time and then runs
    news_title= soup.find_all('div', class_='content_title')[1].text
    news_p = soup.find('div', class_='article_teaser_body').text

# Mars Facts
# Scrape Mars facts from https://space-facts.com/mars/

        # Visit Mars facts url 
    url = 'http://space-facts.com/mars/'
    browser.visit(url)

        # Use Pandas to "read_html" to parse the URL
    tables = pd.read_html(url)

    #Find Mars Facts DataFrame in the lists of DataFrames
    planet_df = tables[0]

    #Assign the columns
    planet_df.columns = ['Description', 'Fact']
    html_table = planet_df.to_html(table_id="html_tbl_css",justify='left',index=False)

    # Use Pandas to convert the data to a HTML table string
    html_table= planet_df.to_html()

    # html_table_dict = planet_df.to_dict(orient='records') #orient='records' set up parameters

    html_table.replace('\n','')
# Ctrl + [ / ] to indent in or out respectively
# Mars Hemisphere

    # store the main url (then need to set up the partial_images url in the forloop)
    hemispheres_main_url= 'https://astrogeology.usgs.gov'

    # Hermispheres url with splinter module
    hemispheres_url= 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(hemispheres_url)

    # HTML Object
    html_hemispheres= browser.html

    # Parse html with Beatiful Soup bs
    soup= bs(html_hemispheres, 'lxml')

    # Extract the hemispheres items url
    hemispheres= soup.find('div', class_= 'collapsible results')
    hemispheres_items= hemispheres.find_all('div', class_= 'item')

    hemisphere_image_urls=[]

        # Loop through the items previously stored
    for item in hemispheres_items:
    
    # Error handling
        try:
        
            # Extract title
            hemisp= item.find('div', class_= 'description')
            title= hemisp.h3.text
                
            # Extract image
            hemisp_url=hemisp.a['href']
            browser.visit(hemispheres_main_url + hemisp_url)
            html= browser.html
            soup= bs(html, 'lxml')
            img_url= soup.find('li').a['href']
            if (title and img_url):
            
                #Print results
                print('*'*100)
                print(title)
                print(img_url)
                
            # Dictionary to be inserted as a MongoDB document
            images_dict= {
                'title': title,
                'img_url': img_url
            }
            
            hemisphere_image_urls.append(images_dict)
            
        except Exception as error:
            print(error)
        
        # Create dictionary for all info scraped from sources above
    mars_dict={
        "news_title":news_title,
        "news_p":news_p,
        "html_table":html_table,
        # "html_table_dict":html_table_dict,
        "hemisphere_images":hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return mars_data dictionary 

    return mars_dict


