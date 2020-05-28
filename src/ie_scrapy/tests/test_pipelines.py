from django.test import TestCase
from ie_scrapy.pipelines import CleaningPipeline, StoragePipeline
from ie_scrapy.items import JobItem, CompanyItem
from job.models import Job, Company, Country, Province, City, Language
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import time

class TestCleaningPipeline(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cp = CleaningPipeline()

    def test_clean_job_date(self):
        today = timezone.localtime(timezone.now()).date()
        self.assertEqual(self.cp._clean_job_date("Hace 25 meses"), today - relativedelta(months=25))
        self.assertEqual(self.cp._clean_job_date('Hace 3 dias'), today - relativedelta(days=3))
        self.assertEqual(self.cp._clean_job_date('Hace 3 días'), today - relativedelta(days=3))
        self.assertEqual(self.cp._clean_job_date('Hace 36 horas'), today - relativedelta(days=int(36/24)))
        self.assertEqual(self.cp._clean_job_date('Hace 1 hora'), today - relativedelta(days=int(1/24)))
        self.assertEqual(self.cp._clean_job_date('Hace 2 años'), today - relativedelta(years=2))
        

    def test_clean_url(self):
        self.assertEqual(self.cp._clean_url('/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'), 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')
        self.assertEqual(self.cp._clean_url('https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'), 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')
        self.assertEqual(self.cp._clean_url('https://www.infoempleo.com'), '')
        self.assertEqual(self.cp._clean_url('https://www.repsol.es/es/index.cshtml'), 'https://www.repsol.es/es/index.cshtml')
        
    def test_clean_country(self):
        self.assertEqual(self.cp._clean_country('Empleo en Alemania'), 'Alemania')
        self.assertEqual(self.cp._clean_country('Empleo en otros Países Italia'), 'Italia')
        self.assertEqual(self.cp._clean_country('Álcala del Valle (España)'), 'España')
        self.assertEqual(self.cp._clean_country('Francia'), '') # A country can´t be alone

    def test_clean_province(self):
        self.assertEqual(self.cp._clean_province('Madrid'), 'Madrid')
        self.assertEqual(self.cp._clean_province('Bercial (el)'), 'Bercial (el)')
        self.assertEqual(self.cp._clean_province('Álcala del Valle (Cádiz)'), 'Cádiz')
        self.assertEqual(self.cp._clean_province('Móstoles, Alcorcón, Bercial (el) (Madrid)'), 'Madrid')
        
    def test_clean_location(self):
        self.assertEqual(self.cp._clean_location('Alcalá del Valle (Cádiz)'), 'Alcalá del Valle')
        self.assertEqual(self.cp._clean_location('Bercial (el) (Madrid)'), 'El Bercial')
        self.assertEqual(self.cp._clean_location('etc (Madrid)'), '')
        self.assertEqual(self.cp._clean_location('alrededores de Madrid'), 'Madrid')
        self.assertEqual(self.cp._clean_location('Belfast'), 'Belfast')
        self.assertEqual(self.cp._clean_location('Oxford alrededores (Gran Bretaña)'), 'Oxford')
        self.assertEqual(self.cp._clean_location('Donostia-San Sebastián (Guipúzcoa)'), 'Donostia-San Sebastián')
        self.assertEqual(self.cp._clean_location('.'), '')
        self.assertEqual(self.cp._clean_location('-'), '')
        self.assertEqual(self.cp._clean_location('*'), '')

    def test_clean_cities(self):
        self.assertEqual(self.cp._clean_cities('Álcala del Valle (Cádiz)'), ['Álcala del Valle'])
        self.assertEqual(self.cp._clean_cities('Móstoles, Alcorcón, Bercial (el) (Madrid)'),
                         ['Móstoles', 'Alcorcón', 'El Bercial'])
        self.assertEqual(self.cp._clean_cities('Móstoles, Alcorcón, Bercial (el), etc (Madrid)'),
                         ['Móstoles', 'Alcorcón', 'El Bercial'])
        self.assertEqual(self.cp._clean_cities(
            'Móstoles, Alcorcón, Bercial (el), alrededores de Madrid, etc (Madrid)'),
                         ['Móstoles', 'Alcorcón', 'El Bercial', 'Madrid'])
        self.assertEqual(self.cp._clean_cities('Belfast y alrededores'), ['Belfast'])
        self.assertEqual(self.cp._clean_cities('Oxford alrededores (Gran Bretaña)'), ['Oxford'])
        self.assertEqual(self.cp._clean_cities('Donostia-San Sebastián (Guipúzcoa)'),
                         ['Donostia-San Sebastián'])
        self.assertEqual(self.cp._clean_cities('.'), [])

    def test_clean_salary(self):
        text="Se    ofrece    -   ...\
         -    3000 Sueldo anual neto entre 43.500€ o 45.000€;    -    Alojamiento..."
        self.assertEqual( self.cp._clean_salary(text, True), (43500, 45000))
        text="Se    ofrece    -   ...\
         -    Sueldo anual neto entre 43550€ a  45600€;    -    Alojamiento..."
        self.assertEqual( self.cp._clean_salary(text, True), (43550, 45600))
        text = "el sueldo  de 3.000 puede ser inicialmente de 3.300€ netos/mes o 3.430€ netos/mes dependiendo de la especialidad"
        self.assertEqual( self.cp._clean_salary(text, True), (3300, 3430))
        text = "3000 3.300€ netos/mes o 3.430"
        self.assertEqual( self.cp._clean_salary(text, True), (3300, 3430))
        text = "3000 3.300€ netos/mes  3.430 5000"
        self.assertEqual( self.cp._clean_salary(text, True), (3300, 3430))
        text = "3.300€ netos/mes "
        self.assertEqual( self.cp._clean_salary(text, True), (3300, 3300))
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual( self.cp._clean_salary(text, True), (2270, 2270))
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual(self.cp._clean_salary(text, True), (2270, 2270))
        text = "Entre 1000 y 20000€ brutos/anuales "
        self.assertEqual(self.cp._clean_salary(text, False), (1000, 20000))
        
    def test_get_annual_salary(self):
        text = "Se    ofrece    -   ...\n -  Sueldo anual neto entre 43.500€ a 45.000€;  -    Alojamiento..."
        self.assertEqual(self.cp._get_annual_salary(text), [43500, 45000])
        text = "Salario Medio Mensual Neto entre 5.000€ a 10.000€ (en función del tipo de tratamientos efectuados"
        self.assertEqual(self.cp._get_annual_salary(text), [60000, 120000])
        text = "actualización salarial, en media actualmente, además del valor inicial base neto de 3.300€. \
                Ganará un Salario Mensual Neto (exento de impuestos en Arabia Saudí) base de 3.300€ como punto de referencia. \
                La propuesta final viene dada según su experiencia profesional y grado de especialización. \
                Así el sueldo será aún más competitivo en función de su experiencia profesional (que es valorizada)  \
                y el nivel de especialización (se valoriza enfermeros especialistas).\
                El sueldo inicial es de 3.300€ netos/mes o 3.430€ netos/mes dependiendo de la especialidad \
                +15 días de Bonos + adicionales USD de 2.500. Anualmente el sueldo líquido varía entre 43.500€ a 45.000€. Con su"
        self.assertEqual(self.cp._get_annual_salary(text), [39600, 41160])
        text = "Salario: 15.500 € b/a"
        self.assertEqual(self.cp._get_annual_salary(text), [15500, 15500])
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual(self.cp._get_annual_salary(text), [27240, 27240])
        text = "empresa con un salario de 17.000 euros brutos al año o 18.000 euros brutos al año, además, cada mes, te podrás llevar entre 1500€ y 1700€. Tu horario"
        self.assertEqual(self.cp._get_annual_salary(text), [17000, 18000])
        text = "empresa con un salario de 17.000 euros brutos al año, 1500€ a 1700€ b/m. Tu horario"
        self.assertEqual(self.cp._get_annual_salary(text), [17000, 17000])
        text = "salario mensual de 2500 euros y al año de 30000"
        self.assertEqual(self.cp._get_annual_salary(text), [30000, 30000])
        text = "salario de 2500 euros o de 30000" # Doesn't include unit time
        self.assertEqual(self.cp._get_annual_salary(text), [None, None])
        text = " +15 días de Bonos + adicionales USD de 2.500. Anualmente el sueldo líquido varía entre 43.500€ a 45.000€. Con su"
        self.assertEqual(self.cp._get_annual_salary(text), [43500, 45000])
        text = 'Si cumples el perfil y quieres  progresar incorporándote a \
                un Grupo en expansión con verdaderas posibilidades de \
                promocionar profesionalmente ¡Esta es tu oportunidad!'
        self.assertEqual(self.cp._get_annual_salary(text), [None, None])
        text = 'Hays colaboramos con un Despacho de Abogados y Asesores de \n\
              referencia a nivel nacional en el asesoramiento integral para \n\
              autónomos, pymes y grandes empresas.  Precisa incorporar en la \n\
              Oficina de Vitoria un/a Responsable del Área Económica - Asesor \n\
              Fiscal que se encargará de gestionar el equipo de 10 - 12 \n\
              personas que integran las áreas mercantil, fiscal y contable \n\
              así como de asesorar en materia fiscal a autónomos, empresas y \n\
              grupos de empresas.'
        self.assertEqual(self.cp._get_annual_salary(text), [None, None])
        text = 'Contrato temporal a través de ETT.\nJornada completa de lunes a viernes (los viernes jornada intensiva de mañana).\n18.361 Euros brutos anuales.'
        self.assertEqual(self.cp._get_annual_salary(text), [18361, 18361])
        text = "'La compañía ofrece:\r\n * Contratación indefinida\r\n * Incorporación inmediata\r\n * Salario fijo + salario variable mensual\r\n * Unirse a una compañía referencia en el sector'"
        self.assertEqual(self.cp._get_annual_salary(text), [None, None])
        text = "'La compañía ofrece:\r\n * Contratación indefinida\r\n * Incorporación inmediata\r\n * b/m + salario variable mensual\r\n * Unirse a una compañía referencia en el sector'"
        self.assertEqual(self.cp._get_annual_salary(text), [None, None])


    def test_get_it_is_offered(self):
        self.assertEqual( self.cp._get_it_is_offered("... ..."), "")
        self.assertEqual( self.cp._get_it_is_offered("...te ofrece ..."), "")
        self.assertEqual( self.cp._get_it_is_offered("...Te ofrecemos un contrato ..."), "un contrato ...")
        self.assertEqual( self.cp._get_it_is_offered("...Se ofrece: un contrato ..."), "un contrato ...")

    def test_set_job_dates_from_state(self):
        today = timezone.localtime(timezone.now()).date()
        today_ = "Hace 5 horas"
        yesterday = today - relativedelta(days=1)
        yesterday_ = "Hace 1 día"
        item = {'state': Job.STATE_UPDATED, 'first_publication_date': today_, 'last_update_date': today_}
        self.assertEqual(self.cp._set_job_dates_from_state(item),
                         {'state': Job.STATE_UPDATED, 'first_publication_date': None, 'last_update_date': today})
        item = {'state': Job.STATE_CREATED, 'first_publication_date': today_, 'last_update_date': today_}
        self.assertEqual(self.cp._set_job_dates_from_state(item),
                         {'state': Job.STATE_CREATED, 'first_publication_date': today, 'last_update_date': None})
        item = {'state': Job.STATE_WITHOUT_CHANGES, 'first_publication_date': yesterday_, 'last_update_date': yesterday_}
        self.assertEqual(self.cp._set_job_dates_from_state(item),
                         {'state': Job.STATE_WITHOUT_CHANGES, 'first_publication_date': yesterday, 'last_update_date': None})
        item = {'state': Job.STATE_CLOSED, 'first_publication_date': '', 'last_update_date': ''}
        self.assertEqual(self.cp._set_job_dates_from_state(item),
                         {'state': Job.STATE_CLOSED, 'first_publication_date': None, 'last_update_date': None})

    def test_clean_company(self):
        company_dict = {'_location': 'Madrid',
                        'category': '   Recursos Humanos  ',
                        'description': '\r\n               ',
                        'link': '/colaboradoras/hays/presentacion/',
                        'name': '\r\n    Hays Recruiting Experts Worldwide',
                        'offers': '\r\n Ver todas sus ofertas (397)',
                        'resume': '\r\n'}

        clean_company_dict = {'_location': 'Madrid',
                              'category': 'Recursos Humanos',
                              'description': '',
                              'link': 'https://www.infoempleo.com/colaboradoras/hays/presentacion/',
                              'name': 'Hays Recruiting Experts Worldwide',
                              'offers': 397,
                              'resume': '',
                              }

        ci = CompanyItem(company_dict)
        clean_ci = self.cp.process_item(ci, None)
        self.assertEqual(clean_ci.get_dict(), clean_company_dict)

    def test_clean_job(self):

        job_dict = {'_cities': 'Donostia-San Sebastián (Guipúzcoa)',
             '_country': 'Empleo en Donostia-San Sebastián (Guipúzcoa)',
             '_province': 'Donostia-San Sebastián (Guipúzcoa)',
             '_summary': '\r\n'
                         '                    Jornada Completa - Contrato Indefinido - '
                         'Retribución sin especificar - Al menos 5 años de experiencia\r\n'
                         '                ',
             'area': 'Legal',
             'category_level': 'Técnicos',
             'company': None,
             'description': 'Proceso de selección continuo',
             'expiration_date': 'Proceso de selección continuo',
             'first_publication_date': 'Hace 31 horas ',
             'functions': 'Desde Hays buscamos un/a Asesor/a Técnico Laboral para formar '
                          'parte de la División de Asesoría de un Grupo líder de servicios '
                          'empresariales en el País Vasco en proceso de expansión, '
                          'dedicado al Asesoramiento, Consultoría y Auditoría, en el '
                          'centro de trabajo ubicado en San Sebastián (Gipuzkoa).\r\n'
                          '\r\n'
                          'En dependencia del Gerente del Despacho, desarrollarás tareas '
                          'de asesoramiento laboral para cartera de clientes de empresas '
                          'de la provincia (elaboración de nóminas, seguros sociales, '
                          'altas, bajas, cálculo de indemnizaciones, etc.)',
             'id': 'Ref: 2622727',
             'it_is_offered': 'Si cumples el perfil y quieres  progresar incorporándote a '
                              'un Grupo en expansión con verdaderas posibilidades de '
                              'promocionar profesionalmente ¡Esta es tu oportunidad!',
             'last_update_date': 'Hace 31 horas ',
             'link': 'https://www.infoempleo.com/ofertasdetrabajo/asesora-tecnico-laboral-grupo-asesor/donostia-san-sebastian/2622727/',
             'name': '\r\nAsesor/a Técnico Laboral. Grupo Asesor                    ',
             'nationality': 'Trabajo',
             'registered_people': '15',
             'requirements': 'Pensamos en una persona con al menos cinco años de '
                             'experiencia en servicios de asesoramiento laboral a empresas '
                             'y autónomos, que venga desarrollando en la actualidad estas '
                             'funciones en Asesoría (imprescindible), buen comunicador y '
                             'con vocación de Asesoramiento al Cliente.',
             'state': '(Actualizada)',
             'tags': '',
             'type': 'https://www.infoempleo.com/trabajo/area-de-empresa_legal/',
             'vacancies': '1'}

        clean_job_dict = {'_cities': ['Donostia-San Sebastián'],
             '_contract': 'Contrato Indefinido',
             '_country': 'España',
             '_experience': 'Al menos 5 años de experiencia',
             '_province': 'Guipúzcoa',
             '_salary': 'Retribución sin especificar',
             '_summary': ['Jornada Completa',
                          'Contrato Indefinido',
                          'Retribución sin especificar',
                          'Al menos 5 años de experiencia'],
             '_working_day': 'Jornada Completa',
             'area': 'Legal',
             'category_level': 'Técnicos',
             'company': None,
             'contract': 'Contrato Indefinido',
             'description': 'Proceso de selección continuo',
             'expiration_date': None,
             'first_publication_date': None,
             'functions': 'Desde Hays buscamos un/a Asesor/a Técnico Laboral para formar '
                          'parte de la División de Asesoría de un Grupo líder de servicios '
                          'empresariales en el País Vasco en proceso de expansión, '
                          'dedicado al Asesoramiento, Consultoría y Auditoría, en el '
                          'centro de trabajo ubicado en San Sebastián (Gipuzkoa).  En '
                          'dependencia del Gerente del Despacho, desarrollarás tareas de '
                          'asesoramiento laboral para cartera de clientes de empresas de '
                          'la provincia (elaboración de nóminas, seguros sociales, altas, '
                          'bajas, cálculo de indemnizaciones, etc.)',
             'id': 2622727,
             'it_is_offered': 'Si cumples el perfil y quieres  progresar incorporándote a '
                              'un Grupo en expansión con verdaderas posibilidades de '
                              'promocionar profesionalmente ¡Esta es tu oportunidad!',
             'last_update_date': self.cp._clean_job_date('Hace 31 horas '),
             'link': 'https://www.infoempleo.com/ofertasdetrabajo/asesora-tecnico-laboral-grupo-asesor/donostia-san-sebastian/2622727/',
             'maximum_salary': None,
             'minimum_salary': None,
             'minimum_years_of_experience': 5,
             'name': 'Asesor/a Técnico Laboral. Grupo Asesor',
             'nationality': 'nacional',
             'recommendable_years_of_experience': 5,
             'registered_people': 15,
             'requirements': 'Pensamos en una persona con al menos cinco años de '
                             'experiencia en servicios de asesoramiento laboral a empresas '
                             'y autónomos, que venga desarrollando en la actualidad estas '
                             'funciones en Asesoría (imprescindible), buen comunicador y '
                             'con vocación de Asesoramiento al Cliente.',
             'state': 'Actualizada',
             'tags': '',
             'type': 'trabajo',
             'vacancies': 1,
             'working_day': 'Jornada Completa'}
        ji = JobItem(job_dict)
        clean_ji = self.cp.process_item(ji, None)
        clean_ji_cities = [] + clean_ji['_cities']
        clean_job_dict_cities = [] + clean_job_dict['_cities']
        self.assertEqual(clean_ji_cities , clean_job_dict_cities )
        clean_ji['_cities'] =  clean_ji_cities
        clean_job_dict['_cities'] = clean_job_dict_cities
        self.assertEqual(clean_ji.get_dict().get('nacionality'), clean_job_dict.get('nacionality'))
        #time.sleep(2)
        self.assertEqual(clean_ji.get_dict().get('_country'), clean_job_dict.get('_country'))
        #time.sleep(2)
        self.assertEqual(clean_ji.get_dict().get('_province'), clean_job_dict.get('_province'))
        #self.assertEqual(clean_ji.get_dict(), clean_job_dict)

    def test_clean_company_name(self):
        d = {
            'name': "IMAN TEMPORING ETT, S.L.",
            'link': "https://www.infoempleo.com/ofertasempresa/iman-temporing-ett-s-l/7347/",
            'resume': "",
            'description': ""
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "IMAN TEMPORING ETT, S.L.")
        d = {
            'name': "Empresa importante",
            'link': "",
            'resume': "La empresa Iman S.L. es muy importante",
            'description': "..."
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "Iman S.L.")
        d = {
            'name': "Empresa importante",
            'link': "",
            'resume': "VODAFONE",
            'description': "..."
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "VODAFONE")
        d = {
            'name': "Empresa importante",
            'link': "",
            'resume': "Grupo Addeco",
            'description': "..."
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "Grupo Addeco")
        d = {
            'name': "Empresa importante",
            'link': "",
            'resume': "Empresa muy importante",
            'description': "La empresa lider Grupo Qwe Asd Zxc, Para Madrid, es una empresa muy importante"
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "Grupo Qwe Asd Zxc")
        d = {
            'name': "Empresa importante",
            'link': "",
            'resume': "Empresa muy importante",
            'description': "Para Cantabria, Empresa dedicada al sector..."
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_name(ci), "")

    def test_clean_company_category(self):
        # If the company has link it will be have category and the pipeline wouldn't call _clean_compnay_description
        d = {
            'name': "",
            'link': "",
            'resume': "Importante empresa nacional lider en la cosmética",
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "cosmética")
        d = {
            'name': "",
            'link': "",
            'resume': 'Importante empresa en cosmética.',
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "cosmética")
        d = {
            'name': "",
            'link': "",
            'resume': 'Importante empresa nacional dedicada al sector de la elevación.',
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "sector de la elevación")
        d = {
            'name': "",
            'link': "",
            'resume': 'Importante empresa dedicada y especializada en el montaje de equipaminetos.',
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "montaje de equipaminetos")
        d = {
            'name': "",
            'link': "",
            'resume': 'Empresa líder en el sector de las Colectividades.',
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "sector de las Colectividades")
        d = {
            'name': "",
            'link': "",
            'resume': 'Importante Consultora de Recursos Humanos.',
            'description': "",
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "Recursos Humanos")
        d = {
            'name': "",
            'link': "",
            'resume': '',
            'description': '...Lider en el mercado. Empresa líder en el sector de las Colectividades en Zona Madrid Importante Distribuidora',
            'category': "",
        }
        ci = CompanyItem(**d)
        self.assertEqual(self.cp._clean_company_category(ci), "Colectividades")


class TestStoragePipeline(TestCase):

    sp = StoragePipeline()

    @classmethod
    def setUpTestData(cls):
        cls.today = timezone.localtime(timezone.now()).date()
        cls.yesterday = cls.today - relativedelta(days=1)
        cls.before_yesterday = cls.today - relativedelta(days=2)
        Job.objects.create(id=111,
                           state=Job.STATE_UPDATED,
                           last_update_date=cls.yesterday)
        Job.objects.create(id=222,
                           state=Job.STATE_UPDATED,
                           first_publication_date=cls.before_yesterday,
                           last_update_date=cls.yesterday)
        Job.objects.create(id=333,
                           state=Job.STATE_UPDATED,
                           first_publication_date=cls.before_yesterday,
                           last_update_date=cls.today)
        # Jobs not updated yet:
        Job.objects.create(id=444,
                           state=Job.STATE_CREATED,
                           first_publication_date=cls.yesterday)
        Job.objects.create(id=555,
                           state=Job.STATE_WITHOUT_CHANGES,
                           first_publication_date=cls.before_yesterday)
        Job.objects.create(id=666,
                           state=Job.STATE_CLOSED,
                           first_publication_date=cls.before_yesterday)
        cls.default_fields = {
            'vacancies': 0,
            'registered_people': 0,
            'type': Job.TYPE_FIRST_JOB,
            'contract': Job.CONTRACT_FREELANCE,
            'working_day': Job.WORKING_DAY_COMPLETE,
            'minimum_years_of_experience': 1,
            'recommendable_years_of_experience': 3,
            'minimum_salary': 20000,
            'maximum_salary': 25000,
            'description':'description',
            'functions': 'functions',
            'requirements': 'requirements',
            'it_is_offered': 'it is offered',
            'area': Job.AREA_LEGAL,
            'category_level': Job.CATEGORY_EMPLOYEES,
            'expiration_date': None,
            'created_at': cls.before_yesterday,
        }
        cls.espana = Country.objects.create(name='España')
        cls.mexico = Country.objects.create(name='Mexico')
        cls.almeria = Province.objects.create(id=1, name='Almería')
        cls.jaen = Province.objects.create(id=2, name='Jaén')
        cls.leon = Province.objects.create(id=3, name='León')
        cls.alava = Province.objects.create(id=4, name='Álava')
        cls.ciudad_real = Province.objects.create(id=5, name='Ciudad Real')
        cls.granada = Province.objects.create(id=6, name='Granada')
        cls.madrid = Province.objects.create(id=7, name='Madrid')
        cls.espana.provinces.add(cls.almeria)
        cls.espana.provinces.add(cls.jaen)
        cls.espana.provinces.add(cls.leon)
        cls.espana.provinces.add(cls.alava)
        cls.espana.provinces.add(cls.ciudad_real)
        cls.espana.provinces.add(cls.granada)
        cls.espana.provinces.add(cls.madrid)
        cls.albanchez = City.objects.create(name='Albanchez', country=cls.espana)
        cls.olula_del_rio = City.objects.create(name='Olula del río', country=cls.espana)
        cls.albanchez_de_magina = City.objects.create(name='Albanchez de Mágina', country=cls.espana)
        cls.villabuena_de_alava = City.objects.create(name='Villabuena de Álava', country=cls.espana)
        cls.almeria_city = City.objects.create(name='Almería', country=cls.espana)
        cls.leon_e = City.objects.create(name='León', country=cls.espana)
        cls.leon_m = City.objects.create(name='León', country=cls.mexico)
        cls.alamillo_cr = City.objects.create(name='Alamillo', country=cls.espana)
        cls.alamillo_g = City.objects.create(name='Alamillo', country=cls.espana)
        cls.las_rozas_de_madrid = City.objects.create(name='Las Rozas de Madrid', country=cls.espana)
        cls.humanes_de_madrid = City.objects.create(name='Humanes de Madrid', country=cls.espana)
        cls.almeria.cities.add(cls.albanchez)
        cls.almeria.cities.add(cls.olula_del_rio)
        cls.almeria.cities.add(cls.almeria_city)
        cls.jaen.cities.add(cls.albanchez_de_magina)
        cls.alava.cities.add(cls.villabuena_de_alava)
        cls.leon.cities.add(cls.leon_e)
        cls.ciudad_real.cities.add(cls.alamillo_cr)
        cls.granada.cities.add(cls.alamillo_g)
        cls.leon.cities.add(cls.leon_e)
        cls.madrid.cities.add(cls.las_rozas_de_madrid)
        cls.madrid.cities.add(cls.humanes_de_madrid)

    def test_the_job_updated_has_been_updated(self):
        # Only check if the any info of the offer has changed, but not the state.
        item_dict={'state':Job.STATE_UPDATED, 'first_publication_date':None, 'last_update_date':self.today}
        item = JobItem(**item_dict)
        self.assertTrue(self.sp._has_been_the_job_updated(Job.objects.get(id=111, state=Job.STATE_UPDATED), item))
        self.assertTrue(self.sp._has_been_the_job_updated(Job.objects.get(id=222, state=Job.STATE_UPDATED), item))
        self.assertFalse(self.sp._has_been_the_job_updated(Job.objects.get(id=333, state=Job.STATE_UPDATED), item))
        self.assertTrue(self.sp._has_been_the_job_updated(Job.objects.get(id=444,  state=Job.STATE_CREATED), item))
        self.assertTrue(self.sp._has_been_the_job_updated(Job.objects.get(id=555), item))
        item = {'state': Job.STATE_CREATED, 'first_publication_date': self.yesterday, 'last_update_date': None}
        self.assertFalse(self.sp._has_been_the_job_updated(Job.objects.get(id=444), item))
        item_dict2 = {'state': Job.STATE_CLOSED, 'first_publication_date': None, 'last_update_date': None, 'expiration_date': None}
        item_dict2 = {**self.default_fields, **item_dict2}
        item2 = JobItem(**item_dict2)
        self.assertTrue(self.sp._has_been_the_job_updated(Job.objects.get(id=555, state=Job.STATE_WITHOUT_CHANGES), item2))
        Job.objects.filter(id=555, state=Job.STATE_WITHOUT_CHANGES).update(**self.default_fields)
        self.assertFalse(self.sp._has_been_the_job_updated(Job.objects.get(id=555), item2))


    def test_update_job(self):
        today = timezone.localtime(timezone.now()).date()
        job_dict = {'state': Job.STATE_CLOSED, 'first_publication_date': None, 'last_update_date': None}
        job_dict = {**job_dict, **self.default_fields}
        item = JobItem(**job_dict)
        Job.objects.filter(id=555, state=Job.STATE_WITHOUT_CHANGES).update(**self.default_fields,)
        job = Job.objects.get(id=555)
        job = self.sp._update_job(job, item)
        job_updated_date = job.updated_at.date()
        self.assertEqual({'state': job.state, 'updated_at': job_updated_date},
                         {'state': item['state'], 'updated_at': today})

    def test_get_city(self):
        self.assertEqual(self.sp._get_city('Albanchez', self.almeria, self.espana), self.albanchez)
        self.assertEqual(self.sp._get_city('Albanchez', None, None), self.albanchez)
        self.assertIsNone(self.sp._get_city('León', None, None)) # León can be a city from Mexico or Spain
        self.assertEqual(self.sp._get_city('León', None, self.mexico), self.leon_m) # León can be a city from Mexico or Spain
        self.assertEqual(self.sp._get_city('León', None, self.espana), self.leon_e) # León can be a city from Mexico or Spain
        self.assertEqual(self.sp._get_city('Albanchez de Magina', None, None), self.albanchez_de_magina)
        self.assertEqual(self.sp._get_city('Olula', self.almeria, self.espana), self.olula_del_rio)
        self.assertIsNotNone(self.sp._get_city('XXX city', self.almeria, self.espana))
        self.assertIsNone(self.sp._get_city('España', None, self.espana))
        self.assertIsNone(self.sp._get_city('Álava', None, self.espana)) # Álava is a province, not a city
        self.assertEqual(self.sp._get_city('Las Rozas', self.madrid, self.espana), self.las_rozas_de_madrid)
        self.assertEqual(self.sp._get_city('Las Rozas', None, self.espana), self.las_rozas_de_madrid)
        self.assertEqual(self.sp._get_city('Las Rozas', None, None), self.las_rozas_de_madrid)
        self.assertEqual(self.sp._get_city('Alamillo', self.granada, self.espana), self.alamillo_g)
        self.assertIsNone(self.sp._get_city('Alamillo', None, None))
        self.assertIsNone(self.sp._get_city('Alamillo', None, self.espana))
        self.assertIsNone(self.sp._get_city('De Madrid', None, None))
        self.assertIsNone(self.sp._get_city('De Madrid', None, self.espana))
        self.assertIsNotNone(self.sp._get_city('De Madrid', self.madrid, self.espana)) # Create a new one (Rozas de Madrid, Humanes de Madrid)
        self.assertIsNotNone(self.sp._get_city('De Madrid', None, self.espana))

    def test_get_location(self):
        cities, province, country = self.sp._get_location(['Albanchez', 'Olula del río'], 'Almería', 'España')
        self.assertEqual(cities, [self.albanchez, self.olula_del_rio])
        self.assertEqual(province, self.almeria)
        self.assertEqual(country, self.espana)
        cities, province, country = self.sp._get_location(['León'], '', 'Mexico')
        self.assertEqual(cities, [self.leon_m])
        self.assertIsNone(province)
        self.assertEqual(country, self.mexico)
        cities, province, country = self.sp._get_location(['León'], '', '')
        self.assertEqual(cities, [])
        self.assertIsNone(province)
        self.assertIsNone(country)
        cities, province, country = self.sp._get_location(['Las Rozas'], '', '')
        self.assertEqual(cities, [self.las_rozas_de_madrid])
        self.assertEqual(province, self.madrid)
        self.assertEqual(country, self.espana)
        cities, province, country = self.sp._get_location(['new city'], 'not a province', 'new country')
        self.assertEqual(cities[0].name, 'new city')
        self.assertIsNone(province)
        self.assertEqual(country.name, 'new country')
        cities, province, country = self.sp._get_location(['alamillo'], '', 'España')
        self.assertEqual(cities, [])
        self.assertIsNone(province)
        self.assertEqual(country, self.espana)
        cities, province, country = self.sp._get_location(['De Madrid'], '', 'España')
        self.assertEqual(cities, [])
        self.assertIsNone(province)
        self.assertEqual(country, self.espana)

    def test_set_locations_from_location(self):
        company_dict = {
            '_location': self.espana.name,
            'city': None,
            'country': None,
            'province': None,
         }
        ci = CompanyItem(**company_dict)
        self.sp._set_locations_from_location(ci)
        self.assertIsNone(ci['city'])
        self.assertIsNone(ci['province'])
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = self.almeria.name
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertEqual(ci['city'], self.almeria_city)
        self.assertEqual(ci['province'], self.almeria)
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = self.alava.name
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertIsNone(ci['city'])
        self.assertEqual(ci['province'], self.alava)
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = 'alamillo'  # Alamillo of Granada and Alamillo fo Ciudad Real
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertIsNone(ci['city'])
        self.assertIsNone(ci['province'])
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = 'albanchez'
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertEqual(ci['city'], self.albanchez)
        self.assertEqual(ci['province'], self.almeria)
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = 'de Madrid'
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertIsNone(ci['city'])
        self.assertEqual(ci['province'], self.madrid)
        self.assertEqual(ci['country'], self.espana)
        ci['_location'] = self.villabuena_de_alava.name
        ci['province'] = None
        ci['country'] = None
        self.sp._set_locations_from_location(ci)
        self.assertEqual(ci['city'], self.villabuena_de_alava)
        self.assertEqual(ci['province'], self.alava)
        self.assertEqual(ci['country'], self.espana)

    def test_get_languages(self):
        l1 = Language.objects.create(name="inglés", level="B2")
        l2 = Language.objects.create(name="francés", level="B1")
        self.assertEqual(self.sp._get_languages([('inglés', 'B2'),('francés', 'B1')]), [l1, l2])

    def test_get_company_upgrade(self):
        company_dict = {
                        'category': 'Recursos Humanos',
                        'description': '',
                        'link': 'https://www.infoempleo.com/colaboradoras/hays/presentacion/',
                        'name': 'Hays Recruiting Experts Worldwide',
                        'offers': 397,
                        'resume': '',
                        'is_registered': True,
                        'city': None,
                        'province': None,
                        'country': None,
                        }
        item = {
            'category': 'Recursos Humanos_',
            'description': 'new description',
            'link': 'https://www.infoempleo.com/colaboradoras/hays/presentacion/______',
            'name': 'XXXXXXXX',
            'offers': 900,
            'resume': 'new resume',
            'is_registered': False,
            'city': self.almeria_city,
            'province': self.almeria,
            'country': self.espana,
        }
        # The name and the link dont suffer upgrade
        upgrade = {
            'category': 'Recursos Humanos_',
            'description': 'new description',
            'offers': 900,
            'resume': 'new resume',
            'city': self.almeria_city,
            'province': self.almeria,
            'country': self.espana,
        }
        company = Company.objects.create(**company_dict)
        self.assertEqual(self.sp._get_company_upgrade(company, item), upgrade)