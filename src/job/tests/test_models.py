#import sys, os
#sys.path.append(os.path.abspath(os.path.join('.', 'ie_scrapy')))
#print(os.path.abspath(os.path.join('.', 'ie_scrapy')))
from django.test import TestCase
from ie_scrapy.pipelines import CleaningPipeline
import datetime
from dateutil.relativedelta import relativedelta

print(__file__)
class TestCleaningPipeline(TestCase):

    cp = CleaningPipeline()

    def execute(self):
        self.clean_job_date()
        self.clean_url()
        self.clean_provinces()
        self.clean_cities()
        self.clean_job_type()
        self.clean_salary()
        self.get_annual_salary()
        self.get_it_is_offered()


    def test_clean_job_date(self):
        today = datetime.date.today()
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date("Hace 25 meses"), today - relativedelta(months=25))
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date('Hace 3 dias'), today - relativedelta(days=3))
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date('Hace 3 días'), today - relativedelta(days=3))
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date('Hace 36 horas'), today - relativedelta(days=int(36/24)))
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date('Hace 1 hora'), today - relativedelta(days=int(1/24)))
        self.assertEqual(TestCleaningPipeline.cp._clean_job_date('Hace 2 años'), today - relativedelta(years=2))
        

    def test_clean_url(self):
        self.assertEqual(TestCleaningPipeline.cp._clean_url('/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'), 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')
        self.assertEqual(TestCleaningPipeline.cp._clean_url('https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'), 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')
        self.assertEqual(TestCleaningPipeline.cp._clean_url('https://www.infoempleo.com'), '')
        self.assertEqual(TestCleaningPipeline.cp._clean_url('https://www.repsol.es/es/index.cshtml'), 'https://www.repsol.es/es/index.cshtml')
        

    def test_clean_provinces(self):
        self.assertEqual(TestCleaningPipeline.cp._clean_province('Álcala del Valle (Cádiz)'), 'Cádiz')
        self.assertEqual(TestCleaningPipeline.cp._clean_province('Móstoles, Alcorcón, Bercial (el) (Madrid)'), 'Madrid')
        

    def test_clean_cities(self):
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Álcala del Valle (Cádiz)'), ['Álcala del Valle'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Móstoles, Alcorcón, Bercial (el) (Madrid)'), ['Móstoles', 'Alcorcón', 'El Bercial'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Móstoles, Alcorcón, Bercial (el), etc (Madrid)'), ['Móstoles', 'Alcorcón', 'El Bercial'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Móstoles, Alcorcón, Bercial (el), alrededores de Madrid, etc (Madrid)'), ['Móstoles', 'Alcorcón', 'El Bercial', 'Madrid'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Belfast y alrededores'), ['Belfast'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('Oxford alrededores (Gran Bretaña)'), ['Oxford'])
        self.assertEqual(TestCleaningPipeline.cp._clean_cities('.'), [])
        

    def test_clean_job_type(self):
        self.assertEqual(TestCleaningPipeline.cp._clean_job_type('https://www.infoempleo.com/ofertas-internacionales/?pagina=5'), 'ofertas-internacionales')
        self.assertEqual(TestCleaningPipeline.cp._clean_job_type('https://www.infoempleo.com/ofertas-internacionales/'), 'ofertas-internacionales')
        self.assertEqual(TestCleaningPipeline.cp._clean_job_type('https://www.infoempleo.com/ofertasdetrabajo/administradora-junior-de-ms-sharepoint/hamburgo/2618631/'), 'trabajo') #!
        self.assertEqual(TestCleaningPipeline.cp._clean_job_type('https://www.christianpost.com/news'), '')
        

    def test_clean_salary(self):
        text="Se    ofrece    -   ...\
         -    3000 Sueldo anual neto entre 43.500€ o 45.000€;    -    Alojamiento..."
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (43500, 45000))
        text="Se    ofrece    -   ...\
         -    Sueldo anual neto entre 43550€ a  45600€;    -    Alojamiento..."
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (43550, 45600))
        text = "el sueldo  de 3.000 puede ser inicialmente de 3.300€ netos/mes o 3.430€ netos/mes dependiendo de la especialidad"
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (3300, 3430))
        text = "3000 3.300€ netos/mes o 3.430"
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (3300, 3430))
        text = "3000 3.300€ netos/mes  3.430 5000"
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (3300, 3430))
        text = "3.300€ netos/mes "
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (3300, 3300))
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual( TestCleaningPipeline.cp._clean_salary(text, True), (2270, 2270))
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual(TestCleaningPipeline.cp._clean_salary(text, True), (2270, 2270))
        text = "Entre 1000 y 20000€ brutos/anuales "
        self.assertEqual(TestCleaningPipeline.cp._clean_salary(text, False), (1000, 20000))
        
    def test_get_annual_salary(self):
        text = "Se    ofrece    -   ...\n -  Sueldo anual neto entre 43.500€ a 45.000€;  -    Alojamiento..."
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [43500, 45000])
        text = "Salario Medio Mensual Neto entre 5.000€ a 10.000€ (en función del tipo de tratamientos efectuados"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [60000, 120000])
        text = "actualización salarial, en media actualmente, además del valor inicial base neto de 3.300€. \
                Ganará un Salario Mensual Neto (exento de impuestos en Arabia Saudí) base de 3.300€ como punto de referencia. \
                La propuesta final viene dada según su experiencia profesional y grado de especialización. \
                Así el sueldo será aún más competitivo en función de su experiencia profesional (que es valorizada)  \
                y el nivel de especialización (se valoriza enfermeros especialistas).\
                El sueldo inicial es de 3.300€ netos/mes o 3.430€ netos/mes dependiendo de la especialidad \
                +15 días de Bonos + adicionales USD de 2.500. Anualmente el sueldo líquido varía entre 43.500€ a 45.000€. Con su"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [39600, 41160])
        text = "Salario: 15.500 € b/a"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [15500, 15500])
        text = "El salario es de 14.26€ brutos/hora (2.270 euros b/mes) "
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [27240, 27240])
        text = "empresa con un salario de 17.000 euros brutos al año o 18.000 euros brutos al año, además, cada mes, te podrás llevar entre 1500€ y 1700€. Tu horario"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [17000, 18000])
        text = "empresa con un salario de 17.000 euros brutos al año, 1500€ a 1700€ b/m. Tu horario"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [17000, 17000])
        text = "salario mensual de 2500 euros y al año de 30000"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [30000, 30000])
        text = " +15 días de Bonos + adicionales USD de 2.500. Anualmente el sueldo líquido varía entre 43.500€ a 45.000€. Con su"
        self.assertEqual(TestCleaningPipeline.cp._get_annual_salary(text), [43500, 45000])
        

    def test_get_it_is_offered(self):
        self.assertEqual( TestCleaningPipeline.cp._get_it_is_offered("... ..."), "")
        self.assertEqual( TestCleaningPipeline.cp._get_it_is_offered("...te ofrece ..."), "")
        self.assertEqual( TestCleaningPipeline.cp._get_it_is_offered("...Te ofrecemos un contrato ..."), "un contrato ...")
        self.assertEqual( TestCleaningPipeline.cp._get_it_is_offered("...Se ofrece: un contrato ..."), "un contrato ...")


