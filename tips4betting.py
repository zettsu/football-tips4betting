import os, sys

from parameters import *

import traceback
import datetime
import logging
from unicodedata import normalize

from lxml import etree
from bs4 import BeautifulSoup
import requests

def log_scrapper(msg):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = "./logs/parser_log_"+today+".log"
    logging.basicConfig(filename=filename, level=logging.INFO)
    now = datetime.datetime.now().strftime("%Y_%m_%d %H:%M")
    logging.info(now + " - " + msg)

def append_xml_tag(parent, name, value):
    element = etree.Element(name)
    element.text = value
    parent.append(element)


def clean_string(string):
    if isinstance(string, str):
        string = string.decode('utf-8')
    return normalize('NFKD', string).encode('ASCII', 'ignore')


def save(file_path, match_text, xml_el):
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        xml_file = open(file_path + '/' + match_text + '.xml', 'wb')
        et = etree.ElementTree(xml_el)
        et.write(xml_file, pretty_print=True)
        xml_file.close()
    except Exception as e:
        log_scrapper(traceback.format_exc())

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


def scrape_stats_match(url):
    url = url
    total_goals = ''
    try:
        soup = get_page(url)
        tips_table = soup.find(attrs={'class': 'tableMid'})
        total_goals = tips_table.find_all('tr')[3].find_all('td')[2].text
    except Exception as e:
        log_scrapper(traceback.format_exc())
        log_scrapper('Error scrapping goals for match'+url)

    return total_goals


def scrape_today(url):
    today       = datetime.datetime.now().strftime("%Y-%m-%d")
    directory   = DIRECTORY_FIXTURE

    log_scrapper('INIT TASK TODAY url=' + url)
    soup = get_page(url)

    tips_table = soup.find('table', attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')

    del rows[0]

    log_scrapper('Matches founded : ' + str(len(rows)))

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
            chances_win_0_tag   = betting_odds_2_tag.find_next('td')
            chances_win_1_tag = chances_win_0_tag.find_next('td')
            chances_win_2_tag = chances_win_1_tag.find_next('td')
            under_over_tag      = chances_win_2_tag.find_next('td')

            country_text    = clean_string(country_tag.find_next('span')['title'])
            time_text       = time_tag.text.replace(' ', '')

            league_text = league_tag.text
            match_text  = match_tag.find_next('a')['href'].rpartition('/')[2].replace('.html','').replace('-',' ')
            teams_text  = match_text.split(" vs ")

            if "-:-" in score_tag.text :
                score_text = score_tag.text
            else:
                score_text = score_tag.text.replace(' ', '').replace('-',':')

            odds_0_text         = betting_odds_0_tag.text
            odds_1_text         = betting_odds_1_tag.text
            odds_2_text         = betting_odds_2_tag.text

            chances_win_0 = chances_win_0_tag.text
            chances_win_1 = chances_win_1_tag.text
            chances_win_2 = chances_win_2_tag.text
            under_over_text     = under_over_tag.text
            goals = '-:-'
            if match_tag.find_next('a')['href'] != None:
                goals = scrape_stats_match(match_tag.find_next('a')['href'])

        except Exception as e:
            log_scrapper(traceback.format_exc())

        if ":" not in time_text:
            log_scrapper('skipping match ' + match_text + ' of day ' + today)
            continue

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
        append_xml_tag(match, 'MatchScore', score_text)
        append_xml_tag(match, 'Averodds1', odds_0_text)
        append_xml_tag(match, 'Averodds2', odds_1_text)
        append_xml_tag(match, 'Averodds3', odds_2_text)
        append_xml_tag(match, 'Pred1', chances_win_0)
        append_xml_tag(match, 'PredX', chances_win_1)
        append_xml_tag(match, 'Pred2', chances_win_2)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'Predtotalpoints', goals)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + today

        try:
            save(file_path, match_text, matches)
        except Exception as e:
            log_scrapper(traceback.format_exc())
            log_scrapper("Can't save file: " + file_path + '/' + match_text + '.xml' + ", please run in Administrator mode")

        log_scrapper('INIT TASK TODAY FINISHED.')

def scrape_tomorrow():
    today       = datetime.datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

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

            if (len(time_tag.text.lstrip().lstrip().split(':')) < 2):
                log_scrapper('skipping match '+ match_text + ' of day '+ tomorrow)
                continue

            league_tag = time_tag.find_next('td')
            match_tag = league_tag.find_next('td')
            score_tag = match_tag.find_next('td')
            betting_odds_0_tag = score_tag.find_next('td')
            betting_odds_1_tag = betting_odds_0_tag.find_next('td')
            betting_odds_2_tag = betting_odds_1_tag.find_next('td')
            chances_win_0_tag = betting_odds_2_tag.find_next('td')
            chances_win_1_tag = chances_win_0_tag.find_next('td')
            chances_win_2_tag = chances_win_1_tag.find_next('td')
            under_over_tag = chances_win_2_tag.find_next('td')

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

        except Exception as e:
            log_scrapper(traceback.format_exc())

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
        except Exception as e:
            log_scrapper(traceback.format_exc())
            log_scrapper("Can't save file: " + file_path + '/' + match_text + '.xml' + ", please run in Administrator mode")

        log_scrapper('INIT TASK TOMORROW FINISHED.')

def scrape_yesterday():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    url = TIPS4BETTING_TIPS_URL_YESTERDAY
    directory = DIRECTORY_RESULTS

    log_scrapper('INIT TASK YESTERDAY url=' + url)

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
            log_scrapper(traceback.format_exc())

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
            log_scrapper(traceback.format_exc())

        log_scrapper('INIT TASK YESTERDAY FINISHED.')

def scrape_results(day):
    day = day.strftime("%Y-%m-%d")
    url = TIPS4BETTING_ARCHIVE_URL + day + '.html'
    directory = DIRECTORY_RESULTS

    print('INIT TASK RESULTS day=('+day+') url=' + url)

    soup = get_page(url)

    tips_table = soup.find(attrs={'id': 'tips'})
    rows = tips_table.find_all('tr')

    del rows[0]
    for row in rows:
        try:
            country_tag = row.find_next('td')
            league_tag = country_tag.find_next('td')
            match_tag = league_tag.find_next('td')
            score_tag = match_tag.find_next('td')
            betting_odds_0_tag = score_tag.find_next('td')
            betting_odds_1_tag = betting_odds_0_tag.find_next('td')
            betting_odds_2_tag = betting_odds_1_tag.find_next('td')
            chances_to_win_0_tag = betting_odds_2_tag.find_next('td')
            chances_to_win_1_tag = chances_to_win_0_tag.find_next('td')
            chances_to_win_2_tag = chances_to_win_1_tag.find_next('td')
            bet_tip_tag = chances_to_win_2_tag.find_next('td')
            under_over_tag = bet_tip_tag.find_next('td')

            if under_over_tag.find_next('td').find_next('a')['href'] is None:
                goals = ''
            else:
                goals = scrape_stats_match(under_over_tag.find_next('td').find_next('a')['href'])

            country_text = clean_string(country_tag.find_next('span')['title'])

            odds_0_text = betting_odds_0_tag.find_next('a').text
            odds_1_text = betting_odds_1_tag.find_next('a').text
            odds_2_text = betting_odds_2_tag.find_next('a').text

            chances_to_win_0_text = chances_to_win_0_tag.text
            chances_to_win_1_text = chances_to_win_1_tag.text
            chances_to_win_2_text = chances_to_win_2_tag.text

            under_over_text = under_over_tag.text
            league_text = league_tag.text
            score_text = score_tag.text

            match_slug = match_tag.text.split('<span>')[0]

            match_text = match_slug.split(' vs ')
        except Exception as e:
            log_scrapper(traceback.format_exc())

        matches = etree.Element('Matches')
        match = etree.Element('Match')

        append_xml_tag(match, 'Sport', SPORT)
        append_xml_tag(match, 'Source', SOURCE)
        append_xml_tag(match, 'Date', day)
        append_xml_tag(match, 'Country', country_text)
        append_xml_tag(match, 'League', league_text)
        append_xml_tag(match, 'HomeTeam', match_text[0])
        append_xml_tag(match, 'AwayTeam', match_text[1])
        append_xml_tag(match, 'MatchScore', score_text)
        append_xml_tag(match, 'Averodds1', odds_0_text)
        append_xml_tag(match, 'Averodds2', odds_1_text)
        append_xml_tag(match, 'Averodds3', odds_2_text)
        append_xml_tag(match, 'Pred1', chances_to_win_0_text)
        append_xml_tag(match, 'PredX', chances_to_win_1_text)
        append_xml_tag(match, 'Pred2', chances_to_win_2_text)
        append_xml_tag(match, 'UnderOver', under_over_text)
        append_xml_tag(match, 'Predtotalpoints', goals)

        matches.append(match)
        file_path = directory + '/' + country_text.encode('utf-8') + '/' + league_text + '/' + day

        try:
            save(file_path, match_text, matches)
        except Exception as e:
            log_scrapper(traceback.format_exc())

        log_scrapper('INIT TASK RESULTS FINISHED.')

def find_countries():
    soup = get_page(BASE_URL)

    container_selector  = soup.find(attrs={'id': 'avtips'}).find_all('a', attrs={'class','cselector'})
    links = []
    for link in container_selector:
        links.append(BASE_URL + link['href'])

    links.pop()
    return links


while True:
    print '1. Scrap today games'
    print '2. Scrap tomorrow games'
    print '3. Scrap yesterday games'
    print '4. Scrap custom date from/to'
    option = raw_input('choice: ')

    if option == '0':
        break
    else:
        if option == '1' :
            links = find_countries()
            for link in links:
                scrape_today(link)
        elif option == '2' :
            scrape_tomorrow()
        elif option == '3' :
            scrape_yesterday()
        elif option == '4' :
            print 'Insert date from/to'
            date_from = raw_input('input from(YYYY-MM-DD): ')
            print 'Insert date from/to'
            date_to = raw_input('input to(YYYY-MM-DD): ')
            today = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            last_day = datetime.datetime.strptime(date_to, '%Y-%m-%d')

            delta = last_day - today
            for i in range(0, delta.days):
                day = today + datetime.timedelta(days=i)
                scrape_results(day)

log_scrapper("Scraping is Finished!")