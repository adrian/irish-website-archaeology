#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from collections import namedtuple
import os
import logging
import sys

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
import http.client as http_client
#http_client.HTTPConnection.debuglevel = 1

Website = namedtuple('Website', ['url', 'title', 'last_modified'])

logger = logging.getLogger('generate_report')

def generate_report(websites):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    env = Environment(loader=FileSystemLoader(cur_dir),
        extensions=['jinja2.ext.loopcontrols'])
    template = env.get_template('iol_websites.html.tmpl')
    html = template.render(websites = websites)
    return html

def get_websites(urls):
    for url in urls:
        yield website(url.rstrip())

def clean_bs_element(bs_element):
    if bs_element and bs_element.text:
        return re.sub(r'\s+', ' ', bs_element.text).strip()
    return ''

def clean_text(text):
    text = re.sub(r'<!--', '', text)
    text = re.sub(r'-->', '', text)
    text = re.sub(r'//', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\s{2,}', '', text)
    return text

def get_title(title):
    title = clean_bs_element(title)
    if title == 'Untitled':
        title = ''
    return title

def title_from_text(soup):
    for s in soup.strings:
        s = clean_text(s)
        if len(s) > 0 and s != 'Untitled':
            return s
    return None

def determine_title(soup):
    title = get_title(soup.title)
    h1 = clean_bs_element(soup.h1)
    h2 = clean_bs_element(soup.h2)
    longest_title = max([title, h1, h2], key=len)
    if longest_title == '':
        longest_title = None

    leading_text = title_from_text(soup)

    if longest_title != None and longest_title.lower() != 'index':
        title_to_return = longest_title
    elif leading_text != None and leading_text.lower() != 'index':
        title_to_return = leading_text
    else:
        title_to_return = '[missing]'

    return title_to_return

def website(url):
    logger.info("Fetching %s" % url)
    try:
        r = requests.get(url, timeout = 3)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = determine_title(soup)
            if 'last-modified' in r.headers:
                date_last_modified = r.headers['last-modified']
            else:
                date_last_modified = r.headers['date']
            return Website(url, title, date_last_modified)
        else:
            logger.error("URL %s returned status %s" % (url, r.status))
            return None
    except requests.exceptions.ConnectTimeout as e:
        logger.error("Timeout while fetching %s" % url)
        return None

def main():
    logging.basicConfig() 
    logging.getLogger().setLevel(logging.INFO)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.ERROR)
    requests_log.propagate = True

    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls_file = 'iol_urls.txt'
        with open(urls_file) as f:
            urls = f.readlines()

    websites = get_websites(urls)
    html = generate_report(websites)

    with open('website/iol_websites.html', 'w') as output_file:
        output_file.write(html)

if __name__ == '__main__':
    main()
