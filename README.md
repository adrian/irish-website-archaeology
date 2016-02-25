# Irish Website Archaeology
This repository records the URLs of [Ireland On-line](https://en.wikipedia.org/wiki/Ireland_On-Line) subscriber websites. Many of these sites haven't been updated since the late 90s or early 00s.

The URLs are listed in **iol_urls.txt**. To add a URL submit a pull request or send me the link directly, adrian@17od.com.

The script **generate\_website.py** generates a HTML page with a link to the site and the page's last update date. The page is hosted at http://www.17od.com/irish-website-archaeology/iol_websites.html.

## Development Environment Setup
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
