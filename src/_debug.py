from job.models import Job

def do():
    links =  [
    'https://www.infoempleo.com/ofertasdetrabajo/promotoresas/sant-quirze/2596529/',
    'https://www.infoempleo.com/ofertasdetrabajo/camarerosas-para-hotel/vid-y-barrios-la/2609543/',
    'https://www.infoempleo.com/ofertasdetrabajo/ayudante-cocina-avanzado-para-hotel/vid-la/2615897/',
    'https://www.infoempleo.com/ofertasdetrabajo/cocineroa-para-hotel/vid-la/2615899/',
    'https://www.infoempleo.com/ofertasdetrabajo/administrativoa-con-ingles-alto/prat/1966591/',
    'https://www.infoempleo.com/ofertasdetrabajo/operadoraor-de-mantenimiento-mecanico/almanzora/2129126/',
    'https://www.infoempleo.com/ofertasdetrabajo/ayudante-cocina-avanzado-para-colectividad/vid-la/2612429/',
    'https://www.infoempleo.com/ofertasdetrabajo/sales-executive/prat/1962110/',
    'https://www.infoempleo.com/ofertasdetrabajo/mozoa-manipuladora-pedidos-zal-2-el-prat-de-ll-40-horas/prat/2464966/'
    'https://www.infoempleo.com/ofertasdetrabajo/repartidora/sant-feliu/2622103/',
        ]

    for link in links:
        try:
            Job.objects.get(link=link).delete()
        except Exception as e:
            print(f'Error: {e}')