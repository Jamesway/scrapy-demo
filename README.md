## Scrapy Python Scraper Demo
Scrapy demo using my Scrapy Docker image to scrape the California DCA Physician Survey. The Physician Survey uses lots of javascript that scrapy can't handle. This demo uses selenium and chrome/chromedriver to handle js interactions.  

Also, Scrapy is built on the Python Twisted framework, ie it operates in a non-blocking fashion, so Spiders aren't procedural.

### Requirements
Docker

### Installation
Clone this repo and unzip

### Usage
```
cd scrapy_dca

# scrape to a json list
docker run --rm -v $(pwd):/code jamesway/scrapy crawl dca_spider -o result.jl
```

## Build Your Own Spider

1. Start a Project
https://docs.scrapy.org/en/latest/intro/tutorial.html
```
docker run --rm -v $(pwd):/code jamesway/scrapy startproject [scrapy_project_name]
```

2. Create a spider for a domain
```
cd [scrapy_project_name]

# your spider will be created in [scrapy_project_name]/[scrapy_project_name]/spiders/
docker run --rm -v $(pwd):/code jamesway/scrapy genspider [spider_name] [domain.com]
```  

## When building your spider...
### scrapy.cfg
scrapy.cfg points to the settings file and the project, if you did scrapy startproject..., you can probably leave these as is

### settings.py
```
# adjust these
ROBOTSTXT_OBEY
CONCURRENT_REQUESTS
DOWNLOAD_DELAY
SPIDER_MIDDLEWARES # make sure you "turn on" your middleware classes in settings.py
LOG_LEVEL # debug is default and gets pretty verbose, maybe use INFO once you get a handle on your spider
```  

### items.py
Allows you to define a model class for your data, which is especially useful if you're going to output json  

### middlewares.py
Once you get a handle on request and response objects you can plug them in to middlewares or pipelines. To use selenium we use a middleware class to take the request object, pass it to chromedriver and plug the response back into a scrapy response object to be parsed by the spider's parse method(s).  

### pipelines.py
Allows you to add code to populate a remote db.

### parse()
A request returns a response that gets parsed by the default method "parse" - this is where the magic happens. You can add custom parse methods and change the callback property on the request to enable them.  

### scrapy shell
While trying to figure out how to parse the response, it helps to have a scrapy shell parse method. With the scrapy shell, you can test extracting data from the response object using CSS or XPath. The extract method returns a list. To get the "first" string, use extract_first(). On mac, ctl+d exits the shell, BUT you need to ctl+c to exit the spider. I never found these to work correctly - probably Docker related.  

### other notes
chrome driver options
https://stackoverflow.com/a/47603459

set Referer
https://stackoverflow.com/a/14876164

submit a form from an initial response (form page load)
https://stackoverflow.com/a/11219623
