from openfisca_core.parameters import ParameterNotFound
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


class depenses_carburants(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Consommation de carburants"

    def formula(menage, period):
        return menage('depenses_diesel', period) + menage('depenses_essence', period)


class depenses_combustibles_liquides(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en combustibles liquides tenant compte d'une éventuelle réponse à une évolution des prix"

    def formula(menage, period, parameters):
        prix_fioul_domestique = parameters(period.start).tarifs_energie.prix_fioul_domestique
        depenses_combustibles_liquides = menage('poste_combustibles_liquides', period)
        try:
            prix_fioul_ttc_reference = \
                prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre_reference
            assert super_95_ttc_reference is not None
            delta_prix_fioul_ttc = (
                prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre
                - prix_fioul_ttc_reference
                )
        except ParameterNotFound:
            delta_prix_fioul_ttc = None

        if delta_prix_fioul_ttc:
            combustibles_liquides_elasticite_prix = menage('elas_price_2_2', period)
            depenses_combustibles_liquides_ajustees = (
                depenses_combustibles_liquides
                * (1 + (1 + combustibles_liquides_elasticite_prix) * delta_prix_fioul_ttc / prix_fioul_ttc_reference)
                )
            return depenses_combustibles_liquides_ajustees

        else:
            return depenses_combustibles_liquides


class depenses_essence(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence tenant compte d'une éventuelle réponse à une évolution des prix"

    def formula(menage, period, parameters):
        depenses_essence = menage('poste_essence', period)
        try:
            super_95_ttc_reference = parameters(period.start).prix_carburants.super_95_ttc_reference
            assert super_95_ttc_reference is not None
            delta_super_95_ttc = (
                parameters(period.start).prix_carburants.super_95_ttc
                - super_95_ttc_reference
                )
        except ParameterNotFound:
            delta_super_95_ttc = None

        if delta_super_95_ttc:
            carburants_elasticite_prix = menage('elas_price_1_1', period)
            depenses_essence_ajustees = (
                depenses_essence
                * (1 + (1 + carburants_elasticite_prix) * delta_super_95_ttc / super_95_ttc_reference)
                )
            return depenses_essence_ajustees
        else:
            return depenses_essence


class depenses_diesel(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en diesel  tenant compte d'une éventuelle réponse à une évolution des prix"

    def formula(menage, period, parameters):
        depenses_diesel = menage('poste_diesel', period)
        try:
            diesel_ttc_reference = parameters(period.start).prix_carburants.diesel_ttc_reference

            assert diesel_ttc_reference is not None
            delta_diesel_ttc = (
                parameters(period.start).prix_carburants.diesel_ttc
                - diesel_ttc_reference
                )
        except ParameterNotFound:
            delta_diesel_ttc = None

        if delta_diesel_ttc:
            carburants_elasticite_prix = menage('elas_price_1_1', period)
            depenses_diesel_ajustees = (
                depenses_diesel * (1 + (1 + carburants_elasticite_prix) * delta_diesel_ttc / diesel_ttc_reference)
                )
            return depenses_diesel_ajustees
        else:
            return depenses_diesel

# TODO: remove *_taxe_carbone variables ?


class depenses_gaz_ville_ajustees_taxe_carbone(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz après réaction à la réforme - taxe carbone"

    def formula(menage, period, parameters):
        depenses_gaz_variables = menage('depenses_gaz_variables', period)
        depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
        reforme_gaz = parameters(period.start).taxe_carbone.gaz
        gaz_elasticite_prix = menage('elas_price_2_2', period)
        depenses_gaz_ajustees_variables = \
            depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * reforme_gaz / depenses_gaz_prix_unitaire)
        depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
        depenses_gaz_ajustees = depenses_gaz_ajustees_variables + depenses_gaz_tarif_fixe
        depenses_gaz_ajustees[numpy.isnan(depenses_gaz_ajustees)] = 0
        depenses_gaz_ajustees[numpy.isinf(depenses_gaz_ajustees)] = 0

        return depenses_gaz_ajustees


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
