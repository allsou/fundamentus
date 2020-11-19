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
    pattern = re.compile('Valor da firma</span>.*Número total de ações', re.DOTALL)
    enterprise_value = re.findall(pattern, content)
    LOGGER.debug(enterprise_value)
    pattern = re.compile('<span class="txt">EBIT</span></td>.*</tr>', re.DOTALL)
    ebit = re.findall(pattern, content)
    LOGGER.debug(ebit)
    # page = fragment_fromstring(content)
    # LOGGER.debug(page)



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

    return result


def to_decimal(string):
    string = string.replace('.', '')
    string = string.replace(',', '.')

    if string.endswith('%'):
        string = string[:-1]
        return Decimal(string) / 100
    else:
        return Decimal(string)


if __name__ == '__main__':
    LOGGER.info('Starting crawler')
    result = get_papers()

    result_format = '{0:<7} {1:<7} {2:<10} {3:<7} {4:<10} {5:<7} {6:<10} {7:<10} {8:<10} {9:<11} {10:<11} {11:<7} {12:<11} {13:<11} {14:<7} {15:<11} {16:<5} {17:<7}'
    print(
        result_format.format(
            'Papel',
            'Cotacao',
            'P/L',
            'P/VP',
            'PSR',
            'DY',
            'P/Ativo',
            'P/Cap.Giro',
            'P/EBIT',
            'P/ACL',
            'EV/EBIT',
            'EV/EBITDA',
            'Mrg.Ebit',
            'Mrg.Liq.',
            'Liq.Corr.',
            'ROIC',
            'ROE',
            'Liq.2meses',
            'Pat.Liq',
            'Div.Brut/Pat.',
            'Cresc.5anos'
        )
    )

    print('-' * 190)
    for key, value in result.items():
        print(
            result_format.format(
                key,
                value['Cotacao'],
                value['P/L'],
                value['P/VP'],
                value['PSR'],
                value['DY'],
                value['P/Ativo'],
                value['P/Cap.Giro'],
                value['P/EBIT'],
                value['P/ACL'],
                value['EV/EBIT'],
                value['EV/EBITDA'],
                value['Mrg.Ebit'],
                value['Mrg.Liq.'],
                value['Liq.Corr.'],
                value['ROIC'],
                value['ROE'],
                value['Liq.2meses'],
                value['Pat.Liq'],
                value['Div.Brut/Pat.'],
                value['Cresc.5anos']
            )
        )
