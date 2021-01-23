import time
from random import randrange
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import requests

##
## try:
##     driver.find_element_by_class_name('logo')
##     print('protection bypassed')
## except:
##     print('scraper protection engaged')

# setting up a headless browser
DRIVER_PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

# notifications
webhook_url = 'https://hooks.slack.com/services/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'

# initial variables
BASE_URL = 'https://www.crunchbase.com'
companies = []
pages = []


# utility class for pretty printing
def print_green(s):
    print(f'\033[92m{s}\033[0m')


# turns name into the url
def format_name(name):
    return name.lower().replace('\n', '').strip().replace('.', '-').replace(' ', '-').replace(':', '-')


# the method to load the page
def load_page(route):
    url = f'{BASE_URL}{route}'
    print('loading', url)

    # load the url
    driver.get(url)

    # we may be dealing with bot protection
    bot_protection = True
    while bot_protection == True:
        try:
            driver.find_element_by_class_name('logo')
            bot_protection = False
        except NoSuchElementException:
            print('scraper protection engaged')
            requests.post(
                webhook_url, data=json.dumps({'text': "The scraping protection activated. Please do a manual bypass."}),
                headers={'Content-Type': 'application/json'}
            )

            time.sleep(60)
            driver.get(url)


def scrape_data(company_name):
    name = format_name(company_name)
    print_green(f'Checking {company_name} alias {name}')

    load_page(f'/organization/{name}')

    # lets wait before we scrape to see if this fixes stale element errors
    time.sleep(4)

    try:
        profile_name = driver.find_element_by_css_selector('.profile-name')
    except NoSuchElementException:
        print_green('the profile is invalid')
        with open('../data/invalid.csv', 'a') as file:
            file.write('\n' + company_name)
        return

    # lets get the url first
    try:
        company_url = driver.find_element_by_xpath('//profile-section[1]//link-formatter/a').text
    except NoSuchElementException:
        company_url = ''

    # location second (sometimes its unavailable)
    try:
        company_location = driver.find_element_by_xpath(
            '/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/ng-component/entity-v2/page-layout/div/div/div/page-centered-layout[2]/div/row-card/div/div[1]/profile-section/section-card/mat-card/div[2]/div/fields-card/ul/li[1]/label-with-icon/span/field-formatter/identifier-multi-formatter/span').text
    except NoSuchElementException:
        company_location = ''

    print('located in:', company_location, 'with a url:', company_url)

    # now lets find people
    load_page(f'/organization/{name}/people')

    # lets wait before we scrape to see if this fixes stale element errors
    time.sleep(4)
    try:
        names = driver.find_elements_by_xpath('//section-card[1]//identifier-image/following-sibling::div/a')
        titles = driver.find_elements_by_xpath(
            '//section-card[1]//identifier-image/following-sibling::div/field-formatter[1]/span')
    except NoSuchElementException:
        print_green('no people found')
        return

    try:
        for i in range(len(names)):
            print(f'found {names[i].text}, {titles[i].text}')

            with open('../data/found.csv', 'a') as file:
                file.write(
                    f'\n"{company_name}","{company_location}","{company_url}","{names[i].text}","{titles[i].text}"')
    except AttributeError:
        print('could not extract names and titles')

    # load the page in "soup" variable
    # soup = get_page(f'/organization/{name}')
    ##if not soup:
    ##    print_green(
    ##        f'{company_name}, alias {name} gave an error while loading')
    ##    with open('../data/error.csv', 'a') as file:
    ##        file.write('\n' + company_name)
    ##    return


# Send a Slack Message
requests.post(
    webhook_url, data=json.dumps({'text': "The scrape job has begun."}),
    headers={'Content-Type': 'application/json'}
)

# Going through the csv of company names
with open('../data/list_of_company_names_raw.csv', 'r') as fp:
    line = fp.readline()

    while line:
        companies.append(line.replace('\n', ''))

        line = fp.readline()

companies = list(dict.fromkeys(companies))

for company in companies:
    scrape_data(company)
    time.sleep(randrange(10, 30))

# Send a Slack Message
requests.post(
    webhook_url, data=json.dumps({'text': "The scrape job has finished."}),
    headers={'Content-Type': 'application/json'}
)

driver.quit()
