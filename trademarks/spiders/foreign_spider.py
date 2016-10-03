#!/usr/bin/env python

import scrapy
from selenium import webdriver


class ForeignSpider(scrapy.Spider):
    name = "foreign"

    companies = [
        'amazon',
        'apple'
    ]

    start_urls = ['http://tess2.uspto.gov/']

    def __init__(self):
        self.driver = webdriver.Firefox()

    def parse(self, response):
        for company in self.companies:
            self.driver.get(response.url)

            search_link = self.driver.find_element_by_link_text('Word and/or Design Mark Search (Free Form)')

            search_link.click()

            search_input = self.driver.find_element_by_name('p_s_ALL')
            submit_button = self.driver.find_element_by_name('a_search')

            search_input.send_keys('44d[ob] and %s[on]' % company)
            submit_button.click()

            links = self.driver.find_elements_by_link_text('TSDR')

            for link in links:
                href = link.get_attribute('href')
                serial = href.split('caseNumber=')[1].split('&')[0]
                url = 'http://tsdr.uspto.gov/statusview/sn%s' % serial

                callback = scrapy.Request(url, callback=self.parse_tsdr)
                callback.meta['serial'] = serial

                yield callback

    def parse_tsdr(self, response):
        data = {
            'serial': response.meta['serial']
        }

        self.log(response.url)

        data['mark'] = response.xpath('//*[@id="summary"]/div[2]/div/div[2]/text()').extract_first().strip()
        data['owner_name'] = response.xpath('//*[@id="relatedProp-section"]/div[1]/div/div[2]/text()').extract_first().strip()

        foreign_fields = len(response.xpath('//*[@id="markInfo-section"]/div[2]/div'))

        if foreign_fields == 3:
            data['foreign_country'] = response.xpath('//*[@id="markInfo-section"]/div[2]/div[3]/div[2]/text()').extract_first().strip()
        else:
            data['foreign_country'] = response.xpath('//*[@id="markInfo-section"]/div[2]/div[2]/div[2]/text()').extract_first().strip()

        yield data
