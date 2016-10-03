#!/usr/bin/env python

import scrapy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

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

            search_input.clear()
            search_input.send_keys('44d[ob] and %s[on]' % company)
            submit_button.click()

            more = True

            while more:
                links = self.driver.find_elements_by_link_text('TSDR')

                for link in links:
                    href = link.get_attribute('href')
                    serial = href.split('caseNumber=')[1].split('&')[0]
                    url = 'http://tsdr.uspto.gov/statusview/sn%s' % serial

                    callback = scrapy.Request(url, callback=self.parse_tsdr)
                    callback.meta['serial'] = serial

                    yield callback

                try:
                    link = self.driver.find_element_by_xpath("//img[@src='/webaka/icon/reg/list_n.gif']/..")
                    link.click()

                    more = True
                except NoSuchElementException:
                    more = False

    def parse_tsdr(self, response):
        data = {
            'serial': response.meta['serial'],
            'url': response.url
        }

        self.log(response.url)

        data['mark'] = response.xpath('//*[@id="summary"]/div[2]/div/div[2]/text()').extract_first().strip()
        data['owner_name'] = response.xpath('//*[@id="relatedProp-section"]/div[1]/div/div[2]/text()').extract_first().strip()
        data['owner_address'] = ' '.join(map(str.strip, response.xpath('//*[@id="relatedProp-section"]/div[2]/div/div[2]/div/text()').extract())).replace('\r\n', ' ')

        foreign_fields = len(response.xpath('//*[@id="markInfo-section"]/div[2]/div'))

        if foreign_fields == 3:
            foreign_country = response.xpath('//*[@id="markInfo-section"]/div[2]/div[3]/div[2]/text()').extract_first()
        else:
            foreign_country = response.xpath('//*[@id="markInfo-section"]/div[2]/div[2]/div[2]/text()').extract_first()

        if foreign_country is not None:
            data['foreign_country'] = foreign_country.strip()

        yield data
