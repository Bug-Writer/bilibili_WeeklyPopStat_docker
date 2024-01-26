# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoInfoItem(scrapy.Item):
    video_title = scrapy.Field()
    video_time  = scrapy.Field()
    video_tags  = scrapy.Field()
