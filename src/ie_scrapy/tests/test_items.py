#import sys, os
#sys.path.append(os.path.abspath(os.path.join('.', 'ie_scrapy')))
#print(os.path.abspath(os.path.join('.', 'ie_scrapy')))
from django.test import TestCase
from ie_scrapy.items import BaseItem, JobItem, CompanyItem
from job.models import Job


class TestBaseItem(TestCase):


    def test_get_model_name(self):
        job_item = JobItem()
        self.assertEqual(job_item.get_model_name(), 'Job')
        company_item = CompanyItem()
        self.assertEqual(company_item.get_model_name(), 'Company')
