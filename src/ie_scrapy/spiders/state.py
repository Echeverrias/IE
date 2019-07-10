class State():
    states = None
    start_urls = None

    def __init__(self, start_urls):
        print('********************************')
        print('STATE.__INIT__')
        print('********************************')
        self.start_urls = start_urls
        self.reset_state()

    def update_state(self, response):
        print('#State.__update_state')
        url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], response.url)[0]
        results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
        text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
        numbers = [int(s) for s in text.split() if s.isdigit()]

        state_info = {
            'default_results_showed': (numbers[1] - numbers[0] + 1),
            'total_results': numbers[2],
            'last_result_parsed': numbers[1],
            'total_pages': math.celi(numbers[2] / (numbers[1] - numbers[0] + 1)),
            'last_page_parsed': math.celi(numbers[1] / (numbers[1] - numbers[0] + 1)),
        }
        state = StateItems.objects_get(url=url)
        if not new_state_created:
            state.results_count = state.results_count + 1

        print(state)
        state.save()

    def init_state(self, response):
        print('#State.__update_state')
        url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], response.url)[0]
        results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
        text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
        numbers = [int(s) for s in text.split() if s.isdigit()]

        state_info = {
            'default_results_showed': (numbers[1] - numbers[0] + 1),
            'total_results': numbers[2],
            'total_pages': math.celi(numbers[2] / (numbers[1] - numbers[0] + 1)),
        }
        state, new_state_created = StateItems.objects_get_or_create(url=url, defaults=state_info)
        if not new_state_created:
            print('The state exists')
            state.total_results = defaults['total_results']
            state.total_pages = defaults['total_pages']

            state.save()
        print(state)

    def parse_results(self, response):
        url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], response.url)[0]
        result = None
        hrefs_xpath = "//*[@id='main-content']/div[2]/ul/li/h2/a/@href"
        try:
            state = self.states.get(url=url)
            if state.state_updated:
                result = response.xpath(hrefs_xpath).extract()
        except:  # The 'start_url haven't been parsed any time'
            result = response.xpath(hrefs_xpath).extract()
        return result

    def reset_state(self):

        for url in self.start_urls:
            StateItems.objects_get_or_created(url=url)
        self.states = self.__get_states()
        try:
            for state in self.states:
                if not state.scrapping_completed:
                    state.results_count = 0
                state.save()
        except:
            pass

    def _get_page_from_state(self, response):
        try:
            state = self.__get_states().get(response.url)
            if state and state.scrapping_completed:
                return 1
            else:
                return state.last_page
        except:
            return 1

    def __get_states(self):
        if not self.states:
            try:
                self.states = StateItems.objects_all()
                print('__get_states')
                print(self.states)
                [s for s in states]
            except:
                pass
        return self.states


def get_page(response):
    try:
        page = int(re.findall(r'\d+', response.url)[0])
    except:
        page = 1
        print('The page is %i' % page)
    return page