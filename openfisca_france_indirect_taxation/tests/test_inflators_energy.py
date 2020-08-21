

import pandas as pd

from openfisca_france_indirect_taxation.surveys import SurveyScenario
from openfisca_france_indirect_taxation.examples.calage_bdf_cn_energy import get_inflators_by_year_energy


def test_inflators_energy():
    inflators_by_year = get_inflators_by_year_energy(rebuild = False)
    year = 2014
    data_year = 2011
    inflation_kwargs = dict(inflator_by_variable = inflators_by_year[year])

    simulated_variables = [
        'poste_combustibles_liquides',
        'depenses_combustibles_solides',
        'depenses_electricite',
        'depenses_tot',
        'loyer_impute',
        'poste_carburants',
        'rev_disp_loyerimput',
        'rev_disponible',
        ]

    # TODO This variable is bugging 'depenses_gaz'
    # Should have been changed lately

    survey_scenario_data_year = SurveyScenario.create(
        year = data_year,
        data_year = data_year
        )
    df_data_year = survey_scenario_data_year.create_data_frame_by_entity(simulated_variables, period = data_year)['menage']
    print(sorted(inflation_kwargs['inflator_by_variable'].keys()))

    survey_scenario_year = SurveyScenario.create(
        inflation_kwargs = inflation_kwargs,
        year = year,
        data_year = data_year,
        )
    df_year = survey_scenario_year.create_data_frame_by_entity(simulated_variables, period = year)['menage']

    df_compare = pd.DataFrame()
    for variable in simulated_variables:
        origin_aggregate = survey_scenario_data_year.compute_aggregate(variable, period = data_year)
        inflated_aggregate = survey_scenario_year.compute_aggregate(variable, period = year)
        inflator = inflation_kwargs['inflator_by_variable'][variable]
        assert abs(inflated_aggregate / origin_aggregate - inflator) <= 1e-6, "{} : inflator = {}, origin = {}, inflated = {}, inflated/origin = {}".format(
            variable,
            inflator,
            origin_aggregate,
            inflated_aggregate,
            inflated_aggregate / origin_aggregate,
            )
        assert (df_year[variable] != 0).any(), "All null {}".format(variable)
        assert (df_data_year[variable] != 0).any(), "All null {}".format(variable)
        df_data_year[variable + '_inflated'] = (df_data_year[variable] * inflation_kwargs['inflator_by_variable'][variable]).copy()
        df_compare[variable] = (df_data_year[variable + '_inflated'] - df_year[variable]).copy()
        if not max(df_compare[variable].abs()) < 1:
            print("Problem with variabe {}: diff = {}".format(
                variable,
                max(df_compare[variable].abs()),
                ))  # check the difference is less than 1€
