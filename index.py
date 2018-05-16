import requests
import os
import re
import urllib
import pyperclip
from pyquery import PyQuery as pq
from itertools import imap, ifilter
from colorama import Fore, Back, Style, init
from pynput import keyboard

# define base url for tracker
baseUrl = ''

# initialize colors
init()

# collect user input for search query
searchText = raw_input('Search for: ')
encodedSearchText = urllib.quote(searchText, safe='~()*!.\'')

# make the http request
response = requests.get(baseUrl + '/search/' + encodedSearchText)

# load the response into PyQuery
d = pq(response.text)

# find the web page table rows
rows = d('table#searchResult tr')

# it extracts the data from the web page table row
def getTorrentInfo(row):
  torrent_name = d(row).find('.detName').text()
  seeders = d(row).find('td:nth-child(3)').text()
  leechers = d(row).find('td:nth-child(4)').text()
  magnet = d(row).find('td:nth-child(2) > a:nth-child(2)').attr('href')
  uploader = d(row).find('td:nth-child(2) font a').text()
  sizeText = d(row).find('td:nth-child(2) font').text()
  # extract the torrent size from the text
  size = re.sub(r'\,\sULed.+', '', re.sub(r'.+Size\s', '', sizeText))
  return [torrent_name, seeders, leechers, uploader, size, magnet]

# collection of torrent information
mapped = imap(getTorrentInfo, rows)

# filter out the ones without text
filtered = ifilter(lambda x: x[0] != '', mapped)

# transform the iterator in a list
to_print = list(filtered)

# keep track of current arrow key selection
currentSelectionIndex = -1

def renderResults():
  index = -1
  global currentSelectionIndex
  for torrent in to_print:
    index+=1
    if currentSelectionIndex == index:
      color_suffix = Back.GREEN
    else:
      color_suffix = ''
    
    # print each line using colors
    print(
      color_suffix + torrent[0] + Style.RESET_ALL +
      ' <' + torrent[3] + '> ' +
      ' [ ' + torrent[4] + ' ] ' +
      '  |  ' + Fore.GREEN + torrent[1] + Style.RESET_ALL +
      '  |   ' + Fore.RED + torrent[2] + Style.RESET_ALL
    )

os.system('cls')
renderResults()

def on_press(key):
    global currentSelectionIndex
    global to_print
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        if key == keyboard.Key.down:
          currentSelectionIndex += 1
        if key == keyboard.Key.up:
          currentSelectionIndex -= 1
        if key == keyboard.Key.enter:
          pyperclip.copy(to_print[currentSelectionIndex][5])
          os.system('cls')
          print(to_print[currentSelectionIndex][5])
          return False
        os.system('cls')
        renderResults()
        if key == keyboard.Key.esc:
            return False

# Collect events until released
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
