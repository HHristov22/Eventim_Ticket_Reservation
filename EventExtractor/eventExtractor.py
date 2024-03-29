from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime

import time
import re
import sys
sys.path.append('..')

from data_types import EventimEvent
from data_types import Preference
from Database.database_manager import Database
from EventExtractor.booking_constants import PAGE_NAME, ACCEPT, EVENTS, LIST_OF_LINKS

DEFAULT_WAIT_TIME = 10
SMALL_WAIT_TIME = 2

LINK_IDENTIFIERS_CONCERTS = ['concerts', 'muzika/narodna_muzika']
LINK_IDENTIFIERS_CULTURE = ['kultura']
LINK_IDENTIFIERS_SPORT = ['sport']
LINK_IDENTIFIERS_FAMILY = ['semeistvo', 'zabavlenija_razni', 'panair', 'party']
LINK_IDENTIFIERS_OTHER= ['drugi']

# Extracts events from the site based on the preferences
# The Database acts as a input/output from it the preferences are taken and into it the events are inserted
class Extractor:
    def __init__(self, database : Database) :
        self.database = database

    def saveEvenetsOfPrefferedTypes(self, userPrefs : Preference) :
        self.__createWebDriver()

        prefferedType = self.database.getPreference().types[0]
        
        if prefferedType  == 'concert':
            concertLinks = self.__extractAllLinksFor(LINK_IDENTIFIERS_CONCERTS)
            self.__saveEventsOfType(userPrefs, concertLinks, 'concert')
            
        elif prefferedType  == 'family':
            familyLinks = self.__extractAllLinksFor(LINK_IDENTIFIERS_FAMILY)
            self.__saveEventsOfType(userPrefs, familyLinks, 'family')
            
        elif prefferedType  == 'culture':
            cultureLinks = self.__extractAllLinksFor(LINK_IDENTIFIERS_CULTURE)
            self.__saveEventsOfType(userPrefs, cultureLinks, 'culture')
            
        elif prefferedType  == 'sport':
            sportLinks = self.__extractAllLinksFor(LINK_IDENTIFIERS_SPORT)
            self.__saveEventsOfType(userPrefs, sportLinks, 'sport')

        elif prefferedType  == 'other':
            otherLinks = self.__extractAllLinksFor(LINK_IDENTIFIERS_OTHER)
            self.__saveEventsOfType(userPrefs, otherLinks, 'other')
        
        self.driver.close()

    def __createWebDriver(self) :
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--headless=new')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(DEFAULT_WAIT_TIME)
        
    def __connectWithWebPage(self):
        self.driver.get(PAGE_NAME)
        self.driver.maximize_window()
        self.__acceptCookies()
        
    def __acceptCookies(self):
        try:
            linksForCookies = self.driver.find_elements("xpath", "//div[contains(@class, 'cookie-policy-action')]")
            for link in linksForCookies:
                if ACCEPT in link.get_attribute("innerHTML"):
                    link.click()
                    break
        except Exception as e:
            print("Error handling cookies:", str(e))
            return None

    def __openEventsMenu(self):
        self.__connectWithWebPage()
        try:
            link = self.driver.find_element("xpath", "//a[contains(text(), '{}')]".format(EVENTS))
            link.click()
        except NoSuchElementException:
            print("events link not found")
            return None

    def __extractAllLinksFor(self, identifiers) :
        self.__openEventsMenu()
        li_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li.m-mainMenu__listItemSubListItem')
        
        links = []
        for li in li_elements :
            a = li.find_element(By.CSS_SELECTOR, 'a')
            link = a.get_attribute('href')
            if link not in LIST_OF_LINKS :
                for identifier in identifiers :
                    if identifier in link :
                        links.append(link)
                        break
        
        return links
    
    def __saveEventsOfType(self, userPrefs : Preference, links, event_type): # links - contanis all links for different type in one category

        events = []
        
        for link in links :
            self.driver.get(link)
            
            if self.__noEventsInPage() :
                continue

            self.__loadMoreElementsIfAvailable()
            
            eventListItems = self.driver.find_elements(By.CLASS_NAME, "m-eventListItem")
            for item in eventListItems :
                eventimEvent = self.__processEventListItem(userPrefs, item)
                if eventimEvent is None:
                    continue
                eventimEvent.type = event_type
                events.append(eventimEvent)  

        for event in events :
            self.database.insertEventimEvent(event)

    def __noEventsInPage(self) :
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, "m-blockNotice")
            for element in elements :
                if element.text == "По Вашите критерии не бяха намерени резултати" :
                    return True       

        except NoSuchElementException:
            pass

        return False
    
    def __loadMoreElementsIfAvailable(self) :
        # When there is no label it takes a lot of time to load, that's why a smaller wait time is set to not waste time
        self.driver.implicitly_wait(SMALL_WAIT_TIME)
        try:
            element = self.driver.find_element(By.CLASS_NAME, "a-pagination_loadMoreLabel")
            if len(element) > 0 and element.text == "Покажи още" :
                element.click()
        except :
            pass
        self.driver.implicitly_wait(DEFAULT_WAIT_TIME)
        
    def __extractDate(self, date_string) : 
        datetime_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S%z")
        return datetime_obj.strftime("%d.%m.%Y")
           
    def __extractTime(self, time_string) :
        datetime_obj = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S%z")
        return datetime_obj.strftime("%H")
           
    def __timeAsDayPart(self, time):
        if time >= 6 and time <= 12:
            return "Morning (6-12)"
        if time >= 11 and time <= 16:
            return "Afternoon (11-16)"
        if time >= 15 and time <= 19:
            return "Evening (15-19)"
        if time >= 18 and time <= 24:
            return "Night (18-24)"
        
        return ""
    
    def __processEventListItem(self, userPrefs : Preference, item : WebElement) -> EventimEvent:
        nameElement = item.find_element(By.CLASS_NAME, "m-eventListItem__title")
        name = nameElement.get_attribute("innerHTML")

        venueElement = item.find_element(By.CLASS_NAME, "m-eventListItem__venue")
        addressElement = item.find_element(By.CLASS_NAME, "m-eventListItem__address")
        location = venueElement.text + " " + addressElement.text

        dateAndTimeElement = item.find_element(By.CSS_SELECTOR, "*[itemprop='startDate']")
        dateAndTime = dateAndTimeElement.get_attribute("content").replace("T", " ", 1)
        formatedDate = self.__extractDate(dateAndTime)
        formatedTime = self.__timeAsDayPart(int(self.__extractTime(dateAndTime)))
        
        print (formatedTime)
        linkElement = item.get_attribute('href')
                    
        if str(formatedDate) in userPrefs.dates and formatedTime in userPrefs.dayParts:
            return EventimEvent(name, "", location, dateAndTime, "None", linkElement)            
        
        return None