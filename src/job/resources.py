from import_export import resources
from .models import Job, Company, City, Province, Community, Country

class JobResource(resources.ModelResource):
    class Meta:
        model = Job

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company


class CityResource(resources.ModelResource):
    class Meta:
        model = City


class ProvinceResource(resources.ModelResource):
    class Meta:
        model = Province

class CommunityResource(resources.ModelResource):
    class Meta:
        model = Community

class CountryResource(resources.ModelResource):
    class Meta:
        model = Country