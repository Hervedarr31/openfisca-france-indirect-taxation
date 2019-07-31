# -*- coding: utf-8 -*-

import os
import pkg_resources
import pandas as pd

from openfisca_france_indirect_taxation.model.base import ParameterNode


def preprocess_legislation(parameters):
    '''
    Preprocess the legislation parameters to add prices and amounts from national accounts
    '''
    default_config_files_directory = os.path.join(
        pkg_resources.get_distribution('openfisca_france_indirect_taxation').location)

    prix_annuel_carburants = pd.read_csv(
        os.path.join(
            default_config_files_directory,
            'openfisca_france_indirect_taxation',
            'assets',
            'prix',
            'prix_annuel_carburants.csv'
            ), sep =','
        )
    prix_annuel_carburants['Date'] = prix_annuel_carburants['Date'].astype(int)
    prix_annuel_carburants = prix_annuel_carburants.set_index('Date')
    prix_carburants = dict()

    # For super_95_e10, we need to use the price of super_95 between 2009 and 2012 included,
    # because we don't have the data. We use super_95 because it is very close and won't affect the results too much
    prix_annuel = prix_annuel_carburants['super_95_e10_ttc']
    years = list(range(2013, 2017))
    years = sorted(years, key=int, reverse=True)
    values = dict()
    for year in years:
        values['{}-01-01'.format(year)] = dict(value = prix_annuel[year] * 100)

    years = list(range(2009, 2013))
    years = sorted(years, key=int, reverse=True)
    for year in years:
        values['{}-01-01'.format(year)] = dict(value = prix_annuel[year] * 100)

    years = list(range(1990, 2009))
    years = sorted(years, key=int, reverse=True)
    for year in years:
        values['{}-01-01'.format(year)] = dict(value = prix_annuel[year] * 100)

    prix_carburants['super_95_e10_ttc'] = {
        "description": 'super_95_e10_ttc'.replace('_', ' '),
        "unit": "currency",
        "values": values
        }
    autres_carburants = [
        'diesel_ht',
        'diesel_ttc',
        'gplc_ht',
        'gplc_ttc',
        'super_95_e10_ht',
        'super_95_ht',
        'super_95_ttc',
        'super_98_ht',
        'super_98_ttc',
        'super_plombe_ht',
        'super_plombe_ttc',
        ]
    for element in autres_carburants:
        assert element in prix_annuel_carburants.columns
        prix_annuel = prix_annuel_carburants[element]
        years = list(range(1990, 2017))
        years = sorted(years, key=int, reverse=True)
        values = dict()
        for year in years:
            values['{}-01-01'.format(year)] = prix_annuel[year] * 100

        prix_carburants[element] = {
            "description": element.replace('_', ' '),
            "unit": "currency",
            "values": values
            }
    prix_carburants['description'] = "Prix des carburants"
    node_prix_carburants = ParameterNode(
        'prix_carburants',
        data = prix_carburants,
        )
    parameters.add_child('prix_carburants', node_prix_carburants)

    # Add the number of vehicle in circulation to the tree
    parc_annuel_moyen_vp = pd.read_csv(
        os.path.join(
            default_config_files_directory,
            'openfisca_france_indirect_taxation',
            'assets',
            'quantites',
            'parc_annuel_moyen_vp.csv'
            ), sep =','
        )

    parc_annuel_moyen_vp = parc_annuel_moyen_vp.set_index('Unnamed: 0')
    parc_vp = {
        "description": "taille moyenne du parc automobile en France métropolitaine en milliers de véhicules",
        }
    for element in ['diesel', 'essence']:
        taille_parc = parc_annuel_moyen_vp[element]
        years = list(range(1990, 2017))
        years = sorted(years, key=int, reverse=True)
        values = dict()
        for year in years:
            values['{}-01-01'.format(year)] = taille_parc[year]

        parc_vp[element] = {
            "description": "nombre de véhicules particuliers immatriculés en France à motorisation " + element,
            "unit": 1000,
            "values": values,
            }

    node_parc_vp = ParameterNode(
        'parc_vp',
        data = parc_vp,
        )
    parameters.add_child('parc_vp', node_parc_vp)

    # Add the total quantity of fuel consumed per year to the tree
    quantite_carbu_vp_france = pd.read_csv(
        os.path.join(
            default_config_files_directory,
            'openfisca_france_indirect_taxation',
            'assets',
            'quantites',
            'quantite_carbu_vp_france.csv'
            ), sep =','
        )

    quantite_carbu_vp_france = quantite_carbu_vp_france.set_index('Unnamed: 0')
    quantite_carbu_vp = {
        "description": "quantite de carburants consommés en France métropolitaine",
        }
    for element in ['diesel', 'essence']:
        quantite_carburants = quantite_carbu_vp_france[element]
        # values_quantite[element] = []
        years = list(range(1990, 2017))
        years = sorted(years, key=int, reverse=True)
        values = dict()
        for year in years:
            values['{}-01-01'.format(year)] = quantite_carburants[year]

        quantite_carbu_vp[element] = {
            "description": "consommation totale de " + element + " en France",
            "values": values
            }

    node_quantite_carbu_vp = ParameterNode(
        'quantite_carbu_vp',
        data = quantite_carbu_vp,
        )
    parameters.add_child('quantite_carbu_vp', node_quantite_carbu_vp)

    # Add the shares of each type of supercabrurant (SP95, SP98, E10, etc.) among supercarburants
    part_des_types_de_supercarburants = pd.read_csv(
        os.path.join(
            default_config_files_directory,
            'openfisca_france_indirect_taxation',
            'assets',
            'part_des_types_de_supercarburants.csv'
            ), sep =';'
        )

    del part_des_types_de_supercarburants['Source']
    part_des_types_de_supercarburants = \
        part_des_types_de_supercarburants[part_des_types_de_supercarburants['annee'] > 0].copy()
    part_des_types_de_supercarburants['annee'] = part_des_types_de_supercarburants['annee'].astype(int)
    part_des_types_de_supercarburants = part_des_types_de_supercarburants.set_index('annee')

    # delete share of e_85 because we have no data for its price
    # When the sum of all shares is not one, need to multiply each share by the same coefficient
    cols = part_des_types_de_supercarburants.columns
    for element in cols:
        part_des_types_de_supercarburants[element] = (
            part_des_types_de_supercarburants[element]
            / (part_des_types_de_supercarburants['somme'] - part_des_types_de_supercarburants['sp_e85'])
            )
    del part_des_types_de_supercarburants['sp_e85']
    del part_des_types_de_supercarburants['somme']
    cols = part_des_types_de_supercarburants.columns
    part_des_types_de_supercarburants['somme'] = 0
    for element in cols:
        part_des_types_de_supercarburants['somme'] += part_des_types_de_supercarburants[element]
    assert (part_des_types_de_supercarburants['somme'] == 1).any(), "The weighting of the shares did not work"

    part_type_supercaburants = {
        "description": "part de la consommation totale d'essence de chaque type supercarburant",
        }
    for element in ['super_plombe', 'sp_95', 'sp_98', 'sp_e10']:
        part_par_carburant = part_des_types_de_supercarburants[element]
        years = list(range(2000, 2017))
        years = sorted(years, key=int, reverse=True)
        values = dict()
        for year in years:
            values['{}-01-01'.format(year)] = part_par_carburant[year]

        part_type_supercaburants[element] = {
            "description": "part de " + element + " dans la consommation totale d'essences",
            "unit": "/1",
            "values": values
            }

    node_part_type_supercaburants = ParameterNode(
        'part_type_supercaburants',
        data = part_type_supercaburants,
        )
    parameters.children['imposition_indirecte'].add_child('part_type_supercarburants', node_part_type_supercaburants)
    return parameters
    # Add CO2 emissions from energy (Source : Ademe)
    emissions_CO2 = {
        "@type": "Node",
        "description": "émissions de CO2 des énergies",
        "children": {},
        }
    emissions_CO2['children']['carburants'] = {
        "@type": "Node",
        "description": "émissions de CO2 des carburants",
        "children": {
            "CO2_diesel": {
                "@type": "Parameter",
                "description": "émissions de CO2 du diesel en kg par litre",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 2.66},
                    ],
                },
            "CO2_essence": {
                "@type": "Parameter",
                "description": "émissions de CO2 du diesel en kg par litre",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 2.42},
                    ],
                },
            },
        }

    emissions_CO2['children']['energie_logement'] = {
        "@type": "Node",
        "description": "émissions de CO2 de l'énergie dans le logement",
        "children": {
            "CO2_electricite": {
                "@type": "Parameter",
                "description": "émissions de CO2 de l'électricité, en kg par kWh",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 0.09},
                    ],
                },
            "CO2_gaz_ville": {
                "@type": "Parameter",
                "description": "émissions de CO2 du gaz, en kg par kWh",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 0.241},
                    ],
                },
            "CO2_gaz_liquefie": {
                "@type": "Parameter",
                "description": "émissions de CO2 du gaz, en kg par kWh",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 0.253},
                    ],
                },
            "CO2_combustibles_liquides": {
                "@type": "Parameter",
                "description": "émissions de CO2 des combustibles liquides, en kg par litre",
                "format": "float",
                "values": [
                    {'start': '1990-01-01', 'value': 3.24},
                    ],
                },
            },
        }

    legislation_json['children']['imposition_indirecte']['children']['emissions_CO2'] = emissions_CO2

    # Add data from comptabilite national about alcohol

    alcool_conso_et_vin = {
        "@type": "Node",
        "description": "alcools",
        "children": {},
        }
    alcool_conso_et_vin['children']['vin'] = {
        "@type": "Node",
        "description": "Pour calculer le taux de taxation implicite sur le vin",
        "children": {
            "droit_cn_vin": {
                "@type": "Parameter",
                "description": "Masse droit vin, vin mousseux, cidres et poirés selon comptabilité nationale",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 122},
                    {'start': '2012-01-01', 'value': 120},
                    {'start': '2011-01-01', 'value': 118},
                    {'start': '2010-01-01', 'value': 119},
                    {'start': '2009-01-01', 'value': 117},
                    {'start': '2008-01-01', 'value': 114},
                    {'start': '2007-01-01', 'value': 117},
                    {'start': '2006-01-01', 'value': 119},
                    {'start': '2005-01-01', 'value': 117},
                    {'start': '2004-01-01', 'value': 125},
                    {'start': '2003-01-01', 'value': 127},
                    {'start': '2002-01-01', 'value': 127},
                    {'start': '2001-01-01', 'value': 127},
                    {'start': '2000-01-01', 'value': 127},
                    {'start': '1999-01-01', 'value': 133},
                    {'start': '1998-01-01', 'value': 132},
                    {'start': '1997-01-01', 'value': 129},
                    {'start': '1996-01-01', 'value': 130},
                    {'start': '1995-01-01', 'value': 129},
                    # {'start': u'2014-01-01', 'value': },
                    ],
                },
            "masse_conso_cn_vin": {
                "@type": "Parameter",
                "description": "Masse consommation vin, vin mousseux, cidres et poirés selon comptabilité nationale",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 11515},
                    {'start': '2012-01-01', 'value': 11407},
                    {'start': '2011-01-01', 'value': 11387},
                    {'start': '2010-01-01', 'value': 11002},
                    {'start': '2009-01-01', 'value': 10728},
                    {'start': '2008-01-01', 'value': 10461},
                    {'start': '2007-01-01', 'value': 10345},
                    {'start': '2006-01-01', 'value': 10002},
                    {'start': '2005-01-01', 'value': 9933},
                    {'start': '2004-01-01', 'value': 9985},
                    {'start': '2003-01-01', 'value': 9695},
                    {'start': '2002-01-01', 'value': 9476},
                    {'start': '2001-01-01', 'value': 9168},
                    {'start': '2000-01-01', 'value': 8854},
                    {'start': '1999-01-01', 'value': 8451},
                    {'start': '1998-01-01', 'value': 8025},
                    {'start': '1997-01-01', 'value': 7636},
                    {'start': '1996-01-01', 'value': 7419},
                    {'start': '1995-01-01', 'value': 7191},
                    # {'start': u'2014-01-01', 'value': },
                    ],
                },
            },
        }

    alcool_conso_et_vin['children']['biere'] = {
        "@type": "Node",
        "description": "Pour calculer le taux de taxation implicite sur la bière",
        "children": {
            "droit_cn_biere": {
                "@type": "Parameter",
                "description": "Masse droit biere selon comptabilité nationale",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 897},
                    {'start': '2012-01-01', 'value': 783},
                    {'start': '2011-01-01', 'value': 393},
                    {'start': '2010-01-01', 'value': 375},
                    {'start': '2008-01-01', 'value': 375},
                    {'start': '2009-01-01', 'value': 376},
                    {'start': '2007-01-01', 'value': 382},
                    {'start': '2006-01-01', 'value': 396},
                    {'start': '2005-01-01', 'value': 364},
                    {'start': '2004-01-01', 'value': 378},
                    {'start': '2003-01-01', 'value': 370},
                    {'start': '2002-01-01', 'value': 361},
                    {'start': '2001-01-01', 'value': 364},
                    {'start': '2000-01-01', 'value': 359},
                    {'start': '1999-01-01', 'value': 380},
                    {'start': '1998-01-01', 'value': 365},
                    {'start': '1997-01-01', 'value': 364},
                    {'start': '1996-01-01', 'value': 366},
                    {'start': '1995-01-01', 'value': 361},
                    # {'start': u'2014-01-01', 'value': },
                    ],
                },
            "masse_conso_cn_biere": {
                "@type": "Parameter",
                "description": "Masse consommation biere selon comptabilité nationale",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 3321},
                    {'start': '2012-01-01', 'value': 2868},
                    {'start': '2011-01-01', 'value': 2769},
                    {'start': '2010-01-01', 'value': 2461},
                    {'start': '2009-01-01', 'value': 2375},
                    {'start': '2008-01-01', 'value': 2287},
                    {'start': '2007-01-01', 'value': 2458},
                    {'start': '2006-01-01', 'value': 2486},
                    {'start': '2005-01-01', 'value': 2466},
                    {'start': '2004-01-01', 'value': 2484},
                    {'start': '2003-01-01', 'value': 2554},
                    {'start': '2002-01-01', 'value': 2405},
                    {'start': '2001-01-01', 'value': 2327},
                    {'start': '2000-01-01', 'value': 2290},
                    {'start': '1999-01-01', 'value': 2334},
                    {'start': '1998-01-01', 'value': 2291},
                    {'start': '1997-01-01', 'value': 2186},
                    {'start': '1996-01-01', 'value': 2144},
                    {'start': '1995-01-01', 'value': 2111},
                    # {'start': u'2014-01-01', 'value': },
                    ],
                },
            },
        }

    alcool_conso_et_vin['children']['alcools_forts'] = {
        "@type": "Node",
        "description": "Pour calculer le taux de taxation implicite sur alcools forts",
        "children": {
            "droit_cn_alcools": {
                "@type": "Parameter",
                "description": "Masse droit alcool selon comptabilité nationale sans droits sur les produits intermediaires et cotisation spéciale alcool fort",
                "format": "float",
                "values": [
                    {'start': '2012-01-01', 'value': 2225},
                    {'start': '2011-01-01', 'value': 2150},
                    {'start': '2010-01-01', 'value': 2111},
                    {'start': '2009-01-01', 'value': 2031},
                    {'start': '2008-01-01', 'value': 2005},
                    {'start': '2007-01-01', 'value': 1990},
                    {'start': '2006-01-01', 'value': 1954},
                    {'start': '2005-01-01', 'value': 1842},
                    {'start': '2004-01-01', 'value': 1908},
                    {'start': '2003-01-01', 'value': 1891},
                    {'start': '2002-01-01', 'value': 1932},
                    {'start': '2001-01-01', 'value': 1957},
                    {'start': '2000-01-01', 'value': 1872},
                    # TODO: Problème pour les alcools forts chiffres différents entre les deux bases excel !
                    ],
                },
            "droit_cn_alcools_total": {
                "@type": "Parameter",
                "description": "Masse droit alcool selon comptabilité nationale avec les differents droits",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 3022},
                    {'start': '2012-01-01', 'value': 2718},
                    {'start': '2011-01-01', 'value': 3078},
                    {'start': '2010-01-01', 'value': 2734},
                    {'start': '2009-01-01', 'value': 2629},
                    {'start': '2008-01-01', 'value': 2528},
                    {'start': '2007-01-01', 'value': 2516},
                    {'start': '2006-01-01', 'value': 2477},
                    {'start': '2005-01-01', 'value': 2352},
                    {'start': '2004-01-01', 'value': 2409},
                    {'start': '2003-01-01', 'value': 2453},
                    {'start': '2002-01-01', 'value': 2503},
                    {'start': '2000-01-01', 'value': 2416},
                    {'start': '2001-01-01', 'value': 2514},
                    {'start': '1999-01-01', 'value': 2385},
                    {'start': '1998-01-01', 'value': 2369},
                    {'start': '1997-01-01', 'value': 2366},
                    {'start': '1996-01-01', 'value': 2350},
                    {'start': '1995-01-01', 'value': 2337},
                    # {'start': u'2014-01-01', 'value': },
                    ],
                },
            "masse_conso_cn_alcools": {
                "@type": "Parameter",
                "description": "Masse consommation alcool selon comptabilité nationale",
                "format": "float",
                "values": [
                    {'start': '2013-01-01', 'value': 7022},
                    {'start': '2012-01-01', 'value': 6996},
                    {'start': '2011-01-01', 'value': 6680},
                    {'start': '2010-01-01', 'value': 6618},
                    {'start': '2009-01-01', 'value': 6342},
                    {'start': '2008-01-01', 'value': 6147},
                    {'start': '2007-01-01', 'value': 6142},
                    {'start': '2006-01-01', 'value': 6106},
                    {'start': '2005-01-01', 'value': 5960},
                    {'start': '2004-01-01', 'value': 5967},
                    {'start': '2003-01-01', 'value': 5895},
                    {'start': '2002-01-01', 'value': 5932},
                    {'start': '2001-01-01', 'value': 5721},
                    {'start': '2000-01-01', 'value': 5558},
                    {'start': '1999-01-01', 'value': 5234},
                    {'start': '1998-01-01', 'value': 5123},
                    {'start': '1997-01-01', 'value': 5065},
                    {'start': '1996-01-01', 'value': 5075},
                    {'start': '1995-01-01', 'value': 4893},
                    ],
                },
            },
        }

    legislation_json['children']['imposition_indirecte']['children']['alcool_conso_et_vin'] = alcool_conso_et_vin

    # Make the change from francs to euros for excise taxes in ticpe
    keys_ticpe = list(legislation_json['children']['imposition_indirecte']['children']['ticpe']['children'].keys())
    for element in keys_ticpe:
        get_values = \
            legislation_json['children']['imposition_indirecte']['children']['ticpe']['children'][element]['values']
        for each_value in get_values:
            get_character = '{}'.format(each_value['start'])
            year = int(get_character[:4])
            if year < 2002:
                each_value['value'] = each_value['value'] / 6.55957
            else:
                each_value['value'] = each_value['value']

    return legislation_json
