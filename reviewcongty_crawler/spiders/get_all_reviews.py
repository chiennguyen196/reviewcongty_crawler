# -*- coding: utf-8 -*-
import scrapy
import re
from utils import get_time
from items import Company, Review


class GetAllReviewsSpider(scrapy.Spider):
    name = 'get-all-reviews'
    allowed_domains = ['reviewcongty.com']

    def start_requests(self):
        url = getattr(self, 'url')
        yield scrapy.Request(url=url)


    def parse(self, response):

        yield self.parse_company_info(response.xpath('//section[@class="company-info-company-page"]/div[@class="company-info"]'))

        for review in self.parse_reviews(response):
            yield review

        num_pages = self.get_num_pages(response)

        
        url = getattr(self, 'url')
        for i in range(2, num_pages + 1):
            next_page_url = url + f"?page={i}"
            yield scrapy.Request(next_page_url, callback=self.parse_reviews)

    # ==== Parse company info ======
    def parse_company_info(self, company_selector):
        
        image_logo = company_selector.css('img::attr(src)').get()
        name = company_selector.css('h2.company-info__name a::text').get().strip()
        url = company_selector.css('h2.company-info__name a::attr(href)').get()
        slug = url.split('/')[-1]
        rating_selector = company_selector.css('h2.company-info__name span.company-info__rating span')[0]
        rating = self.parse_rating(rating_selector)
        rating_count = int(company_selector.css('h2.company-info__name span.company-info__rating span.company-info__rating-count::text').get()[1:-1])
        comapny_type = "".join(company_selector.css('div.company-info__other span')[0].css('::text').getall()).strip()
        size = "".join(company_selector.css('div.company-info__other span')[2].css('::text').getall()).strip()
        address = "".join(company_selector.css('div.company-info__location span::text').getall()).strip().replace('\n', ' ')
        return Company(
            image_logo=image_logo,
            name=name,
            url=url,
            slug=slug,
            rating=rating,
            rating_count=rating_count,
            company_type=comapny_type,
            size=size,
            address=address,
        )

    def parse_rating(self, rating_selector):
        rating_elements = rating_selector.get()
        rating = rating_elements.count('"fas fa-star"')
        rating += rating_elements.count('"fas fa-star-half-alt"') * 0.5
        return rating


    def get_num_pages(self, response):
        num_pages = response.xpath("//nav[@class='pagination is-small custom-pagination']/span/b[2]/text()").get()
        return int(num_pages) if num_pages else 1

    # ===== Parse company reviews =======

    def parse_reviews(self, response):
        reviews_selector = response.xpath("//section[@class='full-reviews']/div[@class='review card']")
        for selector in reviews_selector:
            yield self.parse_one_review(selector)

    def parse_one_review(self, selector):

        review_id = selector.xpath('./header/a[@class="review__share"]/@href').get().split('/')[-1]

        header_text = selector.xpath("./header/p/text()").get().strip()

        first_parentheses_position = header_text.find('(')
        if (first_parentheses_position == -1):
            name, position = header_text, None
        else:
            name, position = header_text[:first_parentheses_position - 1], header_text[first_parentheses_position + 1:-1]

        rating = len(selector.xpath("./header/p/span//i[@class='fas fa-star']").getall())
        created = selector.xpath("./header/time/text()").get()
        created = get_time(created)

        content = "".join(selector.xpath("./div[@class='card-content']/div/div/span[not(@class='see-more__dots')]/node()").getall())

        num_likes = int(selector.xpath('./footer/span[@data-reaction="LIKE"]/text()').get().strip())
        num_dislikes = int(selector.xpath('./footer/span[@data-reaction="HATE"]/text()').get().strip())
        num_delete_requests = int(selector.xpath('./footer/span[@data-reaction="DELETE"]/text()').get().strip())

        replies = []
        for reply_selector in selector.xpath('./div[@class="review-comments"]/div[@class="comment"]'):
            reply = self.get_reply(reply_selector)
            replies.append(reply)

        return Review(
            review_id=review_id,
            name=name,
            position=position,
            rating=rating,
            created=created,
            content=content,
            num_likes=num_likes,
            num_dislikes=num_dislikes,
            num_delete_requests=num_delete_requests,
            replies=replies,
        )
        
    
    def get_reply(self, reply_selector):
        created = "".join(reply_selector.xpath('./p[@class="comment__title"]/text()').getall()).strip()
        created = get_time(created)
        name = reply_selector.xpath('./p[@class="comment__title"]/span/text()').get().replace("đề nghị xóa", "").replace("đã", "").replace("❌", "").strip()
        content = reply_selector.xpath('./p[@class="comment__content text-500"]/text()').get()
        return {
            "name": name,
            "content": content,
            "created": created
        }
        
    



