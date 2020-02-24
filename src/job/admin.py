import copy
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import Job, Company, Province, City, Community, Country, Language
from .resources import JobResource

#admin.site.register(Job)

admin.site.site_header = "Infoempleo";
admin.site.site_title = "Infoempleo";


def custom_titled_filter(title):
    print(dir(admin))
    print()
    class Wrapper(admin.RelatedFieldListFilter):
        def __new__(cls, *args, **kwargs):
            print(args)
            instance = admin.RelatedFieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


def apply_upper_to_author(modelAdmin, request, queryset):
    for item in queryset:
        item.author = item.author.upper()
        item.save()

apply_upper_to_author.short_description = 'Apply upper to the author field'


@admin.register(Job) #admin.site.register(Quote, QuoteAdmin)
class JobAdmin(ImportExportModelAdmin):
    resource_class = JobResource
    # Si no se declara 'list_display' mostrará por defecto su conversión a string
    list_display = ['name', 'state', 'type', 'contract', 'working_day', 'category_level', 'area', 'company', '_location']
    list_filter =  ['type','contract','working_day', 'nationality', 'area']
    #search_fields = ['name', 'id', 'functions', 'requirements', 'it_is_offered']
    search_fields = ['name', 'id', 'functions', 'requirements', 'it_is_offered']

    # Para mostrar campos no editables
    readonly_fields = ['created_at', 'updated_at']
    #fields = ['author', 'quote'] # fields = [('author', 'quote')]
    fieldsets = [
        ('Estado', {
            'fields': [('state'), ('first_publication_date', 'last_update_date', 'expiration_date')]
        }),
        ('Principal', {
            'fields': [('name'), ('id', 'link', 'type'),('summary'),('cities', 'province', 'country'),('cityname', 'provincename','countryname')]
        }),
        ('Summary1', {
            'fields': [('_experience', '_salary', '_working_day', '_contract')]
        }),
        ('Summary2', {
            'fields': [('minimum_years_of_experience', 'recommendable_years_of_experience'), ('minimum_salary', 'maximum_salary'), ('working_day', 'contract')]
        }),
        ('Offer', {
            'fields': ['area','description', 'functions', 'requirements', 'it_is_offered', 'category_level', 'languages']
        }),
        ('Compañía', {
            'fields': ['company']
        }),
        ('Vacantes', {
            'fields': [('vacancies', 'vacancies_update','registered_people')]
        }),
        ('Tags', {
            'fields': ['tags']
        }),
        ('Info', {
            'fields': [('created_at', 'updated_at')]
        })
    ]

    def _location(self, obj):
        cities = obj.cities.all()[0:3]
        if cities:
            city_names = [city.name for city in cities]
            return f'{", ".join(city_names)}{" - " + obj.province.name if obj.province and not obj.province.name in city_names else ""} ({cities[0].country.name})'
        else:
            province = obj.province
            if province:
                return f'{province.name} {"(" + obj.country.name + ")" if obj.country else ""}'
            else:
                None

    # Field name of '_location' in list_display
    _location.short_description = 'Location'


    #actions = [apply_upper_to_author]

class JobInLine(admin.TabularInline):
    model = Job
    extra = 0

@admin.register(Company) #admin.site.register(Quote, QuoteAdmin)
class CompanyAdmin(ImportExportModelAdmin): #class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', '_jobs']
    list_filter = (('city__province__name', custom_titled_filter('Province name') ),)
    search_fields = ['name', 'city__name']
    """
    fieldsets = [
        ('Company', {
            'fields': ['description', 'category', 'offers', city']
        }),

    ]
    """
    inlines = [JobInLine]

    def _jobs(self, obj):
        #return obj.quotes.all().count()
        return obj.jobs.all().count()

    def get_field(self, name, many_to_many=True):
        """
        Returns the requested field by name. Raises FieldDoesNotExist on error.
        """
        to_search = many_to_many and (self.fields + self.many_to_many) or self.fields
        if hasattr(self, '_copy_fields'):
            to_search += self._copy_fields
        for f in to_search:
            if f.name == name:
                return f
        if not name.startswith('__') and '__' in name:
            f = None
            model = self
            path = name.split('__')
            for field_name in path:
                f = model._get_field(field_name)
                if isinstance(f, ForeignKey):
                    model = f.rel.to._meta
            f = copy.deepcopy(f)
            f.name = name
            if not hasattr(self, "_copy_fields"):
                self._copy_fields = list()
            self._copy_fields.append(f)
            return f
        raise FieldDoesNotExist('%s has no field named %r' % (self.object_name, name))

    _jobs.short_description = 'Count of jobs'
    _jobs.admin_order_field = 'job'



@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    list_display = ['name', 'province', 'country', '_jobs_count']
    list_filter = ['province', 'country']
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
    list_display = ['name', '_cities', 'country']
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

class CommunityInLine(admin.TabularInline):
    model = Community
    extra = 0



@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = ['name', '_cities']
    search_fields = ['name']

    def _cities(self, obj):
        self._init_inlines(obj)
        return obj.cities.all().count()

    def _init_inlines(self, obj):
        if obj.name == 'España':
            CountryAdmin.inlines = [CommunityInLine]
        else:
            CountryAdmin.inlines = [CityInLine]


@admin.register(Language)
class LanguageAdmin(ImportExportModelAdmin):
    list_display = ['name', 'level']
    search_fields = ['name']

