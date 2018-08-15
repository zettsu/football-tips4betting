import datetime
import logging
import re
import time

from unicodedata import normalize

import requests
from lxml import etree
from bs4 import BeautifulSoup

from datetime import date, timedelta
import os

from parameters import *

pattern = re.compile(r'\s+')

def logScrapper(msg):
    today = datetime.datetime.now().strftime("%d_%m_%Y")
    filename = "parser_log_"+today+".log"
    logging.basicConfig(filename=filename, level=logging.INFO)
    logging.info(datetime.datetime.now().strftime("%d_%m_%Y %H:%M") + " - " + msg)

def appendXMLTag(parent, name, value):
    element = etree.Element(name)
    element.text = value
    parent.append(element)


def cleanString(string):
    if isinstance(string, str):
        string = string.decode('utf-8')
    return normalize('NFKD', string).encode('ASCII', 'ignore')

def save(file_path, match_text, Xml_el):
    try:
        os.makedirs(file_path)
    except:
        pass
        xmlFile = open(file_path + '/' + match_text + '.xml', 'wb')
        et = etree.ElementTree(Xml_el)
        et.write(xmlFile, pretty_print=True)
def scrapeNow(date, url):
    url = url
    page = ''
    logScrapper('init scrapping target '+url)
    try:
        page = requests.get(url)
    except:
        logScrapper('Can\'t get Data. Check if site is up and working.')

    if page.status_code != 200:
        logScrapper("Can't get data from: " + date)
        return

    soup = BeautifulSoup(page.content, 'html.parser')

    tips_table = soup.find(attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')

    del rows[0]
    for row in rows:
        try:
            country_tag = row.find_next('td')
            time_tag = country_tag.find_next('td')
            league_tag = time_tag.find_next('td')
            match_tag = league_tag.find_next('td')
            score_tag = match_tag.find_next('td')
            betting_odds_0_tag = score_tag.find_next('td')
            betting_odds_1_tag = betting_odds_0_tag.find_next('td')
            betting_odds_2_tag = betting_odds_1_tag.find_next('td')
            under_over_tag = betting_odds_2_tag.find_next('td')

            country_text = cleanString(country_tag.find_next('span')['title'])
            time_text = time_tag.text

            league_text = league_tag.text
            match_text = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-',' ')
            teams_text = match_text.split(" vs ")
            under_over_tag_text = under_over_tag.text
            score_text = score_tag.text
            odds_0_text = betting_odds_0_tag.text
            odds_1_text = betting_odds_1_tag.text
            odds_2_text = betting_odds_2_tag.text
            under_over_text = under_over_tag.text

            result = time_text.lstrip().lstrip().split(':')
            if (len(result) < 2):
                print 'skipping match '+ match_text + ' of day '+ today
                continue
        except Exception as e:
            print e
            print 'error'

        Matches = etree.Element('Matches')

        Match = etree.Element('Match')

        #
        appendXMLTag(Match, 'Sport', SPORT)
        appendXMLTag(Match, 'Source', SOURCE)
        appendXMLTag(Match, 'Date', today)
        appendXMLTag(Match, 'Time', time_text)
        appendXMLTag(Match, 'Country', country_text)
        appendXMLTag(Match, 'League', league_text)
        appendXMLTag(Match, 'HomeTeam', teams_text[0])
        appendXMLTag(Match, 'AwayTeam', teams_text[1])
        appendXMLTag(Match, 'Odds1', odds_0_text)
        appendXMLTag(Match, 'Odds2', odds_1_text)
        appendXMLTag(Match, 'Odds3', odds_2_text)
        appendXMLTag(Match, 'UnderOver', under_over_text)
        appendXMLTag(Match, 'MatchScore', score_text)

        Matches.append(Match)

        filePath = DIRECTORY_FIXTURE + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + today

        try:
            save(filePath, match_text, Matches)
        except:
            logScrapper("Can't save file: " + filePath + '/' + match_text + '.xml' + ", please run in Administrator mode")

today = datetime.datetime.now().strftime("%d-%m-%Y")
print today
tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")
print tomorrow
scrapeNow(today, TIPS4BETTING_TIPS_URL)

scrapeNow(tomorrow, TIPS4BETTING_TIPS_URL_TOMORROW)
#oldScrappe(today)

logScrapper("Scraping is Finished!")
