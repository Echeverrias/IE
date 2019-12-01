import threading
import json
import math

class UrlsState():
    """"
    To save the count of parsed results from each url of wanted results.
    """

    results_per_page = 20
    _lock = threading.Lock()

    
    def __init__(self):
        # parsed_urls: {'key': {'total_results': int, 'results_parsed':int }}
        self.parsed_urls = self._load_parsed_urls_state()
        for url in self.parsed_urls.keys():
            self._init_url_state(url)


    def _save_parsed_urls_state(self, data_dict):
        #print('#UrlsState.__save_parsed_urls_state({})'.format(data_dict))
        with self._lock:
            #print('#UrlsState.__save_parsed_urls_state({})'.format(data_dict))
            with open('parsed urls state.json', 'w') as fw:
                print('#saving_parsed_urls_state')
                #print(data_dict)
                fw.write(json.dumps(data_dict))

    
    def _get_pending_page(self, url):
        state = self.get_parsed_url_state(url)
        total_results = state['total_results']
        results_parsed = state['results_parsed']
        if (results_parsed >= total_results) :
            state['results_parsed'] = 0
            return 1
        else:
            min_page = 1
            pending_page = math.ceil(float(results_parsed) / float(self.results_per_page))
            return max(pending_page, min_page)

    
    def _init_url_state(self, url):
        state = self.get_parsed_url_state(url)
        pending_page = self._get_pending_page(url)
        state['results_parsed'] = (pending_page - 1) * self.results_per_page

    
    def _load_parsed_urls_state(self):

        print('load')
        try:
            with open('parsed urls state.json', 'r') as fr:
                parsed_urls_state = json.loads(fr.read())
            #print(f'load parsed_urls_state: {parsed_urls_state}')
               # print(f'parsed_urls_state.keys: {parsed_urls_state.keys()}'
            return parsed_urls_state
        except:
            print('# NOT STATES IN THE *.json')
            return {}


    def close(self):
        self._save_parsed_urls_state(self.parsed_urls)

    
    def _create_parsed_url_state(self, url):
       # print('create_parsed_url_state: %s' % url)
        state = {
            'results_parsed': 0,
            'total_results': 0,
        }
        return self.parsed_urls.setdefault(url, state)

    
    def get_parsed_url_state(self, url):
        if not self.parsed_urls:
            print(f'Doesnt exist state of {url}')
        return self.parsed_urls.get(url, self._create_parsed_url_state(url))


    
    def update_url_state(self, url, total_results):
        """ Increment the number of results parsed from an url of wanted results.

        Increment the number of results in one.

        :param url: The key, the url
        :param total_results: total_results

        """
        #print('#UrlState.update_url_state({}, {})'.format(url, total_results))
        state = self.parsed_urls.get(url, self._create_parsed_url_state(url))
        state['total_results'] = total_results
        if state['results_parsed'] >= (total_results - 1):
            state['results_parsed'] = 0
        else:
            state['results_parsed'] += 1
        self._save_parsed_urls_state(self.parsed_urls)

    
    def reset_url_state(self, url):
        print(f'UrlState.reset_url_state({url})')
        state = self.parsed_urls.get(url, None)
        if state:
            state['results_parsed'] = 0
            self._save_parsed_urls_state(self.parsed_urls)

    
    def get_pending_url(self, url):
        page = self._get_pending_page(url)
        print('#get_pending_url: {}'.format("{}?pagina={}".format(url, str(page))))
        if int(page) > 1:
            return "{}?pagina={}".format(url, str(page))
        else:
            return url
