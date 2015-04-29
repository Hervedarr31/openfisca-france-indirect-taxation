# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:42:16 2015

@author: Etienne
"""

# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

from pandas import DataFrame, concat
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


import openfisca_france_indirect_taxation
from openfisca_survey_manager.survey_collections import SurveyCollection


from openfisca_france_data import default_config_files_directory as config_files_directory
from openfisca_france_indirect_taxation.surveys import SurveyScenario


def get_input_data_frame(year):
    openfisca_survey_collection = SurveyCollection.load(
        collection = "openfisca_indirect_taxation", config_files_directory = config_files_directory)
    openfisca_survey = openfisca_survey_collection.get_survey("openfisca_indirect_taxation_data_{}".format(year))
    input_data_frame = openfisca_survey.get_values(table = "input")
    input_data_frame.reset_index(inplace = True)
    return input_data_frame


def simulate_df(var_to_be_simulated, year):
    '''
    Construction de la DataFrame à partir de laquelle sera faite l'analyse des données
    '''
    input_data_frame = get_input_data_frame(year)
    TaxBenefitSystem = openfisca_france_indirect_taxation.init_country()

    tax_benefit_system = TaxBenefitSystem()
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        tax_benefit_system = tax_benefit_system,
        year = year,
        )
    simulation = survey_scenario.new_simulation()
    return DataFrame(
        dict([
            (name, simulation.calculate(name)) for name in var_to_be_simulated

            ])
        )


def wavg(groupe, var):
    '''
    Fonction qui calcule la moyenne pondérée par groupe d'une variable
    '''
    d = groupe[var]
    w = groupe['pondmen']
    return (d * w).sum() / w.sum()


def collapse(dataframe, groupe, var):
    '''
    Pour une variable, fonction qui calcule la moyenne pondérée au sein de chaque groupe.
    '''
    grouped = dataframe.groupby([groupe])
    var_weighted_grouped = grouped.apply(lambda x: wavg(groupe = x, var = var))
    return var_weighted_grouped


def df_weighted_average_grouped(dataframe, groupe, varlist):
    '''
    Agrège les résultats de weighted_average_grouped() en une unique dataframe pour la liste de variable 'varlist'.
    '''
    return DataFrame(
        dict([
            (var, collapse(dataframe, groupe, var)) for var in varlist
            ])
        )

if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)


    # Lite des coicop agrégées en 12 postes
    list_coicop12 = []
    for coicop12_index in range(1, 13):
        list_coicop12.append('coicop12_{}'.format(coicop12_index))
    # Liste des variables que l'on veut simuler
    var_to_be_simulated = [
        'ident_men',
        'pondmen',
        'decuc',
        'age',
        'decile',
        'revtot',
        'somme_coicop12',
        'ocde10',
        'niveau_de_vie',
        'rev_disponible'
        ]
    # Merge des deux listes
    var_to_be_simulated += list_coicop12


#    df2005 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2005)
#    annee = df2005.apply(lambda row: 2005, axis = 1)
#    df2005["year"] = annee

    df2000 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2000)
    annee = df2000.apply(lambda row: 2000, axis = 1)
    df2000["year"] = annee

    df1995 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 1995)
    annee = df1995.apply(lambda row: 1995, axis = 1)
    df1995["year"] = annee

#    df2011 = simulate_df(var_to_be_simulated = var_to_be_simulated, year = 2011)
#    annee = df2011.apply(lambda row: 2011, axis = 1)
#    df2011["year"] = annee

    var_to_concat = list_coicop12 + ['rev_disponible','somme_coicop12']

    Wconcat1995 = df_weighted_average_grouped(dataframe = df1995, groupe = 'year', varlist = var_to_concat)
    Wconcat2000 = df_weighted_average_grouped(dataframe = df2000, groupe = 'year', varlist = var_to_concat)
#    Wconcat2005 = df_weighted_average_grouped(dataframe = df2005, groupe = 'year', varlist = var_to_concat)
#    Wconcat2011 = df_weighted_average_grouped(dataframe = df2011, groupe = 'year', varlist = var_to_concat)

    list_part_coicop12_1995 = []
    Wconcat1995['part_coicop12_{}'.format(4)] = Wconcat1995['coicop12_{}'.format(4)] / Wconcat1995['rev_disponible']
    'list_part_coicop12_{}_1995'.format(4)
    list_part_coicop12_1995.append('part_coicop12_{}'.format(4))

    list_part_coicop12_2000 = []
    Wconcat2000['part_coicop12_{}'.format(4)] = Wconcat2000['coicop12_{}'.format(4)] / Wconcat2000['rev_disponible']
    'list_part_coicop12_{}_2000'.format(4)
    list_part_coicop12_2000.append('part_coicop12_{}'.format(4))

#    list_part_coicop12_2005 = []
#    Wconcat2005['part_coicop12_{}'.format(4)] = Wconcat2005['coicop12_{}'.format(4)] / Wconcat2005['rev_disponible']
#    'list_part_coicop12_{}_2005'.format(4)
#    list_part_coicop12_2005.append('part_coicop12_{}'.format(4))
#
#    list_part_coicop12_2011 = []
#    Wconcat2011['part_coicop12_{}'.format(4)] = Wconcat2011['coicop12_{}'.format(4)] / Wconcat2011['rev_disponible']
#    'list_part_coicop12_{}_2011'.format(4)
#    list_part_coicop12_2011.append('part_coicop12_{}'.format(4))


    df_to_graph = concat([Wconcat1995[list_part_coicop12_1995], Wconcat2000[list_part_coicop12_2000]])#, Wconcat2005[list_part_coicop12_2005], Wconcat2011[list_part_coicop12_2011]])

    df_to_graph.columns = [
        u'Logement, eau, gaz et électricté'
        ]

    axes = df_to_graph.plot(
        kind = 'bar',
        stacked = True,
        color = ['#0000FF']
        )
    plt.axhline(0, color = 'k')

    def percent_formatter(x, pos = 0):
        return '%1.0f%%' % (100 * x)

    axes.yaxis.set_major_formatter(ticker.FuncFormatter(percent_formatter))
    axes.set_xticklabels( ['1995', '2000', '2005', '2011'], rotation=0 ) ;

    axes.legend(
        bbox_to_anchor = (0.85, 1.15),
        )

    plt.show()
    plt.savefig('C:/Users/Etienne/Documents/data/graphe2.eps', format='eps', dpi=1000)
