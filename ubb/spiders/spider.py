import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import UbbItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class UbbSpider(scrapy.Spider):
	name = 'ubb'
	start_urls = ['https://www.ubb.bg/news']

	def parse(self, response):
		post_links = response.xpath('//div[@class="view-more-news"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[text()="Следваща"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//div[@class="position-info-row news"]/p//text()').get()
		title = response.xpath('//div[@class="about-page-txt-block anim-block"]/h3/text()').get()
		content = response.xpath('//div[@class="txt-holder"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=UbbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
