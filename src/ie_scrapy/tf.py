
def __get_city(self, city_name, province=None, country=None):
    debug['location'] = f'CleanPipeline._get_city'
    debug['value'] = f'city_name {city_name}'
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(f'__get_city{city_name, province, country}')
    if not city_name:
        return None

    city = None
    if country and country.name == 'España':
        print('The country is España')
        # first search with iexact
        if province:
            print('Province <> None (iexact)')
            cities_qs = City.objects.filter(country=country, province=province, name__iexact=city_name)
        else:
            print('Province == None (iexact)')
            cities_qs = City.objects.filter(country=country, name__iexact=city_name)
        print(f'result: {cities_qs}')
        # second search with icontains
        if cities_qs:
            city = cities_qs[0]
        else:
            print('not iexact city found')
            if province:
                print('Province <> None (icontains)')
                cities_qs = City.objects.filter(country=country, province=province, name__icontains=city_name)
            else:
                print('Province == None (icontains)')
                cities_qs = City.objects.filter(country=country, name__icontains=city_name)
            print(f'result: {cities_qs}')
            if cities_qs.count() > 1:
                print(f'more than one result')
                cities_qs = cities_qs.filter(name__icontains='/')
                for city in cities_qs:
                    cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                cities_qs = cities
            if cities_qs:
                city = cities_qs[0]
                if province:
                    city.province = province
                    city.save()
            elif province and (city_name != province.name):
                city = City.objects.create(name=city_name, province=province, country=country)

    elif country and (city_name.lower() == country.name.lower() or city_name.lower() == CleanupPipeline_.get_acronym(
            country.name).lower()):
        return None
    # a foreign city:
    elif country:
        cities_qs = City.objects.filter(name__iexact=city_name, country=country)
        if cities_qs:
            city = cities_qs[0]
        else:
            city, is_a_new_city = City.objects.get_or_create(name=city_name, country=country)
    else:
        cities_qs = City.objects.filter(name__iexact=city_name)
        if not cities_qs:
            cities_qs = City.objects.filter(name__icontains=city_name)
            if cities_qs and cities_qs.count() > 1:
                cities_qs = cities_qs.filter(name__icontains='/')
                for city in cities_qs:
                    cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                cities_qs = cities
            if cities_qs:
                city = cities_qs[0]
    return city


def __get_location(self, city_names, province_name, country_name):
    print('#Pipeline__get_location: %s %s %s' % (city_names, province_name, country_name))
    country = None
    province = None
    if country_name:
        country, is_a_new_country = Country.objects.get_or_create(name=country_name)
    try:
        provinces = Province.objects.filter(name__iexact=province_name)
        print('provinces %s' % provinces)
        province = provinces[0]
    except:
        print('Error getting the province')
    print('Country: %s' % country)
    cities = []
    for city_name in city_names:
        cities.append(self.__get_city(city_name, province, country))
    # Deleting the null cities:
    cities = list(filter(lambda c: c, cities))
    print('#_get_location return: %s %s %s' % (cities, province, country))
    return cities, province, country