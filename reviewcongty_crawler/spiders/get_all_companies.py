# -*- coding: utf-8 -*-
import scrapy
import urllib.parse


class GetAllCompaniesSpider(scrapy.Spider):
    name = 'get-all-companies'
    allowed_domains = ['reviewcongty.com']

    def start_requests(self):
        n_pages = int(getattr(self, 'n_pages', 367))
        for i in range(1, n_pages + 1):
            url = f"https://reviewcongty.com/?tab=latest&page={i}"
            yield scrapy.Request(url=url)

    def parse(self, response):
        company_list_selector = response.css('div.company-item')

        for comany_selector in company_list_selector:
            comapny_info = self.parse_company_info(comany_selector)
            yield comapny_info


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
        return {
            "image_logo": image_logo,
            "name": name,
            "url": urllib.parse.urljoin('https://reviewcongty.com/', url),
            "slug": slug,
            "rating": rating,
            "rating_count": rating_count,
            "comapny_type": comapny_type,
            "size": size,
            "address": address
        }


    def parse_rating(self, rating_selector):
        rating_elements = rating_selector.get()
        rating = rating_elements.count('"fas fa-star"')
        rating += rating_elements.count('"fas fa-star-half-alt"') * 0.5
        return rating
