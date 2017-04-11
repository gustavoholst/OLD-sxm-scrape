from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path
from datetime import datetime

import pandas as pd
import sched
import time

#Initialize web scraping
driver = webdriver.PhantomJS('./phantomjs-2.1.1-windows/bin/phantomjs.exe')
driver.implicitly_wait(10)

#Set sites to scrape
BPM = 1
ELECTRIC_AREA = 1
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
        history_paths.append(r"..\bpm_history.dat")
    if ELECTRIC_AREA == 1:
        channels.append("Electric Area")
        urls.append("http://www.siriusxm.com/electricarea")
        history_paths.append(r"..\electric_area_history.dat")
    if CLUB_LIFE == 1:
        channels.append("Tiësto's Club Life")
        urls.append("http://www.siriusxm.com/tiesto")
        history_paths.append(r"..\club_life_history.dat")
    return channels, urls, history_paths
    
    
def get_song (url): #Get current song title, artist, and albumart from siriusxm website
    song = {}
    song["datetime"] = datetime.now()
    soup = get_html(url)
    for x in range(1,4):
        try:
            song["Title"] = soup.find_all(class_="onair-pdt-song")[0].contents[0]
            song["Artist"] = soup.find_all(class_="onair-pdt-artist")[0].contents[0]
            for pic in soup.findAll('img'):
                if pic.parent.get('id') == 'onair-pdt':
                    song["Album Art URL"] = pic.get('src')
            print("Currently playing: ", song["Title"], " by ", song["Artist"])
            return song
        except IndexError:
            print("Attempt[{}]: Could not get song... Retrying.".format(x))
            soup = get_html(url)
    return;

    
def open_history(channel,url, path): 
    test_path = Path(path)
    
    if test_path.is_file():
        history = pd.read_csv(path,index_col=0,parse_dates=["First Played", "Last Played"], dtype={"Total Plays": int})
        print(channel, "table loaded from", path)
        return history;
    else:
        history = pd.DataFrame(data=None, columns = ["Artist", "Title", "Album Art URL", "First Played", "Last Played", "Total Plays"], index = None)
        history.to_csv(path)
        print("Blank", channel, "table created @", path)
        return history;


def add_song(history_table,channel,url,path, prev_song):
    song = get_song(url)
    rows = len(history_table.index) 
    if song is not None:
        if song["Title"] == prev_song[channel]["Title"]:
            print("Song already logged!")
        else:    
            prev_song[channel] = song
            artist_match = history_table[history_table["Artist"] == song["Artist"]]
            title_match = artist_match[artist_match["Title"] == song["Title"]] 
            if len(title_match.index.values > 0):
                history_table.set_value(title_match.index.values,"Total Plays",history_table.loc[title_match.index.values]["Total Plays"] + 1)
                history_table.set_value(title_match.index.values,"Last Played", song["datetime"])
                print("Song Repeated!")
            else:
                new_row = {"Artist":song["Artist"], "Title":song["Title"], "Album Art URL":song["Album Art URL"], "First Played":song["datetime"], "Last Played":song["datetime"], "Total Plays":int(1)}
                history_table = history_table.append(new_row, ignore_index = True)
                history_table = history_table.sort_values("Artist", ascending=1)
                history_table.reset_index(inplace = True, drop = True)
                print("New Song Played!")
            history_table.to_csv(path)
    return history_table, prev_song

    
def main():
    history = []
    channels, urls, history_paths = set_channels()
    prev_song={}
    for channel,url,path in zip(channels,urls,history_paths):
        prev_song[channel] = {"Artist":None, "Title":None, "Album Art URL":None, "datetime":None}##TODO: Set prev_song based on most recent value in table
        history.append(open_history(channel,url, path))
    
    try:
        while True:
            for i in range(len(history)):
                print("\nChecking", channels[i], flush=True)
                history[i], prev_song = add_song(history[i],channels[i],urls[i],history_paths[i], prev_song)
                print(channels[i], "checked at", time.strftime("%H:%M:%S"), flush=True)
            time.sleep(20)
    except KeyboardInterrupt:
        print('Excecution ended by user.', flush=True)
        driver.quit()
    return;

if __name__ == "__main__":
    main()