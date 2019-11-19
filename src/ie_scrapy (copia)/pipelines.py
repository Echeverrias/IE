# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import sqlite3
from datetime import date
from dateutil.relativedelta import relativedelta

class IePipeline(object):

    def str_cleanup(self, string):
        return string.strip()

    def int_cleanup(self, string):
        try:
            return int(re.findall(r'\d+', string)[0])
        except:
            return None

    def url_cleanup(self, pathname_or_href):
        origin = 'https://www.infoempleo.com/'
        href = pathname_or_href
        if not (origin in pathname_or_href):
            href = origin + pathname_or_href
        return href

    def process_item(self, item, spider):
        return item


class JobPipeline(IePipeline):

    def country_cleanup(self, string):
        return string.replace('Empleo en Otros Paises', "").replace('Empleo en ', "")

    def nationality_cleanup(self, string):
        if 'extranjero' in string:
            return "internacional"
        else:
            return "nacional"

    def area_cleanup(self, string):
        return string.replace('Area de ', "")

    def company_id_cleanup(self, url):
        try:
            href = self.url_cleanup(url)
            return href.split('/')[-2]
        except:
            return ""

    def date_cleanup(self, string):
        today = date.today()
        job_date = today
        try:
            number = self.int_cleanup(string)
            if 'dia' in string:
                job_date = today - relativedelta(days=number)
            elif 'mes' in string:
                job_date = today - relativedelta(months=number)
            elif 'año' in string:
                job_date = today - relativedelta(years=number)
        except:
            pass
        return job_date


    def process_item(self, item, spider):
        if item.get_name() == 'JobItem':
            item['name'] = self.str_cleanup(item['name'])
            item['requisites'] = self.str_cleanup(item['requisites'])
            item['_id'] = self.int_cleanup(item['_id'])
            item['job_date'] = self.date_cleanup(item['job_date'])
            item['subscribers'] = self.int_cleanup(item['subscribers'])
            item['company_id'] = self.company_id_cleanup(item['company_id'])
            item['nationality'] = self.nationality_cleanup(item['nationality'])
            item['area'] = self.area_cleanup(item['area'])
            if item['nationality'] == "nacional":
                item['country'] = 'España'
            else:
                item['country'] = self.country_cleanup(item['country'])
        return item


class SqlitePipeline(object):

    db = "ie2.db"
    def __init__(self):
        self.create_connection()
        self.drop_tables() #%
        self.create_tables()


    def create_connection(self):
        self.connection = sqlite3.connect(self.db)
        self.curr = self.connection.cursor()


    def create_tables(self):
        self.create_jobs_table()
        self.create_companies_table()

    def drop_tables(self):
        self.curr.execute("""drop table if exists job""")
        self.connection.commit()
        self.curr.execute("""drop table if exists companies""")
        self.connection.commit()


    def create_jobs_table(self):
        self.curr.execute("""create table IF NOT EXISTS job( 
        id integer,
        name text,
        link text,
        company_id text,
        area text,
        requisites text, 
        city text,
        country text,
        nationality text,
        subscribers integer,
        time text
        )""")
        self.connection.commit()

    def create_companies_table(self):
        self.curr.execute("""create table IF NOT EXISTS companies( 
                id integer,
                name text,
                link text,
                city text,
                category text,
                description text, 
                vacancies integer
               )""")
        self.connection.commit()

    def store_item(self, item):
        item_name = item.get_name()
        if item_name == 'JobItem':
            self.insert_job(item.tuple_of_values())
        elif item_name == 'CompanyItem':
            self.insert_company(item.tuple_of_values())

    def insert_job(self, tuple):
        print('INSERT JOB')
        print(tuple)
        print([type(e) for e in tuple])
        self.curr.execute("""insert into job values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple)
        self.connection.commit()

    def insert_company(self, tuple):
        self.curr.execute("""insert into job values(?, ?, ?, ?, ?, ? ,?)""", tuple)
        self.connection.commit()

    def process_item(self, item, spider):
        self.store_item(item)
        return item

    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()

