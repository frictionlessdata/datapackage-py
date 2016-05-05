# coding: utf-8
from __future__ import unicode_literals

import datapackage
import tests.test_helpers as helpers


def test_tsv():
    resource = datapackage.Resource.load({
        'path': helpers.fixture_path('cities.tsv')
    })
    assert resource.data == [
        {'Area': '1807.92', 'Name': 'Acrelândia', 'Population': '12538', 'State': 'AC'},
        {'Area': '186.53', 'Name': 'Boca da Mata', 'Population': '25776', 'State': 'AL'},
        {'Area': '242.62', 'Name': 'Capela', 'Population': '17077', 'State': 'AL'},
        {'Area': '6709.66', 'Name': 'Tartarugalzinho', 'Population': '12563', 'State': 'AP'},
        {'Area': '837.72', 'Name': 'América Dourada', 'Population': None, 'State': 'BA'},
        {'Area': '204.79', 'Name': 'Jijoca de Jericoacoara', 'Population': '17002', 'State': 'CE'},
        {'Area': '6953.67', 'Name': 'Cavalcante', 'Population': '9392', 'State': 'GO'},
        {'Area': '8258.42', 'Name': 'Centro Novo do Maranhão', 'Population': '17622', 'State': 'MA'},
        {'Area': '3651.18', 'Name': 'Ped\ro Gomes', 'Population': '7967', 'State': 'MS'},
        {'Area': '881.06', 'Name': 'Abadia dos Dourados', 'Population': '6704', 'State': 'MG'},
    ]
