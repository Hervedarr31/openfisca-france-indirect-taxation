import numpy


from openfisca_core.parameters import ParameterNotFound
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore
from openfisca_france_indirect_taxation.variables.consommation.depenses_energies import TypesContratGaz


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
            assert prix_fioul_ttc_reference is not None
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


class depenses_gaz_ville(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz après éventuelle réponse comportementale"

    def formula(menage, period, parameters):
        depenses_gaz_variables = menage('depenses_gaz_variables', period)
        depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
        depenses_gaz_contrat = menage('depenses_gaz_contrat', period)

        try:
            prix_unitaire_gdf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc
            delta_prix_unitaire_gdf_kwh_ttc = select(
                [
                    depenses_gaz_contrat == TypesContratGaz.aucun,
                    depenses_gaz_contrat == TypesContratGaz.base,
                    depenses_gaz_contrat == TypesContratGaz.b0,
                    depenses_gaz_contrat == TypesContratGaz.b1,
                    depenses_gaz_contrat == TypesContratGaz.b2i,
                    ],
                [
                    0,
                    prix_unitaire_gdf_ttc.prix_kwh_base_ttc - prix_unitaire_gdf_ttc.prix_kwh_base_ttc_reference,
                    prix_unitaire_gdf_ttc.prix_kwh_b0_ttc - prix_unitaire_gdf_ttc.prix_kwh_b0_ttc_reference,
                    prix_unitaire_gdf_ttc.prix_kwh_b1_ttc - prix_unitaire_gdf_ttc.prix_kwh_b1_ttc_reference,
                    prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc - prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc_reference,
                    ]
                )
            assert prix_unitaire_gdf_ttc.prix_kwh_base_ttc_reference is not None
            assert prix_unitaire_gdf_ttc.prix_kwh_b0_ttc_reference is not None
            assert prix_unitaire_gdf_ttc.prix_kwh_b1_ttc_reference is not None
            assert prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc_reference is not None

        except ParameterNotFound:
            delta_prix_unitaire_gdf_kwh_ttc = None

        depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)

        if delta_prix_unitaire_gdf_kwh_ttc is not None:
            gaz_elasticite_prix = menage('elas_price_2_2', period)
            depenses_gaz_ajustees_variables = select(
                [
                    depenses_gaz_contrat == TypesContratGaz.aucun,
                    depenses_gaz_contrat != TypesContratGaz.aucun,
                    ],
                [
                    0,
                    depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * delta_prix_unitaire_gdf_kwh_ttc / depenses_gaz_prix_unitaire)
                    ]
                )

            return depenses_gaz_ajustees_variables + depenses_gaz_tarif_fixe

        else:
            return depenses_gaz_variables + depenses_gaz_tarif_fixe


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
