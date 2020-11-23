#!/usr/bin/env python3

import http.cookiejar
import logging
import re
import urllib.parse
import urllib.request
from collections import OrderedDict
from decimal import Decimal

from lxml.html import fragment_fromstring

LOGGER = logging.getLogger('sLogger')


def get_details_by_paper(paper_name: str):
    LOGGER.info('Getting papers details at Fundamentus...')
    url = f'http://www.fundamentus.com.br/detalhes.php?papel={paper_name}'
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
        ('Accept', 'text/html, text/plain, text/css, text/sgml, */*;q=0.01')
    ]
    with opener.open(url) as link:
        LOGGER.info(f'Establishing connection to {url}...')
        content = link.read().decode('ISO-8859-1')
    LOGGER.debug('Using regex to get Ev')
    pattern = re.compile('Valor da firma</span>.*Número total de ações', re.DOTALL)
    enterprise_value = re.findall(pattern, content)
    enterprise_value = int(enterprise_value[0].split('<')[4].split('>')[1].replace('.', ''))
    LOGGER.debug(f'Ev {paper_name}: {enterprise_value}')
    LOGGER.debug('Using regex to get Ebit')
    pattern = re.compile('<span class="txt">EBIT</span></td>.*</tr>', re.DOTALL)
    ebit = re.findall(pattern, content)
    ebit = int(ebit[0].split('<')[5].split('>')[1].replace('.', ''))
    LOGGER.debug(f'Ebit {paper_name}: {ebit}')
    result = enterprise_value - ebit
    LOGGER.debug(f'Ev-Ebit {paper_name}: {result}')
    return result, ebit/enterprise_value

def get_papers():
    LOGGER.info('Getting papers at Fundamentus...')
    url = 'http://www.fundamentus.com.br/resultado.php'
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
        ('Accept', 'text/html, text/plain, text/css, text/sgml, */*;q=0.01')
    ]
    # Eliminamos empresas com liquidez inferior a R$ 200.000,00
    # Eliminamos empresas com margem ebit negativa
    query = {
        'pl_min': '',
        'pl_max': '',
        'pvp_min': '',
        'pvp_max': '',
        'psr_min': '',
        'psr_max': '',
        'divy_min': '',
        'divy_max': '',
        'pativos_min': '',
        'pativos_max': '',
        'pcapgiro_min': '',
        'pcapgiro_max': '',
        'pebit_min': '',
        'pebit_max': '',
        'fgrah_min': '',
        'fgrah_max': '',
        'firma_ebit_min': '',
        'firma_ebit_max': '',
        'margemebit_min': '0',
        'margemebit_max': '',
        'margemliq_min': '',
        'margemliq_max': '',
        'liqcorr_min': '',
        'liqcorr_max': '',
        'roic_min': '',
        'roic_max': '',
        'roe_min': '',
        'roe_max': '',
        'liq_min': '200000',
        'liq_max': '',
        'patrim_min': '',
        'patrim_max': '',
        'divbruta_min': '',
        'divbruta_max': '',
        'tx_cresc_rec_min': '',
        'tx_cresc_rec_max': '',
        'setor': '',
        'negociada': 'ON',
        'ordem': '1',
        'x': '28',
        'y': '16'
    }

    with opener.open(url, urllib.parse.urlencode(query).encode('UTF-8')) as link:
        LOGGER.info(f'Establishing connection to {url}...')
        content = link.read().decode('ISO-8859-1')

    LOGGER.info('Using regex to get results...')
    pattern = re.compile('<table id="resultado".*</table>', re.DOTALL)
    content = re.findall(pattern, content)[0]
    page = fragment_fromstring(content)
    result = OrderedDict()
    LOGGER.debug('Iterating table')
    for rows in page.xpath('tbody')[0].findall("tr"):
        result.update(
            {
                rows.getchildren()[0][0].getchildren()[0].text: {
                    'Cotacao': to_decimal(rows.getchildren()[1].text),
                    'P/L': to_decimal(rows.getchildren()[2].text),
                    'P/VP': to_decimal(rows.getchildren()[3].text),
                    'PSR': to_decimal(rows.getchildren()[4].text),
                    'DY': to_decimal(rows.getchildren()[5].text),
                    'P/Ativo': to_decimal(rows.getchildren()[6].text),
                    'P/Cap.Giro': to_decimal(rows.getchildren()[7].text),
                    'P/EBIT': to_decimal(rows.getchildren()[8].text),
                    'P/ACL': to_decimal(rows.getchildren()[9].text),
                    'EV/EBIT': to_decimal(rows.getchildren()[10].text),
                    'EV/EBITDA': to_decimal(rows.getchildren()[11].text),
                    'Mrg.Ebit': to_decimal(rows.getchildren()[12].text),
                    'Mrg.Liq.': to_decimal(rows.getchildren()[13].text),
                    'Liq.Corr.': to_decimal(rows.getchildren()[14].text),
                    'ROIC': to_decimal(rows.getchildren()[15].text),
                    'ROE': to_decimal(rows.getchildren()[16].text),
                    'Liq.2meses': to_decimal(rows.getchildren()[17].text),
                    'Pat.Liq': to_decimal(rows.getchildren()[18].text),
                    'Div.Brut/Pat.': to_decimal(rows.getchildren()[19].text),
                    'Cresc.5anos': to_decimal(rows.getchildren()[20].text)
                }
            }
        )
    LOGGER.debug('Parsing to dict')
    result = {
        outer_k:
            {
                inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()
            } for outer_k, outer_v in result.items()
    }
    return result


def to_decimal(string):
    string = string.replace('.', '')
    string = string.replace(',', '.')

    if string.endswith('%'):
        string = string[:-1]
        return Decimal(string) / 100
    else:
        return Decimal(string)
