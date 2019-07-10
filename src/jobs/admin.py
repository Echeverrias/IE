from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Job, Company, Province, City, Community, Country
from .resources import JobResource

#admin.site.register(Job)

admin.site.site_header = "Infoempleo";
admin.site.site_title = "Infoempleo";


def apply_upper_to_author(modelAdmin, request, queryset):
    for item in queryset:
        item.author = item.author.upper()
        item.save()

apply_upper_to_author.short_description = 'Apply upper to the author field'


@admin.register(Job) #admin.site.register(Quote, QuoteAdmin)
class JobAdmin(ImportExportModelAdmin):
    resource_class = JobResource
    # Si no se declara 'list_display' mostrará por defecto su conversión a string
    list_display = ['name', 'type', 'company']
    list_filter =  ['type','nationality', 'area', 'company']
    search_fields = ['name', 'area', 'id']
    # !! fields = ['author', 'quote', ('created_at', 'updated_at')]
    # 'created_at y updated_a no pueden aparecer porque son valores no editables
    #fields = ['author', 'quote'] # fields = [('author', 'quote')]
    fieldsets = [
        ('Principal', {
            'fields': [('id', 'link', 'type'),('summary','job_date'),('cities', 'province','country'),('city_name', 'province_name','country_name')]
        }),
        ('Summary1', {
            'fields': [('_experience', '_salary', '_working_day', '_contract')]
        }),
        ('Summary2', {
            'fields': [('minimum_years_of_experience', 'recommendable_years_of_experience'), ('minimum_salary', 'maximum_salary'), ('working_day', 'contract')]
        }),
        ('Offer', {
            'fields': ['area','description', 'functions', 'requirements', 'it_is_offered', 'category_level']
        }),
        ('Offer', {
            'fields': ['company']
        }),
        ('Vacancies', {
            'fields': [('vacancies', 'vacancies_update','registered_people')]
        }),
        ('Tags', {
            'fields': ['tags']
        }),
        ('Info', {
            'fields': [('expiration_date', 'created_at', 'updated_at')]
        })
    ]
    #actions = [apply_upper_to_author]

class JobInLine(admin.TabularInline):
    model = Job
    extra = 0

@admin.register(Company) #admin.site.register(Quote, QuoteAdmin)
class CompanyAdmin(ImportExportModelAdmin): #class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', '_jobs']
    list_filter = ['company_name', 'company_city']
    search_fields = ['company_name', 'company_id']
    """
    fieldsets = [
        ('Company', {
            'fields': ['company_description', 'company_category', 'company_offers', company_city']
        }),

    ]
    """
    inlines = [JobInLine]

    def _jobs(self, obj):
        #return obj.quotes.all().count()
        return obj.jobs.all().count()

    _jobs.short_description = 'job'
    _jobs.admin_order_field = 'job'



@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    list_display = ['name', 'province', '_jobs_count']
    list_filter = ['province']
    search_fields = ['name']
   # inlines = ['_jos']

    def _jobs_count(self, obj):
        return obj.jobs.all().count()
    
    def _jobs(self, obj):
        return obj.jobs.all()

class CityInLine(admin.TabularInline):

    model = City
    extra = 0



@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    list_display = ['name', '_cities']
    search_fields = ['name']

    def _cities(self, obj):
        return obj.cities.all().count()

    inlines = [CityInLine]


class ProvinceInLine(admin.TabularInline):
    model = Province
    extra = 0


@admin.register(Community)
class CommunityAdmin(ImportExportModelAdmin):
    list_display = ['name', '_provincies']
    search_fields = ['name']

    def _provincies(self, obj):
        return obj.provinces.all().count()

    inlines = [ProvinceInLine]



@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = ['name', '_cities', '_jobs']
    search_fields = ['name']

    def _cities(self, obj):
        return obj.cities.all().count()

    def _jobs(self, obj):
        return obj.jobs.all().count()











