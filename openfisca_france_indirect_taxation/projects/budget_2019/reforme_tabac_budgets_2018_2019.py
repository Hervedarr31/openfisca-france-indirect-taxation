from openfisca_core.reforms import Reform
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore
from openfisca_france_indirect_taxation.projects.base import elasticite_tabac


def create_reforme_tabac_budgets_2018_2019(baseline_year = None):

    assert baseline_year is not None

    class reforme_tabac_budgets_2018_2019(Reform):
        key = 'reforme_tabac_budgets_2018_2019',
        name = "Réforme de la fiscalité tabac (tabac à rouler et cigarettes) prévue par les budgets 2018 et 2019",

        def apply(self):
            baseline_depenses_cigarettes = self.baseline.get_variable('depenses_cigarettes')
            formula_depenses_cigarettes = baseline_depenses_cigarettes.get_formula()

            class depenses_cigarettes(Variable):
                value_type = float
                entity = Menage
                definition_period = MONTH
                set_input = set_input_divide_by_period

                def formula(menage, period, parameters):
                    baseline_depenses_cigarettes = formula_depenses_cigarettes(menage, period, parameters)
                    prix_paquet_baseline = parameters("{}-12-31".format(baseline_year)).imposition_indirecte.taxes_tabacs.prix_tabac.prix_paquet_cigarettes
                    prix_paquet_reforme = parameters(period).imposition_indirecte.taxes_tabacs.prix_tabac.prix_paquet_cigarettes
                    depenses_cigarettes = (
                        baseline_depenses_cigarettes
                        * (
                            1 + (1 + elasticite_tabac) * (
                                (prix_paquet_reforme - prix_paquet_baseline) / prix_paquet_baseline
                                )
                            ))

                    return depenses_cigarettes

            baseline_depenses_tabac_a_rouler = self.baseline.get_variable('depenses_tabac_a_rouler')
            formula_depenses_tabac_a_rouler = baseline_depenses_tabac_a_rouler.get_formula()

            class depenses_tabac_a_rouler(Variable):
                value_type = float
                entity = Menage
                definition_period = MONTH
                set_input = set_input_divide_by_period

                def formula(menage, period, parameters):
                    baseline_depenses_tabac_a_rouler = formula_depenses_tabac_a_rouler(menage, period)
                    prix_baseline = parameters("{}-12-31".format(baseline_year)).imposition_indirecte.taxes_tabacs.prix_tabac.prix_bague_tabac
                    prix_reforme = parameters(period).imposition_indirecte.taxes_tabacs.prix_tabac.prix_bague_tabac
                    depenses_tabac_a_rouler = (
                        baseline_depenses_tabac_a_rouler
                        * (
                            1 + (1 + elasticite_tabac) * (
                                (prix_reforme - prix_baseline) / prix_baseline
                                )
                            ))

                    return depenses_tabac_a_rouler

            self.update_variable(depenses_cigarettes)
            self.update_variable(depenses_tabac_a_rouler)

    return reforme_tabac_budgets_2018_2019
