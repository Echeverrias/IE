from django.db import models
from django_mysql.models import ListCharField


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']


class Community(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    capital_id = models.IntegerField(null=True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='communities',
                                null=True, blank=True)

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        ordering = ['name']


class Province(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='provinces',
                                null=True, blank=True)
    community = models.ForeignKey(Community,
                                on_delete=models.CASCADE,
                                related_name='provinces',
                                null=True)
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    community_number = models.IntegerField(null=True, blank=True)
    capital_id = models.IntegerField(null=True)

    def __str__(self):
        return "%s" % (self.name)
    class Meta:
        verbose_name = "Province"
        ordering = ['name']

class City (models.Model):
    id = models.AutoField(primary_key=True)
    province = models.ForeignKey(Province,
                                  on_delete=models.CASCADE,
                                    related_name='cities',
                                 null = True, blank = True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='cities',
                                null = True, blank = True)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=30, null=True, default='',blank = True)

    latitude = models.FloatField(null=True, blank = True)
    longitude = models.FloatField(null=True, blank = True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.province)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

class Company(models.Model):
    company_link = models.URLField(null=True)
    company_name = models.CharField(primary_key=True, max_length=100)
    company_description = models.TextField(null=True)
    company_city_name = models.CharField(max_length=50, null=True)
    company_city = models.ForeignKey(City,
                            on_delete=models.CASCADE,
                            related_name='companies',
                            null = True, blank = True)
    company_category = models.CharField(null=True, max_length=100)
    company_offers = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True)  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)  # models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['company_name']

class Job(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    link = models.URLField(null=True)
    type = models.CharField(
        max_length=23,
        choices=(
        ('ofertas-internacionales', 'Empleo internacional'),
        ('trabajo', 'Empleo nacional'),
        ('primer-empleo', 'Primer empleo')
    ),
        default='trabajo',
    )
    summary = ListCharField(base_field=models.CharField(max_length=100),
        size=6,
        max_length=(6 * 101), null=True)
    _experience = models.CharField(max_length=30, null=True, blank=True)
    _salary = models.CharField(max_length=30, null=True, blank=True)
    _contract = models.CharField(max_length=30, null=True, blank=True)
    _working_day = models.CharField(max_length=30, null=True, blank=True)
    minimum_years_of_experience = models.IntegerField(null=True, blank=True, default=0)
    recommendable_years_of_experience = models.IntegerField(null=True, blank=True, default=0)
    minimum_salary = models.IntegerField(null=True, blank=True)
    maximum_salary = models.IntegerField(null=True, blank=True)
    working_day = models.CharField(max_length=30, null=True, blank=True)
    contract = models.CharField(max_length=30, null=True, blank=True)
    city_name = ListCharField(base_field=models.CharField(max_length=100),
        size=6,
        max_length=(6 * 101), null=True)
    cities = models.ManyToManyField(City,
                            related_name='jobs',
                            null = True, blank = True)
    province_name = models.CharField(null=True, max_length=100, blank=True)  # Model
    province = models.ForeignKey(Province,
                             on_delete=models.CASCADE,
                             related_name='jobs',
                             null=True, blank=True)
    country = models.ForeignKey(Country,
                             on_delete=models.CASCADE,
                             related_name='jobs',
                             null=True, blank=True)
    country_name = models.CharField(null=True, max_length=30) #Model
    nationality = models.CharField(max_length=30)
    registered_people = models.IntegerField()
    job_date = models.DateField(null=True)
    expiration_date = models.DateField(null=True)  # models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    functions = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    it_is_offered = models.TextField(null=True, blank=True) #NULL constraint
    tags = models.TextField(null=True, blank=True) #Model
    area = models.CharField(null=True,max_length=100, blank=True) #Model
    category_level = models.CharField(null=True,max_length=100, blank=True)
    vacancies = models.IntegerField()
    vacancies_update = models.IntegerField(null=True, blank=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs', null=True)
    """
    company_link = models.URLField()
    company_name = models.CharField(max_length=100)
    company_description = models.TextField()
    company_city = models.CharField(max_length=30)
    company_category = models.CharField(max_length=100)
    """

    created_at = models.DateTimeField(null=True)  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)  # models.DateTimeField(auto_now=True)


    def __str__(self):
        return "%s - %s (%s)" % (self.name, self.type, self.country)


    class Meta:
        verbose_name = "Job"
        ordering = ['-created_at','job_date', 'name']  # El - delante del nombre del atributo indica que se o



class SpiderState(models.Model):

    url = models.URLField(primary_key=True)
    last_page = models.IntegerField(null=True, default=1)
    total_pages = models.IntegerField(default=0)
    total_results = models.IntegerField(default=0)
    default_results_showed = models.IntegerField(default=20)
    results_count = models.IntegerField(null=True, default=0)
    last_result_parsed = models.IntegerField(null=True, default=0)
    last_page_parsed = models.IntegerField(null=True, default=0)
    scrapping_completed = models.BooleanField(default=False)



