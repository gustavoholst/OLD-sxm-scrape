from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import datetime

##Set value to 1 if first time running on this machine (no history file to start with)
FIRSTRUN = 1

#Initialize web scraping
driver = webdriver.PhantomJS('./phantomjs-2.1.1-windows/bin/phantomjs.exe')


def get_html (url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup;


def extract_song (soup): #Get current song title, artist, and albumart from siriusxm website
    song = {}
    song["Date"] = datetime.date
    song["Time"] = datetime.time
    try:
        song["Title"] = soup.find_all(class_="onair-pdt-song")[0].contents[0]
        song["Artist"] = soup.find_all(class_="onair-pdt-artist")[0].contents[0]
        for pic in soup.findAll('img'):
            if pic.parent.get('id') == 'onair-pdt':
                song["Album Art URL"] = pic.get('src')
        return song
    except IndexError:
        print("no song playing...")
        return

    
def main():
    url = "http://www.siriusxm.com/bpm"
    bpm_soup = get_html(url)
    song = extract_song(bpm_soup) ##TODO: Fix error handling
    
    if FIRSTRUN == 1:
        bpm_history = pd.DataFrame(list(song.items()), columns = ["Date", "Time", "Title", "Artist", "Album Art URL"], index=[0])
        print("Table Created")
        FIRSTRUN == 0
    else:
        bpm_history = pd.read_csv(r"c:\users\mringqui\desktop\bpm_history.csv",index_col=0)
        rows = len(bpm_history.index)
        if not(bpm_history.to_dict('records')[rows-1] == song):
            bpm_history = bpm_history.append(song, ignore_index = True)
            print("Row Added")
    
    bpm_history.to_csv(r"c:\users\mringqui\desktop\bpm_history.csv")
    return;

main()