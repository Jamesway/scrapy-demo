# Scrapy Python Scraper Demo
Scrapy demo using my [scrapy docker image](https://hub.docker.com/r/jamesway/scrapy/) to scrape the [California DCA Physician Survey](https://search.dca.ca.gov/physicianSurvey).
The Physician Survey uses lots of javascript that native scrapy can't handle. This demo uses Selenium and Chrome/Chromedriver to handle js interactions.

Since the demo requires a js controlled form to be filled we initiate the form interactions with Selenium then hand off to scrapy, then back to Selenium....

Scrapy is built on the Python Twisted framework, ie it operates in a non-blocking fashion, so Spiders operate with concurrency.


## Requirements
- ~~Python 3.6~~
- ~~Scrapy~~
- ~~Selenium~~
- ~~Chrome/Chrome Driver~~
- ~~Beautifulsoup 4~~
- ~~SqlAlchemy~~
- Docker

## Usage
```
cd scrapy-demo

# copy the sample.env to .env and update the values in .env
cp .sample-env .env

# bring up the mariadb service
docker-compose up -d

# crawl the dca -  it make take a several seconds (20 - 30) to get started
# the dca is a gov site so it's not super responsive
# "run --rm" removes the container when finished
docker-compose run --rm scrapy crawl dca_spider

# verify the data
# connect to mariadb using credentials in .env and the docker machine ip (usually 192.168.99.100)
```

**Note: docker-compose uses a named volume for the mariadb service so the data will persist.**  
To remove the volume: ```docker volume rm [first 3 or 4 chars of id]```

## To Build A Spider...

### Start a Project
There are a lot of similar concepts between scrapy and django  
[scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)  

```
# startproject cannot be run with docker-compose since it creates the docker-compose file
docker run --rm -v $(pwd):/code jamesway/scrapy startproject [scrapy_project_name]
```

### Create a spider for a domain
```
cd [scrapy_project_name]

# your spider will be created in [scrapy_project_name]/[scrapy_project_name]/spiders/
docker-compose run --rm scrapy genspider [spider_name] [domain.com]

# or with docker
docker run --rm -v $(pwd):/code jamesway/scrapy genspider [spider_name] [domain.com]
```  

## Files of Note
### scrapy.cfg
scrapy.cfg points to the settings file and the project, if you did scrapy startproject..., leave these as is

### settings.py
```
# adjust these
ROBOTSTXT_OBEY

CONCURRENT_REQUESTS

DOWNLOAD_DELAY

# make sure you "turn on" your middleware classes in settings.py
SPIDER_MIDDLEWARES

# enable if you have code for database persistence
ITEM_PIPELINES

# debug is default and gets pretty verbose, maybe use INFO once you get a handle on your spider
LOG_LEVEL
```  

### items.py
where you define model classes for your data

### middlewares.py
Once you get a handle on request and response objects you can plug them in to middlewares or pipelines. To use selenium we use a middleware class to take the request object, pass it to chromedriver and plug the response back into a scrapy response object to be parsed by the spider's parse method(s).

### pipelines.py
Allows you to add code to populate a databases.

### [spider_name].py
Scrapy spiders essentially do two things. They generate requests and parse the response. Methods in your spider will be parsers that consume response objects and possibly generate request objects that yield response objects for other parsers to consume

#### parse()  
A request returns a response that gets parsed by the default method "parse" - this is where the magic happens. You can add custom parse methods and change the callback property on the request to enable them.  

#### scrapy shell  
While trying to figure out how to parse the response, it helps to have a scrapy shell parse method for debugging. With the scrapy shell, you can test extracting data from the response object using CSS or XPath selectors.
- Start with response.body
- The extract() method returns a list.
- To get the "first" string, use extract_first() or extract()[0]
- Ctrl+d exits the shell.

## Misc
- chrome driver options
https://stackoverflow.com/a/47603459

- set Referer
https://stackoverflow.com/a/14876164

- submit a form from an initial response (form page load)
https://stackoverflow.com/a/11219623
