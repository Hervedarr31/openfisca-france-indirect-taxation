import numpy as np


from openfisca_core.parameters import ParameterNotFound
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


class TypesContratGaz(Enum):
    __order__ = 'aucun base b0 b1 b2i'
    aucun = "aucun"
    base = "base"
    b0 = "b0"
    b1 = "b1"
    b2i = "b2i"


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


class depenses_combustibles_solides(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en combustibles solides"

    def formula(menage, period):
        depenses_combustibles_solides = menage('poste_04_5_4_1_1', period)
        return depenses_combustibles_solides


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


class depenses_electricite(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité totale après imputation factures jointes"

    def formula(menage, period):
        depenses_electricite_seule = menage('depenses_electricite_seule', period)
        depenses_electricite_factures_jointes = menage('depenses_electricite_factures_jointes', period)
        depenses_electricite = depenses_electricite_seule + depenses_electricite_factures_jointes
        return depenses_electricite


class depenses_electricite_factures_jointes(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité estimées des factures jointes électricité et gaz"

    def formula(menage, period):
        depenses_factures_jointes = menage('poste_04_5_1_1_1_a', period)
        depenses_electricite_seule = menage('depenses_electricite_seule', period)
        poste_gaz_seul = menage('poste_gaz_seul', period)
        consomme_gaz_et_electricte_separement = (
            (depenses_electricite_seule > 0) & (poste_gaz_seul > 0)
            )
        moyenne_electricite = np.mean(depenses_electricite_seule * consomme_gaz_et_electricte_separement)
        moyenne_gaz = np.mean(poste_gaz_seul * consomme_gaz_et_electricte_separement)
        part_electricite = where(
            moyenne_electricite + moyenne_gaz > 0,
            moyenne_electricite / (moyenne_electricite + moyenne_gaz),
            0,
            )
        depenses_electricite_factures_jointes = depenses_factures_jointes * part_electricite
        return depenses_electricite_factures_jointes


class depenses_electricite_percentile(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Classement par percentile des dépenses d'électricité"

    def formula(menage, period):
        depenses_electricite = menage('depenses_electricite', period)
        depenses_electricite_rank = depenses_electricite.argsort().argsort()
        depenses_electricite_percentile = depenses_electricite_rank / len(depenses_electricite_rank) * 100

        return depenses_electricite_percentile


class depenses_electricite_prix_unitaire(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Prix unitaire de l'électricité de chaque ménage, après affectation d'un compteur"

    def formula(menage, period, parameters):
        depenses_electricite_percentile = menage('depenses_electricite_percentile', period)

        # Note : les barèmes ne donnent que les prix unitaires pour 3 et 6 kva. Pour les puissances supérieures,
        # les valeurs sont assez proches de celles du compteur 6kva que nous utilisons comme proxy.
        prix_unitaire_base_edf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_edf.prix_unitaire_base_edf_ttc
        prix_unitaire_3kva = prix_unitaire_base_edf_ttc.prix_kwh_3_kva
        prix_unitaire_6kva = prix_unitaire_base_edf_ttc.prix_kwh_6_kva
        prix_unitaire = (
            (depenses_electricite_percentile < 4) * prix_unitaire_3kva
            + (depenses_electricite_percentile > 4) * prix_unitaire_6kva
            )

        return prix_unitaire


class depenses_electricite_seule(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité sans inclure dépenses jointes avec le gaz"

    def formula(menage, period):
        return menage('poste_04_5_1_1_1_b', period)


class depenses_electricite_tarif_fixe(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité des ménages sur le coût fixe de l'abonnement, après affectation d'un compteur"

    def formula(menage, period, parameters):
        depenses_electricite_percentile = menage('depenses_electricite_percentile', period)

        tarif_fixe_3kva = \
            parameters(period.start).tarifs_energie.tarifs_reglementes_edf.tarif_fixe_base_edf_ttc.tarif_fixe_3_kva
        tarif_fixe_6kva = \
            parameters(period.start).tarifs_energie.tarifs_reglementes_edf.tarif_fixe_base_edf_ttc.tarif_fixe_6_kva
        tarif_fixe_9kva = \
            parameters(period.start).tarifs_energie.tarifs_reglementes_edf.tarif_fixe_base_edf_ttc.tarif_fixe_9_kva
        tarif_fixe_12kva = \
            parameters(period.start).tarifs_energie.tarifs_reglementes_edf.tarif_fixe_base_edf_ttc.tarif_fixe_12_kva
        tarif_fixe_15kva = \
            parameters(period.start).tarifs_energie.tarifs_reglementes_edf.tarif_fixe_base_edf_ttc.tarif_fixe_15_kva

        tarif_fixe = (
            (depenses_electricite_percentile < 4) * tarif_fixe_3kva
            + (depenses_electricite_percentile > 4) * (depenses_electricite_percentile < 52) * tarif_fixe_6kva
            + (depenses_electricite_percentile > 52) * (depenses_electricite_percentile < 78) * tarif_fixe_9kva
            + (depenses_electricite_percentile > 78) * (depenses_electricite_percentile < 88) * tarif_fixe_12kva
            + (depenses_electricite_percentile > 88) * tarif_fixe_15kva
            )

        return tarif_fixe


class depenses_electricite_variables(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en électricité des ménages, hors coût fixe de l'abonnement"

    def formula(menage, period):
        depenses_electricite = menage('depenses_electricite', period)
        depenses_electricite_tarif_fixe = menage('depenses_electricite_tarif_fixe', period)
        depenses_electricite_variables = depenses_electricite - depenses_electricite_tarif_fixe
        depenses_electricite_variables = max_(depenses_electricite_variables, 0)
        return depenses_electricite_variables


class depenses_energies_logement(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en énergies dans le logement"

    def formula(menage, period):
        return (
            menage('depenses_combustibles_liquides', period)
            + menage('depenses_combustibles_solides', period)
            + menage('depenses_electricite', period)
            + menage('depenses_energie_thermique', period)
            + menage('depenses_gaz_liquefie', period)
            + menage('depenses_gaz_ville', period)
            )


class depenses_energie_thermique(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en énergie thermique"

    def formula(menage, period):
        return menage('poste_04_5_5_1_1', period)


class depenses_gaz_factures_jointes(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz estimées des factures jointes électricité et gaz"

    def formula(menage, period):
        depenses_factures_jointes = menage('poste_04_5_1_1_1_a', period)
        depenses_electricite_factures_jointes = menage('depenses_electricite_factures_jointes', period)
        depenses_gaz_factures_jointes = depenses_factures_jointes - depenses_electricite_factures_jointes
        return depenses_gaz_factures_jointes


class depenses_gaz_liquefie(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz liquéfié"

    def formula(menage, period):
        depenses_gaz_liquefie = menage('poste_04_5_2_2_1', period)

        return depenses_gaz_liquefie


class depenses_gaz_contrat(YearlyVariable):
    value_type = Enum
    possible_values = TypesContratGaz
    default_value = TypesContratGaz.base
    entity = Menage
    label = "Contrat de gaz"

    def formula(menage, period, parameters):
        tarifs_reglementes_gdf = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf

        poste_gaz_ville = menage('poste_gaz_ville', period)

        tarif_fixe_gaz = tarifs_reglementes_gdf.tarif_fixe_gdf_ttc.base_0_1000
        depenses_sans_part_fixe = poste_gaz_ville - tarif_fixe_gaz
        prix_unitaire_gaz = tarifs_reglementes_gdf.prix_unitaire_gdf_ttc.prix_kwh_base_ttc
        quantite_base = depenses_sans_part_fixe / prix_unitaire_gaz

        tarif_fixe_gaz = tarifs_reglementes_gdf.tarif_fixe_gdf_ttc.b0_1000_6000
        depenses_sans_part_fixe = poste_gaz_ville - tarif_fixe_gaz
        prix_unitaire_gaz = tarifs_reglementes_gdf.prix_unitaire_gdf_ttc.prix_kwh_b0_ttc
        quantite_b0 = depenses_sans_part_fixe / prix_unitaire_gaz

        tarif_fixe_gaz = tarifs_reglementes_gdf.tarif_fixe_gdf_ttc.b1_6_30000
        depenses_sans_part_fixe = poste_gaz_ville - tarif_fixe_gaz
        prix_unitaire_gaz = tarifs_reglementes_gdf.prix_unitaire_gdf_ttc.prix_kwh_b1_ttc
        quantite_b1 = depenses_sans_part_fixe / prix_unitaire_gaz

        tarif_fixe_gaz = tarifs_reglementes_gdf.tarif_fixe_gdf_ttc.b2i_30000
        depenses_sans_part_fixe = poste_gaz_ville - tarif_fixe_gaz
        prix_unitaire_gaz = tarifs_reglementes_gdf.prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc
        quantite_b2i = depenses_sans_part_fixe / prix_unitaire_gaz

        quantite_optimale_base_b0 = max_(quantite_base, quantite_b0)
        quantite_optimale_base_b1 = max_(quantite_optimale_base_b0, quantite_b1)
        quantite_optimale_base_b2i = max_(quantite_optimale_base_b1, quantite_b2i)
        quantite_optimale = max_(quantite_optimale_base_b2i, 0)

        return select(
            [
                poste_gaz_ville == 0,
                quantite_base == quantite_optimale,
                quantite_b0 == quantite_optimale,
                quantite_b1 == quantite_optimale,
                quantite_b2i == quantite_optimale,
                ],
            [
                TypesContratGaz.aucun,
                TypesContratGaz.base,
                TypesContratGaz.b0,
                TypesContratGaz.b1,
                TypesContratGaz.b2i,
                ]
            )


class depenses_gaz_prix_unitaire(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Prix unitaire du gaz rencontré par les ménages"

    def formula(menage, period, parameters):
        depenses_gaz_contrat = menage("depenses_gaz_contrat", period)
        prix_unitaire_gdf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc
        return select(
            [
                depenses_gaz_contrat == TypesContratGaz.aucun,
                depenses_gaz_contrat == TypesContratGaz.base,
                depenses_gaz_contrat == TypesContratGaz.b0,
                depenses_gaz_contrat == TypesContratGaz.b1,
                depenses_gaz_contrat == TypesContratGaz.b2i,
                ],
            [
                0,
                prix_unitaire_gdf_ttc.prix_kwh_base_ttc,
                prix_unitaire_gdf_ttc.prix_kwh_b0_ttc,
                prix_unitaire_gdf_ttc.prix_kwh_b1_ttc,
                prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc,
                ]
            )


class depenses_gaz_tarif_fixe(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz des ménages sur le coût fixe de l'abonnement"

    def formula(menage, period, parameters):
        depenses_gaz_contrat = menage('depenses_gaz_contrat', period)
        tarif_fixe_gdf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.tarif_fixe_gdf_ttc
        tarif_fixe = select(
            [
                depenses_gaz_contrat == TypesContratGaz.aucun,
                depenses_gaz_contrat == TypesContratGaz.base,
                depenses_gaz_contrat == TypesContratGaz.b0,
                depenses_gaz_contrat == TypesContratGaz.b1,
                depenses_gaz_contrat == TypesContratGaz.b2i,
                ],
            [
                0,
                tarif_fixe_gdf_ttc.base_0_1000,
                tarif_fixe_gdf_ttc.b0_1000_6000,
                tarif_fixe_gdf_ttc.b1_6_30000,
                tarif_fixe_gdf_ttc.b2i_30000,
                ]
            )
        return tarif_fixe


class depenses_gaz_variables(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz des ménages, hors coût fixe de l'abonnement"

    def formula(menage, period):
        poste_gaz_ville = menage('poste_gaz_ville', period)
        tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
        depenses_gaz_variables = poste_gaz_ville - tarif_fixe
        depenses_gaz_variables = select(
            [
                depenses_gaz_contrat == TypesContratGaz.aucun,
                depenses_gaz_contrat != TypesContratGaz.aucun,
                ],
            [
                0,
                max_(poste_gaz_ville - tarif_fixe, 0),
                ]
            )
        return depenses_gaz_variables


class poste_combustibles_liquides(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en combustibles liquides"

    def formula(menage, period):
        return menage('poste_04_5_3_1_1', period)


class poste_gaz_seul(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz de ville"

    def formula(menage, period):
        return menage('poste_04_5_2_1_1', period)


class poste_gaz_ville(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz estimées des factures jointes électricité et gaz"

    def formula(menage, period):
        poste_gaz_seul = menage('poste_gaz_seul', period)
        depenses_gaz_factures_jointes = menage('depenses_gaz_factures_jointes', period)
        depenses_gaz_ville = poste_gaz_seul + depenses_gaz_factures_jointes
        return depenses_gaz_ville
