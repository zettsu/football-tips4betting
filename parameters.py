import os

BASE_URL = 'http://tips4betting.com/'
TIPS4BETTING_TIPS_URL = BASE_URL
TIPS4BETTING_TIPS_URL_TOMORROW = BASE_URL + "tomorrow.php"
TIPS4BETTING_TIPS_URL_YESTERDAY = BASE_URL + "yesterday.php"
TIPS4BETTING_ARCHIVE_URL = BASE_URL + 'arhive/betting-tips-arhive-on-'
TIPS4BETTING_HISTORY_URL = BASE_URL + 'history.html'

SOURCE = 'TIPS4BETTING'
SPORT = 'Soccer'

BASE_DIRECTORY = os.getcwd() + '/TIPS4BETTING'
DIRECTORY_RESULTS = BASE_DIRECTORY + '/Results'
DIRECTORY_FIXTURE = BASE_DIRECTORY + '/Fixture'