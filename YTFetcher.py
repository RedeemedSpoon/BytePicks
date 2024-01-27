from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

# This program may no longer work because of changes in the YouTube UI changes or selenium
# For this to work perfectly, use a VPN with the country you want to search in and for the language you want
# This only work on Firefox, you can use chrome or something else by changing the driver in the line bellow

driver = webdriver.Firefox()
driver.get("https://youtube.com")
search_bar = driver.find_element(By.NAME, "search_query")
search_bar.send_keys("programming")
search_bar.send_keys(Keys.RETURN)
