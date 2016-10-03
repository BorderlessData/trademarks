# trademarks

Scraper for tech company trademarks filed in foreign nations

## Setup

```
mkvirtualenv trademarks
pip install -r requirements.txt
```

## Running

```
rm foreign.csv && scrapy crawl foreign -o foreign.csv
```
