from requests_html import HTML, HTMLSession
from job.models import Company
from django_mysql.models import ListF


def _clean_company_link(url):
    url_base = "https://www.infoempleo.com"
    if not url_base in url:
        return url_base + url
    else:
        return url

def _clean_companies_links(links):
    url_base = "https://www.infoempleo.com/"
    links_ = set(links)
    links_ = list(map(_clean_company_link, links_))
    links_ = [link for link in links_ if link != url_base]
    return links_


def _get_collaboratin_companies_page():
    session = HTMLSession()
    res = session.get("https://www.infoempleo.com/empresas-colaboradoras/")
    return res

def _get_collaboratin_companies():
    html = _get_collaboratin_companies_page().html
    eareas = html.xpath('//div[contains(@id, "lightbox-subarea")]')
    companies = {}
    for earea in eareas:
        area_text = earea.find('header', first=True).text
        elinks = earea.find('a')
        links = [elink.attrs.get('href', '/') for elink in elinks if elink.attrs.get('href', '/') != '/']
        companies[area_text] = _clean_companies_links(links)
    return companies

def _populate_company(area, link):
    qs = Company.objects.filter(link=link)
    if qs:
        for company in qs:
            try:
                if area not in company.area:
                    company.area.append(area)
                    company.save()
            except: # The company hasn't an area yet
                company.area = [area]
                company.save()
    else:
        company = Company(area=[area], link=link)
        company.save()


def _populate_companies(companies):
    for area, links in companies.items():
        for link in links:
            _populate_company(area, link)

def scrape_and_update_or_create_collaboratin_companies():
    companies = _get_collaboratin_companies()
    _populate_companies(companies)