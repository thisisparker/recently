# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "bs4",
#     "feedparser",
#     "gspread",
# ]
# ///

import json
import os
import re

from datetime import datetime
from zoneinfo import ZoneInfo

import feedparser
import gspread

from bs4 import BeautifulSoup

def get_recent_concerts():
    credentials = os.getenv('GDOC_CREDENTIALS')
    if not credentials:
        raise ValueError('Google Doc credentials not set')
    
    service_acct = json.loads(credentials)

    gc = gspread.service_account_from_dict(service_acct)

    gdoc_key = os.getenv('GDOC_KEY')
    if not gdoc_key:
        raise ValueError('Google Sheets key not set')
    sh = gc.open_by_key(gdoc_key)
    records = sh.sheet1.get_all_records()

    today = datetime.now(ZoneInfo("America/New_York")).date().isoformat()

    records.sort(key=lambda x: x['date'], reverse=True)

    records = [r for r in records if r['date'] <= today]

    shows = []
    for r in records:
        artist_list = [a.strip() for a in r['artists'].split(',')]
        if len(artist_list) < 3:
            artists = ' and '.join(artist_list)
        else:
            artists = ', '.join(artist_list[:len(artist_list)-1]) + ', and ' + artist_list[-1]
        shows.append({'artists': artists, 'venue':r['venue']})

    return shows

def get_recent_books():
    feed = feedparser.parse('https://www.goodreads.com/user/updates_rss/3672995')

    books = []
    for b in feed['entries']:
        if not b.id.startswith('Review'):
            continue
        soup = BeautifulSoup(b.summary_detail['value'], features="html.parser")
        title_and_author = soup.find('img')['alt']
        title, author = title_and_author.rsplit(' by ')
        books.append({'title':title, 'author':author})

    return books

def get_recent_movies():
    feed = feedparser.parse('https://letterboxd.com/xorxor/rss/')

    movies = []
    for m in feed['entries']:
        title, year = re.match(r'(.*), (\d{4})', m['title']).groups()
        movies.append({'title': title, 'year':year})

    return movies


def main():
    movies = get_recent_movies()
    books  = get_recent_books()
    concerts = get_recent_concerts()

    recently = {'movies': movies[:3], 'books': books[:3], 'concerts': concerts[:3]}

    print(json.dumps(recently, indent=4))

if __name__ == '__main__':
    main()
