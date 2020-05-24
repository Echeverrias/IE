from django.db.utils import InterfaceError
from django import db
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_mysql.models import ListCharField
from utilities import languages_utilities
from simple_history.models import HistoricalRecords
from .managers import JobManager, CompanyManager

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name="nombre")
    slug = models.CharField(max_length=30)

    class Meta:
        verbose_name = "País" #"Country"
        verbose_name_plural = "Países" #"Countries"
        ordering = ['name']

    def save(self, *args, **kwargs):
        try:
            self.slug = slugify(self.name)
        except:
            pass
        super(Country, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.name)


class Community(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30, verbose_name="nombre")
    capital_id = models.IntegerField(null=True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='communities',
                                null=True, blank=True,
                                verbose_name="país")

    class Meta:
        verbose_name = "Comunidad" #"Community"
        verbose_name_plural = "Comunidades" #"Communities"
        ordering = ['name']

    def save(self, *args, **kwargs):
        try:
            self.slug = slugify(self.name)
        except:
            pass
        super(Community, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.name)


class Province(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='provinces',
                                null=True, blank=True,
                                verbose_name="país")
    community = models.ForeignKey(Community,
                                on_delete=models.CASCADE,
                                related_name='provinces',
                                null=True, verbose_name="comunidad autónoma")
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30, verbose_name="nombre")
    community_number = models.IntegerField(null=True, blank=True)
    capital_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = "Provincia" #"Province"
        verbose_name_plural = "Provincias"  # "Provinces"
        ordering = ['name']

    def save(self, *args, **kwargs):
        try:
            self.slug = slugify(self.name)
        except:
            pass
        super(Province, self).save(*args, **kwargs)


    def __str__(self):
        return "%s" % (self.name)



class City (models.Model):
    id = models.AutoField(primary_key=True)
    province = models.ForeignKey(Province,
                                 on_delete=models.CASCADE,
                                 related_name='cities',
                                 null = True, blank = True,
                                 verbose_name="provincia")
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='cities',
                                null = True, blank = True,
                                verbose_name="país")
    name = models.CharField(max_length=100, verbose_name="nombre")
    slug = models.CharField(max_length=100, null=True, blank = True)
    latitude = models.FloatField(null=True, blank = True, verbose_name="latitud")
    longitude = models.FloatField(null=True, blank = True, verbose_name="longitud")

    class Meta:
        verbose_name = "Ciudad" #"City"
        verbose_name_plural = "Ciudades" #"Cities"
        ordering = ['name']

    def save(self, *args, **kwargs):
        print('save')
        try:
            self.slug = slugify(self.name)
        except:
            pass
        super(City, self).save(*args, **kwargs)


    def __str__(self):
        if self.province:
            return "%s (%s) (%s)" % (self.name, self.province, self.country)
        else:
            return "%s (%s)" % (self.name, self.country)



class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, blank=True, max_length=300, verbose_name="nombre")
    link = models.URLField(null=True)
    reference = models.IntegerField(null=True, blank=True, verbose_name="nº de referencia")
    is_registered = models.BooleanField(null=True, blank=True, verbose_name="empresa colaboradora")
    description = models.TextField(null=True, verbose_name="descripción")
    resume = models.CharField(max_length=300, null=True, blank=True, verbose_name="resumen")
    location_name = models.CharField(max_length=50, null=True)
    city = models.ForeignKey(City,
                            on_delete=models.CASCADE,
                            related_name='companies',
                            null = True, blank = True, verbose_name="ciudad")
    country = models.ForeignKey(Country,
                             on_delete=models.CASCADE,
                             related_name='companies',
                             null=True, blank=True, verbose_name="país")
    area = ListCharField(base_field=models.CharField(max_length=45),
                             size=34,
                             max_length=(1570), null=True, blank=True, verbose_name="área")
    category = models.CharField(null=True, blank=True, max_length=100, verbose_name="categoría")
    offers = models.IntegerField(null=True, blank=True,  verbose_name="nº de ofertas")
    slug = models.CharField(max_length=300, null=True, blank = True)
    created_at = models.DateTimeField(editable=False, null=True, verbose_name="fecha de creción del registro")  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, null=True, verbose_name="fecha de actualización del registro")  # models.DateTimeField(auto_now=True)
    checked_at = models.DateTimeField(editable=False, null=True, blank=True, verbose_name="fecha de comprobación del registro")  # models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    objects = CompanyManager()

    class Meta:
        verbose_name = "Compañía" #"Company"
        verbose_name_plural = "Compañías" #"Companies"
        ordering = ['name']

    def save(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())
        if not self.created_at:
            self.created_at = now
        else:
            self.updated_at = now if now.date() > self.created_at.date() else None
        self.checked_at = now
        try:
            if self.name:
                self.slug = slugify(self.name)
            else:
                self.slug = self._get_slug_from_link()
        except:
            pass
        super(Company, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = str(self.id)
            super(Company, self).save(*args, **kwargs)

    def __str__(self):
        return self.name or ''

    def _get_slug_from_link(self):
        link = self.link
        try:
            link = link[:-1] if self.link.endswith('/') else link
            slug = link.split('/')[-2]
        except Exception as e:
            slug = ''
        return slug


class Language(models.Model):

    id = models.AutoField(primary_key=True)
    LANGUAGES = languages_utilities.LANGUAGES
    LANGUAGES_CHOICES = ((l, l) for l in LANGUAGES)

    LEVELS = ['C2', 'C1', 'B2', 'B1', 'A2', 'A1']
    LEVELS_CHOICES = ((l, l) for l in LEVELS)
    name = models.CharField(
        max_length=15,
        choices=LANGUAGES_CHOICES,
        default='',
        verbose_name = "nombre",
    )
    level = models.CharField(
        max_length=2,
        choices=LEVELS_CHOICES,
        default='',
        verbose_name = "nivel"
    )

    class Meta:
        verbose_name = "Idioma" #"Language"
        verbose_name_plural = "Idiomas" #"Languages"
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
        (STATE_WITHOUT_CHANGES, 'Sin cambios'),
        (STATE_UPDATED, 'Actualizada'),
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
        (WORKING_DAY_INDIFFERENT, "flexible"),
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

    # 20 areas
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
    name = models.CharField(max_length=200, verbose_name="nombre")
    link = models.URLField(null=True)

    state = models.CharField(
        max_length=30,
        choices=STATE_CHOICES,
        null=True,
        blank=True,
        verbose_name = "estado"
    )

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_NATIONAL,
        verbose_name = "tipo",
    )
    _summary = ListCharField(base_field=models.CharField(max_length=100),
        size=6,
        max_length=(6 * 101), null=True)
    _experience = models.CharField(max_length=40, null=True, blank=True)
    _salary = models.CharField(max_length=40, null=True, blank=True)
    _contract = models.CharField(max_length=40, null=True, blank=True)
    _working_day = models.CharField(max_length=40, null=True, blank=True)
    minimum_years_of_experience = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name="experiencia mínima")
    recommendable_years_of_experience = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name="experiencia recomendable")
    minimum_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name="salario míminimo")
    maximum_salary = models.PositiveIntegerField(null=True, blank=True, verbose_name="salario máximo")
    working_day = models.CharField(
        max_length=30,
        choices=WORKING_DAY_CHOICES,
        default=CATEGORY_UNSPECIFIED,
        verbose_name="jornada laboral",
    )
    contract = models.CharField(
        max_length=40,
        choices=CONTRACT_CHOICES,
        default=CONTRACT_UNSPECIFIED,
        verbose_name = "tipo de contrato",
    )

    cities = models.ManyToManyField(City,
                            related_name='jobs',
                            null = True, blank = True,
                            verbose_name="ciudades",)
    province = models.ForeignKey(Province,
                                 on_delete=models.CASCADE,
                                 related_name='jobs',
                                 null=True, blank=True,
                                 verbose_name="provincia",)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='jobs',
                                null=True, blank=True,
                                verbose_name="país",)
    languages = models.ManyToManyField(Language,
                            related_name='jobs',
                            null = True, blank = True,
                            verbose_name="idiomas",)
    _cities = ListCharField(base_field=models.CharField(max_length=100),
                             size=6,
                             max_length=(6 * 101), null=True, blank=True)
    _province = models.CharField(null=True, max_length=100, blank=True)  # Model
    _country = models.CharField(null=True, max_length=30) #Model
    nationality = models.CharField(max_length=30, verbose_name="nacionalidad")
    first_publication_date = models.DateField(null=True, blank=True, default=None, verbose_name="fecha de publicación de la oferta")
    last_update_date = models.DateField(null=True, blank=True, default=None, verbose_name="fecha de actualización de la oferta")
    expiration_date = models.DateField(null=True, blank=True, default=None, verbose_name="fecha de caducidad de la oferta")  # models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True, verbose_name="descripción")
    functions = models.TextField(null=True, blank=True, verbose_name="funciones")
    requirements = models.TextField(null=True, blank=True, verbose_name="requisitos")
    it_is_offered = models.TextField(null=True, blank=True,verbose_name="se ofrece") #NULL constraint
    tags = models.TextField(null=True, blank=True,verbose_name="etiquetas") #Model
    area = models.CharField(
        max_length=40,
        choices=AREA_CHOICES,
        verbose_name = "área"
    )
    category_level = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_UNSPECIFIED,
        null=True,
        verbose_name="categoría o nivel",
    )
    vacancies = models.PositiveIntegerField(null=True, blank=True, verbose_name="nº de vacantes")
    registered_people = models.PositiveIntegerField(default=0, verbose_name="inscritos")
    vacancies_update = models.PositiveIntegerField(null=True, blank=True)
    company = models.ForeignKey(
        Company,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name='jobs', verbose_name="compañía")
    created_at = models.DateTimeField(editable=False, null=True, verbose_name="fecha de creación del registro")  # models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True, verbose_name="fecha de actualización del registro")  # models.DateTimeField(auto_now=True)
    checked_at = models.DateTimeField(editable=False, null=True, blank=True, verbose_name="fecha de comprobación del registro")  # models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    objects = JobManager()

    class Meta:
        verbose_name = "Oferta de empleo"
        verbose_name_plural = "Ofertas de empleo"
        ordering = ['-created_at', 'name']
        #unique_together = (('id'),)

    def __str__(self):
        city = ""
        try:
            city = " - %s" % ( self.cities.all().first())
        except:
            pass
        return "%s - %s%s" % (self.name, self.type, city)

    def save(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())
        if not self.created_at:
            self.created_at = now
        else:
            self.updated_at = now if now.date() > self.created_at.date() else None
        self.checked_at = now
        try:
            super(Job, self).save(*args, **kwargs)
        except InterfaceError as ie:
            db.connection.close()
            super(Job, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('job_detail', args=[str(self.pk)])

    def company_link_(self):
        return self.company.link

    def fields(self):
        return [field['name'] for field in self._meta.fields]

    def display_cities(self):
        """
        For display the cities and the country of an offer in the admin section
        :return: The cities and the country
        """
        cities = self.cities.all()[0:3]
        if cities:
            names = [city.name for city in cities]
            return f'{", ".join(names)} ({cities[0].country.name})'
        else:
            return None

    display_cities.short_description = 'Cities (Country)'


    @staticmethod
    def add_city(job, city):
        try:
            job_ = Job.objects.get(id=job.id)
            job_.cities.add(city)
        except Exception as e:
            print(f'Error in Job.add_city: {e}')






