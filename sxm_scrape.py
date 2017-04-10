from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path

import pandas as pd
import datetime
import sched
import time

#Initialize web scraping
driver = webdriver.PhantomJS('./phantomjs-2.1.1-windows/bin/phantomjs.exe')
driver.implicitly_wait(10)

#Set sites to scrape
BPM = 1
ELECTRIC_AREA = 0
CLUB_LIFE = 0


def get_html (url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup;

    
def set_channels():
    channels = []
    urls = []
    history_paths = []
    if BPM == 1:
        channels.append("BPM")
        urls.append("http://www.siriusxm.com/bpm")
        history_paths.append(r"..\..\bpm_history.dat")
    if ELECTRIC_AREA == 1:
        channels.append("Electric Area")
        urls.append("http://www.siriusxm.com/electricarea")
        history_paths.append(r"c:\users\mringqui\desktop\electric_area_history.dat")
    if CLUB_LIFE == 1:
        channels.append("Tiësto's Club Life")
        urls.append("http://www.siriusxm.com/tiesto")
        history_paths.append(r"c:\users\mringqui\desktop\club_life_history.dat")
    return channels, urls, history_paths
    
    
def extract_song (soup): #Get current song title, artist, and albumart from siriusxm website
    song = {}
    song["Date"] = datetime.date.today().strftime("%Y-%m-%d")
    song["Time"] = time.strftime("%H:%M:%S")
    try:
        song["Title"] = soup.find_all(class_="onair-pdt-song")[0].contents[0]
        song["Artist"] = soup.find_all(class_="onair-pdt-artist")[0].contents[0]
        for pic in soup.findAll('img'):
            if pic.parent.get('id') == 'onair-pdt':
                song["Album Art URL"] = pic.get('src')
        print("Currently playing: ", song["Title"], " by ", song["Artist"])
        return song
    except IndexError:
        print("Could not get song...")
        return;

    
def open_history(url, path): 
    test_path = Path(path)
    
    if test_path.is_file():
        history = pd.read_csv(path,index_col=0)
        print("Table Loaded from", path)
        return history;
    else:
        soup = get_html(url)
        song = extract_song(soup)
        if song is not None:
            history = pd.DataFrame(song, columns = ["Artist", "Title", "Album Art URL", "Date First Played", "Date Last Played", "Time Last Played", "Total Plays"], index = [0])
            history.to_csv(path)
            print("Table Created @", path)
            return history;
        else:
            print("Table NOT Created (no song playing).")
            return;

            
def add_song(history_table,url,path):
    soup = get_html(url)
    song = extract_song(soup)
    rows = len(history_table.index) 
    if song is not None:
        if not(song["Title"] == history_table["Title"][rows-1]):
            artist_match = history_table[history_table["Artist"] == song["Artist"]]
            title_match = artist_match[artist_match["Title"] == song["Title"]] 
            if len(title_match.index.values > 0):
                history_table.loc[title_match.index.values]["Total Plays"] += 1
                history_table.loc[title_match.index.values]["Date Last PLayed"] = song["Date"]
                history_table.loc[title_match.index.values]["Time Last PLayed"] = song["Time"]
                print("Song Repeated!")
            else:
                new_row = {"Artist":song["Artist"], "Title":song["Title"], "Album Art URL":song["Album Art Url"], "Date First Played":song["Date"], "Date Last Played":song["Date"], "Time Last Played":song["Time"], "Total Plays":1}
                history_table = history_table.append(new_row, ignore_index = True)
                print("New Song Played!")
            history_table.to_csv(path)
    return history_table

    
def main():
    history = []
    channels, urls, history_paths = set_channels()
    
    for url,path in zip(urls,history_paths):
        history.append(open_history(url, path))
    
    try:
        while True:
            for i in range(len(history)):
                print("\nChecking", channels[i], flush=True)
                history[i] = add_song(history[i],urls[i],history_paths[i])
                print(channels[i], "checked at", time.strftime("%H:%M:%S"), flush=True)
            time.sleep(20)
    except KeyboardInterrupt:
        print('Excecution ended by user.', flush=True)
        driver.quit()
    return;

main()