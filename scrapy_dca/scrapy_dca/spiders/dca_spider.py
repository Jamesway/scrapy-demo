import scrapy
from time import time, sleep, strptime, strftime
from scrapy_dca.items import PhysicianItem
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request, TextResponse
from scrapy.shell import inspect_response
from selenium import webdriver
from selenium.webdriver.support.ui import Select

class PostSpider(scrapy.Spider):
  name = "dca_spider"
  allowed_domains = ["search.dca.ca.gov"]
  start_urls = []

  #https://stackoverflow.com/a/47603459
  options = webdriver.ChromeOptions()
  options.add_argument('--disable-extensions')
  options.add_argument('--headless')
  options.add_argument('--disable-gpu')
  options.add_argument('--no-sandbox')
  driver = webdriver.Chrome(chrome_options=options)

  scrape_time = time()

  # overwrite start_requests so we can use our generated requests for use with the SeleniumChrome middleware
  def start_requests(self):

      self.start_urls = self.submit_form()
      for link in self.start_urls:
          self.logger.info('https://search.dca.ca.gov' + link)
          request = self.make_requests_from_url('https://search.dca.ca.gov' + link)

          #switch for SeleniumChrome middleware
          request.meta['driver'] = 'chrome'
          #request.callback = self.parse_shell
          yield request


  # crawl starts with a JS heavy form submission - selenium, chromedriver required
  def submit_form(self):

    self.driver.get('https://search.dca.ca.gov/physicianSurvey')
    sleep(2)

    # fill the form and submit
    #http://selenium-python.readthedocs.io/navigating.html#filling-in-forms
    zipcode = self.driver.find_element_by_id('pzip')
    zipcode.send_keys('90025')
    license = Select(self.driver.find_element_by_id('licenseType'))
    license.select_by_value('8002')
    status = Select(self.driver.find_element_by_id('primaryStatusCodes'))
    status.select_by_value('20')
    discipline = Select(self.driver.find_element_by_id('hasDiscipline'))
    discipline.select_by_value('Yes')
    self.driver.find_element_by_id('srchSubmitHome').click()
    sleep(5)

    response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
    return response.css('a.button.newTab::attr(href)').extract()

  # default parser
  def parse(self, response):

      item = PhysicianItem()

      item['name'] = response.css('#name::text').extract_first(default='').strip()
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
      yield item

  # helps debugging extractions
  def parse_shell(self, response):
      # We want to inspect one specific response.
      if "search.dca.ca.gov" in response.url:
          inspect_response(response, self)
