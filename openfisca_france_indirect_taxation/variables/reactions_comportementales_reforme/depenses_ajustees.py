from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


class depenses_electricite_ajustees_taxe_carbone(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité après réaction à la réforme - taxe carbone"

    def formula(menage, period, parameters):
        depenses_electricite_variables = menage('depenses_electricite_variables', period)
        depenses_electricite_prix_unitaire = menage('depenses_electricite_prix_unitaire', period)
        reforme_electricite = parameters(period.start).taxe_carbone.electricite
        electricite_elasticite_prix = menage('elas_price_2_2', period)
        depenses_electricite_ajustees_variables = (
            depenses_electricite_variables
            * (1 + (1 + electricite_elasticite_prix) * reforme_electricite / depenses_electricite_prix_unitaire)
            )
        depenses_electricite_tarif_fixe = menage('depenses_electricite_tarif_fixe', period)
        min_tarif_fixe = depenses_electricite_tarif_fixe.min()
        depenses_electricite_ajustees = depenses_electricite_ajustees_variables + depenses_electricite_tarif_fixe

        # We do not want to input the expenditure of the contract for those who consume nothing
        depenses_elec = menage('depenses_electricite', period)
        depenses_electricite_ajustees = (
            depenses_electricite_ajustees * (depenses_elec > min_tarif_fixe)
            + depenses_elec * (depenses_elec < min_tarif_fixe)
            )

        return depenses_electricite_ajustees
