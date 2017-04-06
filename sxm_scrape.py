from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

#Initialize web scraping
driver = webdriver.PhantomJS('./phantomjs-2.1.1-windows/bin/phantomjs.exe')


def get_html (url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup;


def extract_song (soup): #Get current song title, artist, and albumart from siriusxm website
    song = {}
    song["title"] = soup.find_all(class_="onair-pdt-song")[0].contents[0]
    song["artist"] = soup.find_all(class_="onair-pdt-artist")[0].contents[0]
    for pic in soup.findAll('img'):
        if pic.parent.get('id') == 'onair-pdt':
            song["albumart"] = pic.get('src')
    return song["title"], song["artist"], song["albumart"]

    
def main():
    bpm_history = pd.DataFrame(columns=["Title", "Artist", "Album Art URL"])
    url = 'http://www.siriusxm.com/bpm'
    bpm_soup = get_html(url)
    a,b,c = extract_song(bpm_soup)
    bpm_history = bpm_history.append({"Title": a, "Artist": b, "Album Art URL": c}, ignore_index = True)
    print(bpm_history)
    bpm_history.to_csv(r'c:\users\mringqui\desktop\bpm_history.csv')
    return;

main()