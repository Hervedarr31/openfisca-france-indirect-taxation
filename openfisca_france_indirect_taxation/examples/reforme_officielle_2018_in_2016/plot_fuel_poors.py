# -*- coding: utf-8 -*-

# Import general modules
from __future__ import division

import pandas as pd
import seaborn

# Import modules specific to OpenFisca
from openfisca_france_indirect_taxation.surveys import SurveyScenario
from openfisca_france_indirect_taxation.almost_ideal_demand_system.aids_estimation_from_stata import get_elasticities
from openfisca_france_indirect_taxation.examples.calage_bdf_cn_energy import get_inflators_by_year_energy
from openfisca_france_indirect_taxation.examples.reforme_officielle_2018_in_2016.number_fuel_poor import number_fuel_poors
from openfisca_france_indirect_taxation.examples.utils_example import graph_builder_bar_percent, graph_builder_bar

seaborn.set_palette(seaborn.color_palette("Set2", 12))


def plot_effect_reform_fuel_poors():
    types = ['logement', 'transport', 'joint', 'double']
    statuts = [u'avant reforme', u'officielle - officielle', u'officielle - integrale']
    dataframe = pd.DataFrame(index = types, columns=statuts)
    dict_precarite = dict()
    (dict_precarite['logement'], dict_precarite['transport'],
        dict_precarite['double'], dict_precarite['joint']) = \
        number_fuel_poors(year, data_year)
    for type_precarite in types:
        for statut in [u'officielle - officielle', u'officielle - integrale']:
            dataframe[statut][type_precarite] = (
                dict_precarite[type_precarite]['precarite - ' + statut] -
                dict_precarite[type_precarite]['precarite - avant reforme']
                ) / dict_precarite[type_precarite]['precarite - avant reforme']

    graph_builder_bar_percent(dataframe)

    
def plot_number_fuel_poors():
    types = ['logement', 'transport', 'joint', 'double']
    statuts = [u'avant reforme', u'officielle - officielle', u'officielle - integrale']
    dataframe = pd.DataFrame(index = types, columns=statuts)
    dict_precarite = dict()
    (dict_precarite['logement'], dict_precarite['transport'],
        dict_precarite['double'], dict_precarite['joint']) = \
        number_fuel_poors(year, data_year)
    for type_precarite in types:
        for statut in statuts:
            dataframe[statut][type_precarite] = \
                dict_precarite[type_precarite]['precarite - ' + statut]

    graph_builder_bar(dataframe, False)


def plot_share_fuel_poors():
    survey_scenario = SurveyScenario.create(
        elasticities = elasticities,
        inflation_kwargs = inflation_kwargs,
        reform_key = 'officielle_2018_in_2016',
        year = year,
        data_year = data_year
        )

    df_reforme = survey_scenario.create_data_frame_by_entity(['pondmen'], period = year)['menage']
    pop_size = df_reforme['pondmen'].sum()

    types = ['logement', 'transport', 'joint', 'double']
    statuts = [u'avant reforme', u'officielle - officielle', u'officielle - integrale']
    dataframe = pd.DataFrame(index = types, columns=statuts)
    dict_precarite = dict()
    (dict_precarite['logement'], dict_precarite['transport'],
        dict_precarite['double'], dict_precarite['joint']) = \
        number_fuel_poors(year, data_year)
    for type_precarite in types:
        for statut in statuts:
            dataframe[statut][type_precarite] = \
                dict_precarite[type_precarite]['precarite - ' + statut] / pop_size

    graph_builder_bar_percent(dataframe)


if __name__ == '__main__':    
    year = 2016
    data_year = 2011
    inflators_by_year = get_inflators_by_year_energy(rebuild = False)
    elasticities = get_elasticities(data_year)
    inflation_kwargs = dict(inflator_by_variable = inflators_by_year[year])
    
    plot_effect_reform_fuel_poors()
    plot_number_fuel_poors()
    plot_share_fuel_poors()

