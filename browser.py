from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager



def search(something):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.maximize_window()
    browser.get('https://www.google.com/')    
    findElem = browser.find_element_by_name('q')
    findElem.send_keys(something)
    findElem.send_keys(Keys.RETURN)