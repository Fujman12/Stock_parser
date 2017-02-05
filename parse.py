import csv
import datetime
import os
import pymysql.cursors
import datetime
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from decimal import *
from time import sleep

from BeautifulSoup import BeautifulSoup

def format_values(value):
    value = value.replace(u'\xa0','')

    return Decimal(value.replace(',','.'))

print "Enter your MySql host:"
host = raw_input(">")

print "Enter your MySql server port:"
port = int(raw_input(">"))

print "Enter database name"
db = raw_input(">")

print "Enter table name"
table = raw_input(">")

print "Enter user"
user = raw_input(">")

print "Enter password"
passwd = raw_input(">")



conn = pymysql.connect(host=host , port=port, user=user, passwd=passwd, db=db)
cursor = conn.cursor()

create_sql = """CREATE TABLE IF NOT EXISTS %s (
id INT(7) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
day DATE,
isin VARCHAR(12) NOT NULL,
name VARCHAR(35) NOT NULL,
open DECIMAL(7,2),
close DECIMAL(7,2),
high DECIMAL(7,2),
low DECIMAL(7,2)
)""" % table

cursor.execute(create_sql)

print "Enter number of months:"
months = int(raw_input(">"))

now = datetime.datetime.now()
months_ago = now - datetime.timedelta(365/12 * months)
date_url = "%s_%s" % (months_ago.strftime("%d.%m.%Y"), now.strftime("%d.%m.%Y"))

driver = webdriver.Chrome("%s/chromedriver" % os.path.dirname(os.path.abspath(__file__)))

firstrow = True

with open('Sample 2.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:

        query = """INSERT INTO %s
                  (day, isin, name, open, close, high, low)
                  VALUES """ % table

        if firstrow:
            firstrow = False
            continue
        url = row[6].replace('/aktien/', '/kurse/historisch/')
        url = url.replace('-Aktie', '/STU/')
        url = url + date_url
        print "Going to %s" % url

        try:
            driver.get(url)

        except TimeoutException:
            print "TIME!"
            driver.execute_script("window.stop();")
        except WebDriverException:
            print "Wrong url for %s " % row[0]
            continue

        sleep(2)
        source = driver.page_source
        soup = BeautifulSoup(source)

        try:
            hist_div = soup.find('div', id = 'historic-price-list')
            tbody = hist_div.find('div', {'class' : 'content'} ).table.tbody
        except Exception as e:
            print e.message
            print "No info for %s on %s" % (row[0], url)
            continue

        trs = tbody.findAll('tr')
        #print trs
        firstrow = True

        for tr in trs:

            if firstrow:
                firstrow = False
                continue

            tds = tr.findAll('td')
            if (tds[0].string is not None and
                tds[1].string is not None and
                  tds[2].string is not None and
                    tds[3].string is not None and
                      tds[4].string is not None):

                      date = datetime.datetime.strptime(tds[0].string, "%d.%m.%Y").date()
                      mysql_date = date.strftime("%Y-%m-%d")

                      _open = format_values(tds[1].string)
                      _close = format_values(tds[2].string)
                      _high = format_values(tds[3].string)
                      _low = format_values(tds[4].string)
                      name = conn.escape(row[0])
                      isin = conn.escape(row[1])

                      query = query + "('%s', %s, %s, %s, %s, %s, %s)," % (mysql_date, isin, name, _open, _close, _high, _low)

                     # print mysql_date + " " + str(_open) + " " + str(_close) + " " + str(_high) + " " + str(_low)


        query = query[:-1]
        #print query
        cursor.execute(query)
        conn.commit()
        print row[0] + " information succesfully added to %s" % table

driver.close()
