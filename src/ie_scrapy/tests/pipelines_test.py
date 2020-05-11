from ..pipelines import CleaningPipeline, StoragePipeline
import datetime
from dateutil.relativedelta import relativedelta

cp = CleaningPipeline()

def cleaningPipelineTest():
    clean_job_date_test()
    clean_url_test()
    clean_provinces_test()
    clean_cities_test()

def clean_job_date_test():
    today = datetime.date.today()
    assert(cp._clean_job_date("Hace 25 meses")) == today - relativedelta(months=25)
    assert(cp._clean_job_date('Hace 3 dias')) == today - relativedelta(days=3)
    assert(cp._clean_job_date('Hace 3 días')) == today - relativedelta(days=3)
    assert(cp._clean_job_date('Hace 47 horas')) == today - relativedelta(days=int(47/24))
    assert(cp._clean_job_date('Hace 2 años')) == today - relativedelta(years=2)
    return True

def clean_url_test():
    assert (cp._clean_url('/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')) == 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'
    assert (cp._clean_url('https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/')) == 'https://www.infoempleo.com/ofertasdetrabajo/gestora-punto-de-venta-pais-vasco/bilbao/2618860/'
    assert (cp._clean_url('https://www.infoempleo.com')) == ''
    assert (cp._clean_url('https://www.repsol.es/es/index.cshtml')) == 'https://www.repsol.es/es/index.cshtml'
    return True

def clean_provinces_test():
    assert(cp._clean_province('Álcala del Valle (Cádiz)')) == 'Cádiz'
    assert(cp._clean_province('Móstoles, Alcorcón, Bercial (el) (Madrid)')) == 'Madrid'
    return True

def clean_cities_test():
    assert(cp._clean_cities('Álcala del Valle (Cádiz)')) == ['Álcala del Valle']
    assert(cp._clean_cities('Móstoles, Alcorcón, Bercial (el) (Madrid)')) == ['Móstoles', 'Alcorcón', 'El Bercial']
    assert(cp._clean_cities('Móstoles, Alcorcón, Bercial (el), etc (Madrid)')) == ['Móstoles', 'Alcorcón', 'El Bercial']
    assert(cp._clean_cities('Móstoles, Alcorcón, Bercial (el), alrededores de Madrid, etc (Madrid)')) == ['Móstoles', 'Alcorcón', 'El Bercial', 'Madrid']
    assert(cp._clean_cities('Belfast y alrededores')) == ['Belfast']
    assert(cp._clean_cities('Oxford alrededores (Gran Bretaña)')) == ['Oxford']
    assert(cp._clean_cities('.')) == []
    return True
