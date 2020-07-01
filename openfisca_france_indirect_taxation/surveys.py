# -*- coding: utf-8 -*-


import logging
import numpy

from openfisca_survey_manager.scenarios import AbstractSurveyScenario
from openfisca_france_indirect_taxation.utils import get_input_data_frame
from openfisca_france_indirect_taxation import FranceIndirectTaxationTaxBenefitSystem

log = logging.getLogger(__name__)


class SurveyScenario(AbstractSurveyScenario):
    id_variable_by_entity_key = dict(
        menage = 'ident_men',
        )
    filtering_variable_by_entity = None
    role_variable_by_entity_key = dict(
        menage = 'role_menage',
        )

    @classmethod
    def create(cls, calibration_kwargs = None, data_year = None, elasticities = None, inflation_kwargs = None,
            input_data_frame = None, baseline_tax_benefit_system = None, reform = None,
            tax_benefit_system = None, year = None):

        assert year is not None

        if reform is None:
            assert baseline_tax_benefit_system is None, "No need of reference_tax_benefit_system if no reform"
            if tax_benefit_system is None:
                tax_benefit_system = FranceIndirectTaxationTaxBenefitSystem()
        else:
            if baseline_tax_benefit_system is None:
                baseline_tax_benefit_system = FranceIndirectTaxationTaxBenefitSystem()

            tax_benefit_system = reform(baseline_tax_benefit_system)

        if calibration_kwargs is not None:
            assert set(calibration_kwargs.keys()).issubset(set(
                ['target_margins_by_variable', 'parameters', 'total_population']))

        if inflation_kwargs is not None:
            assert set(inflation_kwargs.keys()).issubset(set(['inflator_by_variable', 'target_by_variable']))

        assert data_year is None or input_data_frame is None

        if input_data_frame is None:
            data_year = data_year or year
            input_data_frame = get_input_data_frame(data_year)

        if elasticities is not None:
            assert 'ident_men' in elasticities.columns
            input_data_frame['ident_men'] = input_data_frame.ident_men.astype(numpy.int64)
            input_data_frame = input_data_frame.merge(elasticities, how = "left", on = 'ident_men')
            for col in elasticities.columns:
                assert col in input_data_frame.columns

        survey_scenario = cls()
        survey_scenario.set_tax_benefit_systems(
            tax_benefit_system = tax_benefit_system,
            baseline_tax_benefit_system = baseline_tax_benefit_system
            )
        survey_scenario.used_as_input_variables = set(input_data_frame.columns).intersection(
            set(tax_benefit_system.variables.keys()))
        survey_scenario.year = year
        survey_scenario.data_year = data_year
        data = dict(input_data_frame = input_data_frame)

        survey_scenario.init_from_data(data = data)

        if calibration_kwargs:
            survey_scenario.calibrate(**calibration_kwargs)

        if inflation_kwargs:
            log.debug('inflating for year = {} using {}'.format(year, inflation_kwargs))
            survey_scenario.inflate(period = year, **inflation_kwargs)

        survey_scenario.initialize_weights()
        assert survey_scenario.simulation is not None
        assert survey_scenario.tax_benefit_system is not None

        return survey_scenario

    def custom_initialize(self, simulation):
        """
        Applique des modifications aux simulations
        """

        if self.baseline_simulation is not None:
            use_baseline = simulation == self.baseline_simulation
        else:
            self.baseline_simulation = simulation
            use_baseline = True

        # Cas des réformes de suppression des tarifs_sociaux_gaz
        if not use_baseline:
            period = self.year
            tax_benefit_system = self.simulation.tax_benefit_system
            tarifs_sociaux_gaz_variable = tax_benefit_system.variables['tarifs_sociaux_gaz']
            if (
                tarifs_sociaux_gaz_variable.is_neutralized
                # or (
                #     tarifs_sociaux_gaz_variable.end is not None
                #     and tarifs_sociaux_gaz_variable.end <= self.year
                #     )
                ):

                tarifs_sociaux_gaz_value = self.baseline_simulation.calculate("tarifs_sociaux_gaz", period = period)
                depenses_gaz_variables_value = self.baseline_simulation.calculate("depenses_gaz_variables", period = period)
                simulation.set_input(
                    "depenses_gaz_variables",
                    period,
                    depenses_gaz_variables_value + tarifs_sociaux_gaz_value
                    )

        # TODO traiter les cas de la dispartion en réforme _et_ baseline des tarifs_sociaux


    def initialize_weights(self):
        self.weight_variable_by_entity = dict()
        self.weight_variable_by_entity['menage'] = 'pondmen'
        self.weight_variable_by_entity['individu'] = 'weight_ind'
