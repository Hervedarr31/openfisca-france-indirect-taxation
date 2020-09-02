import logging


from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


log = logging.getLogger(__name__)


class depenses_energies_totales(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité sans inclure dépenses jointes avec le gaz"

    def formula(menage, period):
        depenses_energies_logement = menage('depenses_energies_logement', period)
        depenses_carburants = menage('depenses_carburants', period)
        depenses_energies_totales = (
            depenses_carburants
            + depenses_energies_logement
            )

        return depenses_energies_totales


class combustibles_liquides(YearlyVariable):
    value_type = float
    entity = Menage
    label = "=1 si le menage consomme des combustibles liquides"

    def formula(menage, period):
        depenses_combustibles_liquides = menage('depenses_combustibles_liquides', period)
        combustibles_liquides = 1 * (depenses_combustibles_liquides > 0)

        return combustibles_liquides


class electricite(YearlyVariable):
    value_type = float
    entity = Menage
    label = "=1 si le menage consomme de l'électricité"

    def formula(menage, period):
        depenses_electricite = menage('depenses_electricite', period)
        electricite = 1 * (depenses_electricite > 0)

        return electricite


class gaz_ville(YearlyVariable):
    value_type = float
    entity = Menage
    label = "=1 si le menage consomme du gaz"

    def formula(menage, period):
        depenses_gaz_ville = menage('depenses_gaz_ville', period)
        gaz_ville = 1 * (depenses_gaz_ville > 0)

        return gaz_ville
