import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm

# Se capturan los datos del archivo export_all.csv en un dataframe,
# eliminando los duplicados directamente en el dataframe

visited = set()

def get_all_pages(pages, url, domain, visited):
    """
    Metodo Recursivo que obtiene todas las paginas de un dominio
    """
    # make an HTTP GET request to the website
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    except:
        print(f'Error al cargar la página {url}')
        return pages

    # parse the HTML content of the website
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all links in the HTML content
    links = soup.find_all('a')

    # extract the URLs from the links
    for link in links:
        page = link.get('href')
        if not page:
            continue
        if page[0] == '/':
            page = f'https://{domain}{page}'
        elif page[0] == 'w':
            page = f'https://{page}'
        if domain not in page or page in visited or page.endswith('.jpg'):
            continue
        print(f'Inx {len(visited)} - Scaning: {page}')
        df = pd.DataFrame([page], columns=['URL'])
        # Se escribe el dataframe en un archivo csv añadiendo los datos al final del archivo
        df.to_csv('export_all.csv', index=False, mode='a', header=False)
        visited.add(page)
        pages.append(page)

    for page in tqdm(pages):
        pages += get_all_pages([], page, domain, visited)

    return pages


def main():
    # the URL of the website to crawl
    domain = 'www.idbinvest.org'
    url = f'https://{domain}'
    pages = []
    # get all the URLs on the website
    pages = get_all_pages(pages, url, domain, visited)

if __name__ == '__main__':
    main()