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
    logging.basicConfig(filename=filename, level=logging.DEBUG)
    logging.info(today + " - " + msg)

def appendXMLTag(parent, name, value):
    element = etree.Element(name)
    element.text = value
    parent.append(element)


def cleanString(string):
    if isinstance(string, str):
        string = string.decode('utf-8')
    return normalize('NFKD', string).encode('ASCII', 'ignore')

def scrapeNow(date):
    url = TIPS4BETTING_TIPS_URL
    page = ''

    try:
        page = requests.get(url)
    except:
        print('Can\'t get Data. Check if site is up and working.')

    if page.status_code != 200:
        print("Can't get data from: " + date)
        return

    time.sleep(5)
    soup = BeautifulSoup(page.content, 'html.parser')

    tips_table = soup.find(attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')
    print len(rows)
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

            if(len(time_text.split(':')) < 1):
                continue

            league_text = league_tag.text
            country_text =  cleanString(country_tag.find_next('span')['title'])
            match_text = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-','_')
            under_over_tag_text = under_over_tag.text
            score_text = score_tag.text
            odds_0_text = betting_odds_0_tag.text
            odds_1_text = betting_odds_1_tag.text
            odds_2_text = betting_odds_2_tag.text
            under_over_text = under_over_tag.text
        except:
            print 'error'

        Matches = etree.Element('Matches')

        Match = etree.Element('Match')
        Matches.append(Match)
        #
        appendXMLTag(Match, 'Sport', SPORT)
        appendXMLTag(Match, 'Source', SOURCE)
        #appendXMLTag(Match, 'Date', dt)
        appendXMLTag(Match, 'Time', time_text)
        appendXMLTag(Match, 'Country', country_text)
        appendXMLTag(Match, 'League', league_text)
        #appendXMLTag(Match, 'HomeTeam', names[name].split('-')[0].strip())
        #appendXMLTag(Match, 'AwayTeam', names[name].split('-')[1].strip())
        #
        appendXMLTag(Match, 'Odds1', odds_0_text)
        appendXMLTag(Match, 'Odds2', odds_1_text)
        appendXMLTag(Match, 'Odds3', odds_2_text)
        appendXMLTag(Match, 'UnderOver', under_over_text)
        # appendXMLTag(Match, 'AverOddsX', odds[name][1])
        # appendXMLTag(Match, 'AverOdds2', odds[name][2])
        # appendXMLTag(Match, 'MatchScore', scores[name])
        filePath = ''
        try:
            filePath = DIRECTORY_FIXTURE + '/' + country_text.encode('utf-8') + '/' +  league_text + '/' + today+"/"
            try:
                os.makedirs(filePath)
            except:
                pass
                xmlFile = open(filePath + '/' + match_text + '.xml', 'wb')
                et = etree.ElementTree(Matches)
                et.write(xmlFile, pretty_print=True)
        except:
            logScrapper("Can't save file: " + filePath + '/' + match_text + '.xml' + ", please run in Administrator mode")
    # b = soup.find_all('script')
    # dates = []
    #
    # for i in b:
    #     if 'mf_usertime' in i.text and len(i.text) < 100:
    #         dates.append(i.text)
    #
    # prediction_tag = soup.find_all('td', attrs={'class': 'prob2 prediction_full'})
    # predictions = []
    #
    # if len(prediction_tag) > 2:
    #     for i in range(2, len(prediction_tag), 3):
    #         predictions.append([prediction_tag[i-2].text, prediction_tag[i-1].text, prediction_tag[i].text])
    #
    # odds_tag = soup.find_all('td', attrs={'class': 'aver_odds_full'})
    # odds = []
    #
    # if len(odds_tag) > 2:
    #     for i in range(3, len(odds_tag), 3):
    #         odds.append([odds_tag[i-2].text, odds_tag[i-1].text, odds_tag[i].text])
    #
    # scores_tag = soup.find_all('td', attrs={'align': 'center'})
    # scores = []
    #
    # for i in scores_tag:
    #     if ':' in i.text and ' ' not in i.text:
    #         scores.append(i.text)
    # score_count = len(scores)
    #
    # for i in range(0, len(odds) - score_count):
    #     scores.append('')
    #
    # flag_tag = soup.find_all('img', attrs={'class': 'flags', 'alt': ''})
    # league = []
    #
    # for flag in flag_tag:
    #     league.append(flag['title'])
    #
    # g = soup.find_all('span', attrs={'class': 'm1'})
    # names = []
    # for flag in flag_tag:
    #     names.append(flag.find_parent().text)
    #
    # for name in range(0, len(names)):
    #     dateLst = dates[name].strip()[13:23].split('/')
    #     dt = "-".join([dateLst[2], dateLst[0], dateLst[1]])
    #
    #     maxLen = 0
    #     country_name = 'Unknown'
    #
    #     for country in COUNTRIES:
    #         if league[name].lower().strip().startswith(country.lower()) and len(country) > maxLen:
    #             maxLen = len(country)
    #             country_name = country
    #
    #     for other_league in OTHER_LEAGUES:
    #         if league[name].lower().strip().startswith(other_league.lower()) and len(other_league) > maxLen:
    #             maxLen = len(other_league)
    #             country_name = other_league
    #
    #     league_name = league[name].strip()
    #
    #     print "match " + league + country_name
    #
    #     Matches = etree.Element('Matches')
    #
    #     Match = etree.Element('Match')
    #     Matches.append(Match)
    #
    #     appendXMLTag(Match, 'Sport', SPORT)
    #     appendXMLTag(Match, 'Source', SOURCE)
    #     appendXMLTag(Match, 'Date', dt)
    #     appendXMLTag(Match, 'Time', dates[name].strip()[25:30])
    #     appendXMLTag(Match, 'Country', country_name)
    #     appendXMLTag(Match, 'League', league_name)
    #     appendXMLTag(Match, 'HomeTeam', names[name].split('-')[0].strip())
    #     appendXMLTag(Match, 'AwayTeam', names[name].split('-')[1].strip())
    #
    #     appendXMLTag(Match, 'Pred1', predictions[name][0][:-1])
    #     appendXMLTag(Match, 'PredX', predictions[name][1][:-1])
    #     appendXMLTag(Match, 'Pred2', predictions[name][2][:-1])
    #     appendXMLTag(Match, 'AverOdds1', odds[name][0])
    #     appendXMLTag(Match, 'AverOddsX', odds[name][1])
    #     appendXMLTag(Match, 'AverOdds2', odds[name][2])
    #     appendXMLTag(Match, 'MatchScore', scores[name])
    #


    logScrapper('Scraped Today at: ' + date)

#-%H-%M

today = datetime.datetime.now().strftime("%d-%m-%Y")
print today
scrapeNow("14-08-2018")
#oldScrappe(today)

logScrapper("Scraping is Finished!")