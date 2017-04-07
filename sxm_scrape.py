from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path

import pandas as pd
import datetime

#Initialize web scraping
driver = webdriver.PhantomJS('./phantomjs-2.1.1-windows/bin/phantomjs.exe')

#Set sites to scrape
BPM = 1
ELECTRIC_AREA = 1
CLUB_LIFE = 0

def get_html (url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup;


def extract_song (soup): #Get current song title, artist, and albumart from siriusxm website
    song = {}
    song["Date"] = datetime.date.today().strftime("%Y-%m-%d")
    song["Time"] = datetime.date.today().strftime("%H:%M:%S")
    try:
        song["Title"] = soup.find_all(class_="onair-pdt-song")[0].contents[0]
        song["Artist"] = soup.find_all(class_="onair-pdt-artist")[0].contents[0]
        for pic in soup.findAll('img'):
            if pic.parent.get('id') == 'onair-pdt':
                song["Album Art URL"] = pic.get('src')
        return song
    except IndexError:
        print("No song playing...")
        return;

    
def open_history(url, path): 
    test_path = Path(path)
    
    if test_path.is_file():
        history = pd.read_csv(path,index_col=0)
        rows = len(history.index)
        print("Table Loaded from", path)
    else:
        bpm_soup = get_html(url)
        song = extract_song(bpm_soup)
        if song is not None:
            history = pd.DataFrame(song, columns = ["Artist", "Title", "Album Art URL", "Date", "Time"], index = [0])
            history.to_csv(path)
            print("Table Created @", path)
            return history;
        else:
            print("Table NOT Created (no song playing).")
            return;
            
# if not(bpm_history.to_dict('records')[rows-1] == song):
# bpm_history = bpm_history.append(song, ignore_index = True)
# print("Row Added")
    


def set_paths():
    urls = []
    history_paths = []
    if BPM == 1:
        urls.append("http://www.siriusxm.com/bpm")
        history_paths.append(r"c:\users\mringqui\desktop\bpm_history.dat")
    if ELECTRIC_AREA == 1:
        urls.append("http://www.siriusxm.com/electricarea")
        history_paths.append(r"c:\users\mringqui\desktop\electric_area_history.dat")
    if CLUB_LIFE == 1:
        urls.append("http://www.siriusxm.com/tiesto")
        history_paths.append(r"c:\users\mringqui\desktop\club_life_history.dat")
    return urls, history_paths
    
def main():
    urls, history_paths = set_paths()
    for url,path in zip(urls,history_paths):
        history = open_history(url, path)
    
    return;

main()