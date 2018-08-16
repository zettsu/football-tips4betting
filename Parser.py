from parameters import *

import datetime
import logging
import re

from unicodedata import normalize

import requests
from lxml import etree
from bs4 import BeautifulSoup

pattern = re.compile(r'\s+')


def log_scrapper(msg):
    today = datetime.datetime.now().strftime("%d_%m_%Y")
    filename = "parser_log_"+today+".log"
    logging.basicConfig(filename=filename, level=logging.INFO)
    now = datetime.datetime.now().strftime("%d_%m_%Y %H:%M")
    logging.info(now + " - " + msg)


def append_xml_tag(parent, name, value):
    element = etree.Element(name)
    element.text = value
    parent.append(element)


def clean_string(string):
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

def get_page(url):
    page = None
    try:
        page = requests.get(url)
    except:
        log_scrapper('Can\'t get Data. Check if site is up and working.')

    if page.status_code != 200:
        log_scrapper("Can't get data from site")
        return

    return BeautifulSoup(page.content, 'html.parser')

def scrape_today():
    today       = datetime.datetime.now().strftime("%d-%m-%Y")
    url         = TIPS4BETTING_TIPS_URL
    directory   = DIRECTORY_FIXTURE

    log_scrapper('INIT TASK TODAY url=' + url)

    soup = get_page(url)

    tips_table = soup.find(attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')

    del rows[0]
    for row in rows:

        try:
            country_tag     = row.find_next('td')
            time_tag        = country_tag.find_next('td')
            league_tag      = time_tag.find_next('td')
            match_tag       = league_tag.find_next('td')
            score_tag       = match_tag.find_next('td')
            betting_odds_0_tag  = score_tag.find_next('td')
            betting_odds_1_tag  = betting_odds_0_tag.find_next('td')
            betting_odds_2_tag  = betting_odds_1_tag.find_next('td')
            under_over_tag      = betting_odds_2_tag.find_next('td')

            country_text    = clean_string(country_tag.find_next('span')['title'])
            time_text       = time_tag.text

            league_text = league_tag.text
            match_text  = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-',' ')
            teams_text  = match_text.split(" vs ")

            score_text          = score_tag.text
            odds_0_text         = betting_odds_0_tag.text
            odds_1_text         = betting_odds_1_tag.text
            odds_2_text         = betting_odds_2_tag.text
            under_over_text     = under_over_tag.text

            result = time_text.lstrip().lstrip().split(':')

            if (len(result) < 2):
                log_scrapper('skipping match '+ match_text + ' of day '+ today)
                continue
        except Exception as e:
            log_scrapper(e)

        matches = etree.Element('Matches')
        match = etree.Element('Match')

        append_xml_tag(match, 'Sport', SPORT)
        append_xml_tag(match, 'Source', SOURCE)
        append_xml_tag(match, 'Date', today)
        append_xml_tag(match, 'Time', time_text)
        append_xml_tag(match, 'Country', country_text)
        append_xml_tag(match, 'League', league_text)
        append_xml_tag(match, 'HomeTeam', teams_text[0])
        append_xml_tag(match, 'AwayTeam', teams_text[1])
        append_xml_tag(match, 'Odds1', odds_0_text)
        append_xml_tag(match, 'Odds2', odds_1_text)
        append_xml_tag(match, 'Odds3', odds_2_text)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'MatchScore', score_text)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + today

        try:
            save(file_path, match_text, matches)
        except Exception as e:
            #log_scrapper(e)
            log_scrapper("Can't save file: " + file_path + '/' + match_text + '.xml' + ", please run in Administrator mode")


def scrape_tomorrow():
    today       = datetime.datetime.now().strftime("%d-%m-%Y")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")

    url         = TIPS4BETTING_TIPS_URL_TOMORROW
    directory   = DIRECTORY_FIXTURE

    log_scrapper('INIT TASK TOMORROW url=' + url)

    soup = get_page(url)

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

            country_text = clean_string(country_tag.find_next('span')['title'])
            time_text = time_tag.text

            league_text = league_tag.text
            match_text = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-',' ')
            teams_text = match_text.split(" vs ")

            score_text = score_tag.text
            odds_0_text = betting_odds_0_tag.text
            odds_1_text = betting_odds_1_tag.text
            odds_2_text = betting_odds_2_tag.text
            under_over_text = under_over_tag.text

            result = time_text.lstrip().lstrip().split(':')
            if (len(result) < 2):
                log_scrapper('skipping match '+ match_text + ' of day '+ tomorrow)
                continue
        except Exception as e:
            log_scrapper(e)

        matches = etree.Element('Matches')
        match = etree.Element('Match')

        append_xml_tag(match, 'Sport', SPORT)
        append_xml_tag(match, 'Source', SOURCE)
        append_xml_tag(match, 'Date', tomorrow)
        append_xml_tag(match, 'Time', time_text)
        append_xml_tag(match, 'Country', country_text)
        append_xml_tag(match, 'League', league_text)
        append_xml_tag(match, 'HomeTeam', teams_text[0])
        append_xml_tag(match, 'AwayTeam', teams_text[1])
        append_xml_tag(match, 'Odds1', odds_0_text)
        append_xml_tag(match, 'Odds2', odds_1_text)
        append_xml_tag(match, 'Odds3', odds_2_text)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'MatchScore', score_text)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + today

        try:
            save(file_path, match_text, matches)
        except:
            log_scrapper("Can't save file: " + file_path + '/' + match_text + '.xml' + ", please run in Administrator mode")


def scrape_yesterday():

    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")

    url = TIPS4BETTING_TIPS_URL_YESTERDAY
    directory = DIRECTORY_RESULTS

    log_scrapper('INIT TASK TOMORROW url=' + url)

    soup = get_page(url)

    tips_table = soup.find(attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')

    # first row are for table headers
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

            country_text = clean_string(country_tag.find_next('span')['title'])
            time_text = time_tag.text
            match_slug = match_tag.text.split('<span>')[0]
            match_teams = match_slug.split(' vs ')
            league_text = league_tag.text
            score_text = score_tag.text
            odds_0_text = betting_odds_0_tag.text
            odds_1_text = betting_odds_1_tag.text
            odds_2_text = betting_odds_2_tag.text
            under_over_text = under_over_tag.text
        except Exception as e:
            log_scrapper(e)

        matches = etree.Element('Matches')
        match = etree.Element('Match')

        append_xml_tag(match, 'Sport', SPORT)
        append_xml_tag(match, 'Source', SOURCE)
        append_xml_tag(match, 'Date', yesterday)
        append_xml_tag(match, 'Time', time_text)
        append_xml_tag(match, 'Country', country_text)
        append_xml_tag(match, 'League', league_text)
        append_xml_tag(match, 'HomeTeam', match_teams[0])
        append_xml_tag(match, 'AwayTeam', match_teams[1])
        append_xml_tag(match, 'Odds1', odds_0_text)
        append_xml_tag(match, 'Odds2', odds_1_text)
        append_xml_tag(match, 'Odds3', odds_2_text)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'MatchScore', score_text)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + yesterday

        try:
            save(file_path, match_slug, matches)
        except Exception as e:
            log_scrapper(e)


def scrape_results(day):
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    url = TIPS4BETTING_TIPS_URL
    directory = DIRECTORY_RESULTS

    log_scrapper('INIT TASK RESULTS day=('+day+') url=' + url)

    soup = get_page(url)

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

            country_text = clean_string(country_tag.find_next('span')['title'])
            time_text = time_tag.text

            league_text = league_tag.text
            match_text = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-',' ')
            teams_text = match_text.split(" vs ")

            score_text = score_tag.text
            odds_0_text = betting_odds_0_tag.text
            odds_1_text = betting_odds_1_tag.text
            odds_2_text = betting_odds_2_tag.text
            under_over_text = under_over_tag.text

            result = time_text.lstrip().lstrip().split(':')
            if len(result) < 2:
                log_scrapper('skipping match '+ match_text + ' of day '+ today)
                continue
        except Exception as e:
            log_scrapper(e)

        matches = etree.Element('Matches')
        match = etree.Element('Match')

        append_xml_tag(match, 'Sport', SPORT)
        append_xml_tag(match, 'Source', SOURCE)
        append_xml_tag(match, 'Date', today)
        append_xml_tag(match, 'Time', time_text)
        append_xml_tag(match, 'Country', country_text)
        append_xml_tag(match, 'League', league_text)
        append_xml_tag(match, 'HomeTeam', teams_text[0])
        append_xml_tag(match, 'AwayTeam', teams_text[1])
        append_xml_tag(match, 'Odds1', odds_0_text)
        append_xml_tag(match, 'Odds2', odds_1_text)
        append_xml_tag(match, 'Odds3', odds_2_text)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'MatchScore', score_text)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + today

        try:
            save(file_path, match_text, matches)
        except Exception as e:
            log_scrapper(e)


scrape_today()

#scrape_tomorrow()

#scrape_yesterday()

#html_url = TIPS4BETTING_ARCHIVE_URL + date_target + ".html"
#scrape_results()

log_scrapper("Scraping is Finished!")
