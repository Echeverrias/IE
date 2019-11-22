from django.db import models
from django.urls import reverse
from django_mysql.models import ListCharField
import language_utilities
from simple_history.models import HistoricalRecords
from .managers import JobManager


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return "%s" % (self.name)


class Community(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    capital_id = models.IntegerField(null=True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='communities',
                                null=True, blank=True)

    class Meta:
        verbose_name = "Community"
        verbose_name_plural = "Communities"
        ordering = ['name']

    def __str__(self):
        return "%s" % (self.name)


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

    class Meta:
        verbose_name = "Province"
        ordering = ['name']


    def __str__(self):
        return "%s" % (self.name)



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
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=30, null=True, default='',blank = True)

    latitude = models.FloatField(null=True, blank = True)
    longitude = models.FloatField(null=True, blank = True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        if self.province:
            return "%s (%s) (%s)" % (self.name, self.province, self.country)
        else:
            return "%s (%s)" % (self.name, self.country)



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
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)  # models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['company_name']

    def __str__(self):
        return self.company_name

class Language(models.Model):

    id = models.AutoField(primary_key=True)
    LANGUAGES = language_utilities.LANGUAGES
    LANGUAGES_CHOICES = ((l, l) for l in LANGUAGES)

    LEVELS = ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']
    LEVELS_CHOICES = ((l, l) for l in LEVELS)
    name = models.CharField(
        max_length=15,
        choices=LANGUAGES_CHOICES,
        default='',
    )
    level = models.CharField(
        max_length=2,
        choices=LEVELS_CHOICES,
        default='',
    )

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ['name', 'level']

    def __str__(self):
        return f'{self.name} - {self.level}'


class Job(models.Model):

    STATE_CREATED = 'Nueva'
    STATE_WITHOUT_CHANGES = ''
    STATE_UPDATED = 'Actualizada'
    STATE_CLOSED = 'Inscripción cerrada'
    STATE_CHOICES = (
        (STATE_CREATED, 'Nueva'),
        (STATE_UPDATED, 'Actualizada'),
        (STATE_WITHOUT_CHANGES, 'Sin cambios'),
        (STATE_CLOSED, 'Inscripción cerrada')
    )

    TYPE_INTERNATIONAL = 'ofertas-internacionales'
    TYPE_NATIONAL = 'trabajo'
    TYPE_FIRST_JOB = 'primer-empleo'
    TYPE_CHOICES = (
        (TYPE_INTERNATIONAL, 'Empleo internacional'),
        (TYPE_NATIONAL, 'Empleo nacional'),
        (TYPE_FIRST_JOB, 'Primer empleo'),
    )

    CONTRACT_FIXED_DURATION = 'Contrato De duración determinada'
    CONTRACT_UNSPECIFIED = 'Contrato sin especificar'
    CONTRACT_PRACTICES = 'Contrato Prácticas'
    CONTRACT_UNDEFINED = 'Contrato Indefinido'
    CONTRACT_FREELANCE = 'Contrato Autónomo o freelance'
    CONTRACT_FIXED_DISCONTINUOUS = 'Contrato Fijo discontinuo'
    CONTRACT_FORMATIVE = "Contrato Formativo"
    CONTRACT_CHOICES = (
        (CONTRACT_UNSPECIFIED, 'sin especificar'),
        (CONTRACT_PRACTICES, 'prácticas'),
        (CONTRACT_UNDEFINED, 'indefinido'),
        (CONTRACT_FREELANCE, 'autónomo o freelance'),
        (CONTRACT_FIXED_DISCONTINUOUS, 'fijo discontinuo'),
        (CONTRACT_FORMATIVE, "formativo"),
        (CONTRACT_FIXED_DURATION, 'de duración determinada'),
    )

    WORKING_DAY_TELE = "Jornada Tele Trabajo"
    WORKING_DAY_UNSPECIFIED = "Jornada sin especificar"
    WORKING_DAY_INTENSIVE = "Jornada Intensiva"
    WORKING_DAY_INDIFFERENT = "Jornada Indiferente"
    WORKING_DAY_PARTIAL = "Jornada Parcial"
    WORKING_DAY_WEEKEND = "Jornada Fin de Semana"
    WORKING_DAY_COMPLETE = "Jornada Completa"
    WORKING_DAY_CHOICES = (
        (WORKING_DAY_UNSPECIFIED, "sin especificar"),
        (WORKING_DAY_INTENSIVE, "intensiva"),
        (WORKING_DAY_INDIFFERENT, "indiferente"),
        (WORKING_DAY_PARTIAL, "parcial"),
        (WORKING_DAY_WEEKEND, "fin de semana"),
        (WORKING_DAY_COMPLETE, "completa"),
        (WORKING_DAY_TELE, "tele trabajo"),
    )

    CATEGORY_KNOBS = "Mandos"
    CATEGORY_EMPLOYEES = "Empleados"
    CATEGORY_TECHNICIANS = "Técnicos"
    CATEGORY_DIRECTION = "Dirección"
    CATEGORY_UNSPECIFIED = "Sin especificar"

    CATEGORY_CHOICES = (
        (CATEGORY_KNOBS, "Mandos"),
        (CATEGORY_EMPLOYEES, "Empleados"),
        (CATEGORY_TECHNICIANS, "Técnicos"),
        (CATEGORY_DIRECTION, "Dirección"),
        (CATEGORY_UNSPECIFIED, "Sin especificar"),
    )

    AREA_EDUCATION_TRAINING = "Educación, formación"
    AREA_TECHNOLOGY_AND_INFORMATICS = "Tecnología e informática"
    AREA_HEALTH_HEALTH_AND_SOCIAL_SERVICES = "Sanidad, salud y servicios sociales"
    AREA_MEDIA_PUBLISHING_AND_GRAPHIC_ARTS = "Medios, editorial y artes gráficas"
    AREA_SHOPPING_LOGISTICS_AND_TRANSPORTATION = "Compras, logística y transporte"
    AREA_ADMINISTRATIVE_AND_SECRETARIAT = "Administrativos y secretariado"
    AREA_PROFESSIONALS_ARTS_AND_CRAFTS = "Profesionales, artes y oficios"
    AREA_TELECOMMUNICATIONS = "Telecomunicaciones"
    AREA_LEGAL = "Legal"
    AREA_INTERNET = "Internet"
    AREA_BANKING_AND_INSURANCE = "Banca y seguros"
    AREA_QUALITY_ID_PRL_AND_ENVIRONMENT = "Calidad, I+D, PRL y medio ambiente"
    AREA_HUMAN_RESOURCES = "Recursos humanos"
    AREA_SALES_MANAGER = "Comercial, ventas"
    AREA_ENGINEERING_AND_PRODUCTION = "Ingeniería y producción"
    AREA_CUSTOMER_SUPPORT = "Atención al cliente"
    AREA_CONSTRUCTION_AND_REAL_ESTATE = "Construcción e inmobiliaria"
    AREA_HOSTELRY_TOURISM = "Hostelería, Turismo"
    AREA_BUSINESS_ADMINISTRATION = "Administración de Empresas"
    AREA_MARKETING_AND_COMMUNICATION = "Marketing y comunicación"
    AREA_CHOICES = (
        (AREA_EDUCATION_TRAINING, "Educación, formación"),
        (AREA_TECHNOLOGY_AND_INFORMATICS, "Tecnología e informática"),
        (AREA_HEALTH_HEALTH_AND_SOCIAL_SERVICES, "Sanidad, salud y servicios sociales"),
        (AREA_MEDIA_PUBLISHING_AND_GRAPHIC_ARTS, "Medios, editorial y artes gráficas"),
        (AREA_SHOPPING_LOGISTICS_AND_TRANSPORTATION, "Compras, logística y transporte"),
        (AREA_ADMINISTRATIVE_AND_SECRETARIAT, "Administrativos y secretariado"),
        (AREA_PROFESSIONALS_ARTS_AND_CRAFTS, "Profesionales, artes y oficios"),
        (AREA_TELECOMMUNICATIONS, "Telecomunicaciones"),
        (AREA_LEGAL, "Legal"),
        (AREA_INTERNET, "Internet"),
        (AREA_BANKING_AND_INSURANCE,"Banca y seguros"),
        (AREA_QUALITY_ID_PRL_AND_ENVIRONMENT, "Calidad, I+D, PRL y medio ambiente"),
        (AREA_HUMAN_RESOURCES, "Recursos humanos"),
        (AREA_SALES_MANAGER, "Comercial, ventas"),
        (AREA_ENGINEERING_AND_PRODUCTION, "Ingeniería y producción"),
        (AREA_CUSTOMER_SUPPORT, "Atención al cliente"),
        (AREA_CONSTRUCTION_AND_REAL_ESTATE, "Construcción e inmobiliaria"),
        (AREA_HOSTELRY_TOURISM, "Hostelería, Turismo"),
        (AREA_BUSINESS_ADMINISTRATION, "Administración de Empresas"),
        (AREA_MARKETING_AND_COMMUNICATION, "Marketing y comunicación"),
    )
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    link = models.URLField(null=True)

    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='',
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=23,
        choices=TYPE_CHOICES,
        default=TYPE_NATIONAL,
    )
    summary = ListCharField(base_field=models.CharField(max_length=100),
        size=6,
        max_length=(6 * 101), null=True)
    _experience = models.CharField(max_length=40, null=True, blank=True)
    _salary = models.CharField(max_length=40, null=True, blank=True)
    _contract = models.CharField(max_length=30, null=True, blank=True)
    _working_day = models.CharField(max_length=30, null=True, blank=True)
    minimum_years_of_experience = models.PositiveIntegerField(null=True, blank=True, default=0)
    recommendable_years_of_experience = models.PositiveIntegerField(null=True, blank=True, default=0)
    minimum_salary = models.PositiveIntegerField(null=True, blank=True)
    maximum_salary = models.PositiveIntegerField(null=True, blank=True)
    #working_day = models.CharField(max_length=30, null=True, blank=True)
    working_day = models.CharField(
        max_length=23,
        choices=WORKING_DAY_CHOICES,
    )
    #contract = models.CharField(max_length=30, null=True, blank=True)
    contract = models.CharField(
        max_length=32,
        choices=CONTRACT_CHOICES,
    )
    cityname = ListCharField(base_field=models.CharField(max_length=100),
        size=6,
        max_length=(6 * 101), null=True)
    cities = models.ManyToManyField(City,
                            related_name='jobs',
                            null = True, blank = True)
    languages = models.ManyToManyField(Language,
                            related_name='jobs',
                            null = True, blank = True)
    provincename = models.CharField(null=True, max_length=100, blank=True)  # Model
    countryname = models.CharField(null=True, max_length=30) #Model
    nationality = models.CharField(max_length=30)
    first_publication_date = models.DateField(null=True, blank=True, default=None)
    last_update_date = models.DateField(null=True, blank=True, default=None)
    expiration_date = models.DateField(null=True, blank=True)  # models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    functions = models.TextField(null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    it_is_offered = models.TextField(null=True, blank=True) #NULL constraint
    tags = models.TextField(null=True, blank=True) #Model
    #area = models.CharField(null=True,max_length=100, blank=True) #Model
    area = models.CharField(
        max_length=34,
        choices=AREA_CHOICES,
    )
    #category_level = models.CharField(null=True,max_length=100, blank=True)
    category_level = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
    )
    vacancies = models.PositiveIntegerField()
    registered_people = models.PositiveIntegerField(default=0)
    vacancies_update = models.PositiveIntegerField(null=True, blank=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='job', null=True)
   
    

    created_at = models.DateTimeField(auto_now_add=True, null=True)  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  # models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    #objects = JobQuerySet.as_manager()
    objects = JobManager()
    #first_publication_date = models.DateField(null=True, blank=True, default=None)
    #fake = models.CharField(max_length=30, null=True, blank=True, default='fake')

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ['-created_at', 'name']  # El - delante del nombre del atributo indica que se o
        #unique_together = (('id'),)


    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('detail', args=[str(self.pk)])


    def __str__(self):
        return "%s - %s (%s)" % (self.name, self.type, self.cities)

    def company_link_(self):
        return self.company.company_link

    def fields(self):
        return [field['name'] for field in self._meta.fields]

    @classmethod
    def add_city(cls, job, city):
        job_, is_new = cls.objects.get_or_create(id=job.id)
        job_.cities.add(city)




def _create_languages():
    for l in Language.LANGUAGES:
        for l_ in Language.LEVELS:
            Language.objects.get_or_create(name=l, level=l_)

