import json
from scrapy_dca.items import PhysicianItem
import scrapy
from scrapy.http import TextResponse
from scrapy.shell import inspect_response
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from time import sleep

class PostSpider(scrapy.Spider):
    name = 'dca_spider'
    allowed_domains = ['search.dca.ca.gov']
    start_urls = ['https://search.dca.ca.gov/physicianSurvey']

    #https://stackoverflow.com/a/47603459
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(5)

    scrape_time = datetime.now()

    # def start_requests(self):
    #     # overwrite start_requests if we need to
    #     # otherwise scrapy generates start_requests from start_urls[]
    #     # and calls parse() as the default callback
    #
    #     for s in self.start_urls:
    #         request = self.make_requests_from_url(s)
    #         # request.callback = self.parse_shell
    #
    #         yield request


    # use selenium to generate a form response
    def get_selenium_response(self, url):


        self.driver.get(url)

        # fill the form and submit
        # http://selenium-python.readthedocs.io/navigating.html#filling-in-forms
        zipcode = self.driver.find_element_by_id('pzip')
        zipcode.send_keys('90025')
        license = Select(self.driver.find_element_by_id('licenseType'))
        license.select_by_value('8002')
        status = Select(self.driver.find_element_by_id('primaryStatusCodes'))
        status.select_by_value('20')
        discipline = Select(self.driver.find_element_by_id('hasDiscipline'))
        discipline.select_by_value('No')
        self.driver.find_element_by_id('srchSubmitHome').click()

        # this gives time for the slow loading results page to load
        sleep(5)

        response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
        #self.parse_shell(response)
        return response


    def parse_physician(self, response):

        item = PhysicianItem()

        # name format is last, first - i'm reversing it
        name = response.css('#name::text').extract_first(default='').strip().split(", ")
        item['name'] = name[1] + ' ' + name[0]
        self.logger.info('parsing response for: ' + item['name'])
        item['prev_name'] = response.css('#prevName::text').extract_first(default='').strip()
        item['source'] = response.css('#clntType::text').extract_first().strip()
        item['license'] = response.css('#licDetail').re_first(r'Licensing details for: (.*)</h2>').strip()
        item['license_type'] = response.css('#licType::text').extract_first(default='').strip()
        item['issue_date'] = response.css('#issueDate::text').extract_first().strip()
        item['exp_date'] = response.css('#expDate::text').extract_first().strip()

        item['status1'] = response.css('#primaryStatus::text').extract_first(default='').strip()
        item['status2'] = response.css('#C_modType::text').extract_first(default='').strip()
        item['school'] = response.css('#schoolName::text').extract_first(default='').strip()
        item['graduation'] = response.css('#gradYear::text').extract_first(default='').strip()
        item['practice_location'] = response.css('.survAnswer')[2].re_first(r'(\d{5})')
        item['ethnicity'] = response.css('.survAnswer')[10].re_first(r'<div class="survAnswer">(.*)</div>').strip()
        item['language'] = response.css('.survAnswer')[11].re_first(r'<div class="survAnswer">(.*)</div>').strip()
        item['gender'] = response.css('.survAnswer')[12].re_first(r'<div class="survAnswer">(.*)</div>').strip()

        # non-greedy matches
        item['services'] = list(filter(None, response.css('.survAnswer')[7].re(r'>(.*?)<')))
        item['address'] = response.css('#address .wrapWithSpace').re(r'>(.*?)<br')
        item['certifications'] = json.dumps(list(filter(None, response.css('.survAnswer')[8].re(r'>(.*?)<'))))

        item['scraped_at'] = self.scrape_time
        yield item


    # default parser
    def parse(self, response):

        print(response.url)

        # Here you got response from webdriver
        # you can use selectors to extract data from it
        selenium_response = self.get_selenium_response(response.url)

        for link in selenium_response.xpath('//ul[contains(@class, "actions")]/li/a[contains(@class, "newTab")]/@href'):

            # follow the links and use the parse_physician callback
            #yield selenium_response.follow(link, self.parse_shell)
            yield selenium_response.follow(link, self.parse_physician)


    # helps debugging extractions
    def parse_shell(self, response):
        # We want to inspect one specific response.
        if "search.dca.ca.gov" in response.url:
            inspect_response(response, self)