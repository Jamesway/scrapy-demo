
from scrapy_dca.items import PhysicianItem
from scrapy import Spider
from scrapy.http import TextResponse
from scrapy.shell import inspect_response
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from time import sleep

class PostSpider(Spider):

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
    driver.implicitly_wait(2)

    scrape_time = datetime.now()

    # if the results are less than this
    # the number of crawlable links was less or
    # there were dups, check the dup filtered count
    crawl_limit = 50


    def get_selenium_response(self, url):

        # http://selenium-python.readthedocs.io/navigating.html#filling-in-forms
        # use selenium to fill the form and submit
        # return a scrapy response object

        self.driver.get(url)

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
        sleep(2)

        response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

        # to debug
        # self.parse_shell(response)

        return response


    def start_requests(self):

        # overriding start_requests() is not usually necessary unless:
        # - we need to use selenium to interact with a form
        # - we want to customize parts of the request object
        #
        # if we don't override start_requests(),
        # scrapy generates requests from urls in start_urls[]
        # and calls parse() as the default callback
        #
        # for s in self.start_urls:
        #     request = self.make_requests_from_url(s)
        #     # request.callback = self.parse_shell
        #
        #     yield request
        #
        # since we need selenium for the js form interactions we're going to circumvent creating a request
        # instead we create a scrapy response object from the selenium form results
        # then we use the xpath selector of the response object to create links to follow


        for s in self.start_urls:

            # puts selenium response back into a scrapy response so we can use response.xpath and response.css
            print('crawling [' + s + '], hang tight...')
            selenium_response = self.get_selenium_response(s)

            links = selenium_response.xpath(
                '//ul[contains(@class, "actions")]/li/a[contains(@class, "button newTab")]/@href'
            ).extract()

            limit = min(self.crawl_limit, len(links))

            print('crawling ' + str(limit) + ' links of ' + str(len(links)) + ' available')

            for l in links[:limit]:
                # follow the links and use the parse_physician callback

                # for debugging
                # yield selenium_response.follow(l, self.parse_shell)

                # to pass a named parser
                # yield selenium_response.follow(l, self.parse_physician)

                # use the default parser
                yield selenium_response.follow(l)


    def parse(self, response):

        # default parser
        # even though you are't required to create a start_requests method,
        # you'll want to have a parser defined or nothing happens to the reponse data
        # we could name like below or have multiple named parsers
        # def parse_physician(self, response):

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
        item['certifications'] = list(filter(None, response.css('.survAnswer')[8].re(r'>(.*?)<')))

        item['scraped_at'] = self.scrape_time
        yield item


    # helps debugging extractions
    def parse_shell(self, response):
        # We want to inspect one specific response.
        if "search.dca.ca.gov" in response.url:
            inspect_response(response, self)