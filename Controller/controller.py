import sys
sys.path.append('..')
from Database.database_manager import Database
from data_types import Preference
from data_types import EventimEvent
from EventExtractor.eventExtractor import Extractor
from ReservationEngine.Booking import Booking

#those should be deleted
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DATABASE_FILE_PATH = "eventim.db"

class Controler :
    
    def __init__(self) -> None :
        self.db = Database(DATABASE_FILE_PATH)

    def setPreference(self, pref : Preference) :
        self.db.setPreference(pref)

    def getEvents(self) -> list[EventimEvent] :
        userPrefs = self.db.getPreference()
        self.db.deleteAllEventimEvents()
        extractor = Extractor(self.db)
        extractor.saveEvenetsOfPrefferedTypes(userPrefs)
        return self.db.getAllEventimEvent()
    
    def pickEvent(self, link : str) :
        booking = Booking()
        booking.openLink(link)
