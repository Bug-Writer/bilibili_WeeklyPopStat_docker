import scrapy
from BiliStat.items import VideoInfoItem
from scrapy.http import Request

class BiliSpider(scrapy.Spider):
    name = 'BiliSpider'
    allowed_domains = ['bilibili.com']
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

    def start_requests(self):
        headers = {'User-Agent': self.user_agent}
        issue_count = getattr(self, 'issue', 5)
        for i in range(1, int(issue_count) + 1):
            url = f'https://www.bilibili.com/v/popular/weekly?num={i}'
            yield Request(url, self.parse_page, headers = headers)

    def parse_page(self, response):
        video_hrefs = response.css('.video-card a::attr(href)').getall()
        for href in video_hrefs:
            if href.startswith('//www.bilibili.com/v'):
                yield response.follow(href, self.parse_video)

    def parse_video(self, response):
        item = VideoInfoItem()
        item['video_title'] = response.css('h1.video-title::text').get()
        item['video_time']  = response.css('span.pubdate-text::text').get().strip()
        item['video_tags']  = response.css('a.tag-link::text').getall()
        return item

