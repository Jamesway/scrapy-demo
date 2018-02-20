# Scrapy-Demo

Scrapy demo using the California DCA Physician Survey. The Physician Survey uses lots of javascript that scrapy can't handle. This demo uses selenium and chrome/chromedriver to handle js interactions.

I made a Docker image to run the demo: Jamesway/scrapy-selenium-chrome

TL;DR

list commands for the scrapy project
```
docker run --rm -v $(pwd):/code -w /code/scrapy_dca scrapy-selenium-chrome
```

scrape to a json list
```
docker run --rm -v $(pwd):/code -w /code/scrapy_dca scrapy-selenium-chrome crawl dca_spider -o result.jl
```

## Before you start...
Scrapy is built on the twisted framework, ie it operates in a non-blocking fashion - Spiders aren't procedural.


## Create Scrapy Project

from https://docs.scrapy.org/en/latest/intro/tutorial.html

```
scrapy startproject [projectName]
```

creates a scrapy project with files and folders

## Before you code your spider, it helps to be aware of these

### scrapy.cfg
scrapy.cfg points to the settings file and the project, if you did scrapy startproject..., you can probably leave these as is

### settings.py
Here's all the good stuff - of note:

ROBOTSTXT_OBEY,
CONCURRENT_REQUESTS,
DOWNLOAD_DELAY (better than sleeping),
SPIDER_MIDDLEWARES (make sure you "turn on" your middleware classes in settings.py),
LOG_LEVEL (debug is default and gets pretty verbose, maybe use INFO once you get a handle on your spider)

### items.py
You can define a model class for your data, which is especially useful if you're going to output json

### middlewares.py
Once you get a handle on request and response objects you can plug them in to middlewares or pipelines. To use selenium we use a middleware class to take the request object, pass it to chromedriver and plug the response back into a scrapy response object to be parsed by the spider's parse method(s).

### pipelines.py
I didn't create a pipeline, but this is where you could, for example, stream data to a remote db.

## Spiders...
...reside in /spiders

### parse()
A request returns a response that gets parsed by the default method "parse" - this is where the magic happens. You can add custom parse methods and change the callback property on the request to enable them.

### scrapy shell
While trying to figure out how to parse the response, it helps to have scrapy shell parse method. With the scrapy shell, you can test out extracting data from the response object. Css extractions with regex worked well for me, but you can also extract with xpath. The extract method returns a list, to get the "first" string, use extract_first() - unless you want a list. On mac, ctl+d exits the shell, BUT you need to ctl+c to exit the spider - ctl+c never worked for me.


## other notes
chrome driver options
https://stackoverflow.com/a/47603459

set Referer
https://stackoverflow.com/a/14876164

submit a form from an initial response (form page load)
https://stackoverflow.com/a/11219623
