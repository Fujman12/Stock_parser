import csv
import datetime
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from BeautifulSoup import BeautifulSoup

print "Enter number of month:"
months = int(raw_input(">"))

now = datetime.datetime.now()
months_ago = now - datetime.timedelta(365/12 * months)
date_url = "%s_%s" % (months_ago.strftime("%d.%m.%Y"), now.strftime("%d.%m.%Y"))

driver = webdriver.Chrome("%s/chromedriver.exe" % os.path.dirname(os.path.abspath(__file__)))

firstrow = True

with open('Sample 2.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        if firstrow:
            firstrow = False
            continue
        url = row[6].replace('/aktien/', '/kurse/historisch/')
        url = url.replace('-Aktie', '/STU/')
        url = url + date_url
        print "Going to %s" % url
        driver.get(url)

        source = driver.page_source
        soup = BeautifulSoup(source)


        hist_div = soup.find('div', id = 'historic-price-list')
        tbody = hist_div.find('div', {'class' : 'content'} ).table.tbody

        trs = tbody.findAll('tr')
        #print trs
        firstrow = True

        for tr in trs:

            if firstrow:
                firstrow = False
                continue

            tds = tr.findAll('td')

            print tds[0].string + " " + tds[1].string + " " +tds[2].string + " " + tds[3].string + " " + tds[4].string
