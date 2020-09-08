from openfisca_france_indirect_taxation.variables.base import *


class tva_energie(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Montant de la TVA acquitée sur les produits énergétiques"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        depenses = sum(
            [
                menage(depense, period)
                for depense in [
                    'depenses_carburants',
                    'depenses_combustibles_liquides',
                    'depenses_gaz_ville'
                    ]
                ]
            )
        tva = tax_from_expense_including_tax(depenses, taux_plein_tva)
        return tva
