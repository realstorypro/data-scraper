import time
from selenium import webdriver

##
## try:
##     driver.find_element_by_class_name('logo')
##     print('protection bypassed')
## except:
##     print('scraper protection engaged')

# setting up a headless browser
DRIVER_PATH = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


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
            print('protection bypassed')
            bot_protection = False
        except:
            print('scraper protection engaged')
            time.sleep(60)


def scrape_data(company_name):
    name = format_name(company_name)
    print_green(f'Checking {company_name} alias {name}')

    load_page(f'/organization/{name}')

    # load the page in "soup" variable
    #soup = get_page(f'/organization/{name}')
    ##if not soup:
    ##    print_green(
    ##        f'{company_name}, alias {name} gave an error while loading')
    ##    with open('../data/error.csv', 'a') as file:
    ##        file.write('\n' + company_name)
    ##    return



# Going through the csv of company names
with open('../data/list_of_company_names_raw.csv', 'r') as fp:
    line = fp.readline()

    while line:
        companies.append(line.replace('\n', ''))

        line = fp.readline()

companies = list(dict.fromkeys(companies))

for company in companies:
    scrape_data(company)
