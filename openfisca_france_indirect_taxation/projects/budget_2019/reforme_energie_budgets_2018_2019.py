# -*- coding: utf-8 -*-

import numpy

from openfisca_core.parameters import ParameterNotFound
from openfisca_core.reforms import Reform
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore
from openfisca_france_indirect_taxation import FranceIndirectTaxationTaxBenefitSystem
from openfisca_france_indirect_taxation.variables.consommation.depenses_energies import TypesContratGaz
from openfisca_france_indirect_taxation.reforms.reforme_energie_test import build_prix_carburants_reference


def modify_parameters(parameters):
    period = '2017'
    parameters = build_prix_carburants_reference(parameters)

    reference_value = parameters(period).prix_carburants.diesel_ttc_reference
    parameters.prix_carburants.diesel_ttc.update(
        start = period,
        value = reference_value + 1 * 2.6 + 266 * (0.0446 - 0.0305)  # 266 = valeur du contenu carbone du diesel (source : Ademe)
        )

    reference_value = parameters(period).prix_carburants.super_95_ttc_reference
    parameters.prix_carburants.super_95_ttc.update(
        start = period,
        value = reference_value + 242 * (0.0446 - 0.0305)  # 242 = valeur du contenu carbone du diesel (source : Ademe)
        )

    reference_value = \
        parameters(period).tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre_reference
    parameters.tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre.update(
        start = period,
        value = reference_value + 3.24 * (0.0446 - 0.0305)  # (en euros par litre)
        )

    parameters.imposition_indirecte.produits_energetiques.ticpe.gazole_fioul_domestique_hectolitre.update(
        start = period,
        value = (
            parameters(period).imposition_indirecte.produits_energetiques.ticpe.gazole_fioul_domestique_hectolitre
            + 100 * 3.24 * (0.0446 - 0.0305)  # (en euros par litre)
            )
        )

    prix_unitaire_gdf_ttc = parameters.tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc

    for node in [
            prix_unitaire_gdf_ttc.prix_kwh_base_ttc,
            prix_unitaire_gdf_ttc.prix_kwh_b0_ttc,
            prix_unitaire_gdf_ttc.prix_kwh_b1_ttc,
            prix_unitaire_gdf_ttc.prix_kwh_b2i_ttc,
            ]:
        name = node.name.split(".")[-1:][0]
        reference_value = prix_unitaire_gdf_ttc.children[name + '_reference'](period)
        prix_unitaire_gdf_ttc.children[name].update(
            start = period,
            value = reference_value + 0.241 * (0.0446 - 0.0305)  # (en euros par kWh)
            )

    parameters.prestations.add_child(  # Peut être ne lire que le fichier des paramètres et ne pas instancier le TBS
        'cheque_energie_reforme',
        FranceIndirectTaxationTaxBenefitSystem().parameters.prestations.cheque_energie
        )

    return parameters


class officielle_2019_in_2017(Reform):
    key = 'officielle_2019_in_2017',
    name = "Réforme de la fiscalité des énergies de 2018 par rapport aux taux de 2016",

    class cheques_energie(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Montant des chèques énergie tels que prévus par la loi"

        def formula(menage, period, parameters):
            revenu_fiscal = max_(0.0, menage('revdecm', period) / 1.22)
            ocde10 = menage('ocde10', period)
            revenu_fiscal_uc = revenu_fiscal / ocde10
            bareme_cheque_energie_reforme = parameters(period).prestations.cheque_energie_reforme

            return select(
                [
                    (ocde10 == 1),
                    ((ocde10 > 1) * (ocde10 < 2)),
                    (ocde10 >= 2),
                    ],
                [
                    bareme_cheque_energie_reforme.menage_avec_1_uc.calc(revenu_fiscal_uc),
                    bareme_cheque_energie_reforme.menage_entre_1_et_2_uc.calc(revenu_fiscal_uc),
                    bareme_cheque_energie_reforme.menage_avec_2_uc_et_plus.calc(revenu_fiscal_uc),
                    ],
                default = 0.0
                )

    class combustibles_liquides_ticpe(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Calcul du montant de TICPE sur le combustibles_liquides domestique après réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

            accise_combustibles_liquides_ticpe = (
                parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.gazole_fioul_domestique_hectolitre / 100
                )
            reforme_combustibles_liquides = \
                parameters(period.start).officielle_2019_in_2017.combustibles_liquides_2019_in_2017
            accise_combustibles_liquides_ajustee = accise_combustibles_liquides_ticpe + reforme_combustibles_liquides
            prix_fioul_ttc = \
                parameters(period.start).tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre
            prix_fioul_ttc_ajuste = prix_fioul_ttc + reforme_combustibles_liquides

            taux_implicite_combustibles_liquides_ajuste = (
                (accise_combustibles_liquides_ajustee * (1 + taux_plein_tva))
                / (prix_fioul_ttc_ajuste - accise_combustibles_liquides_ajustee * (1 + taux_plein_tva))
                )

            depenses_combustibles_liquides_ajustees = menage('depenses_combustibles_liquides', period)
            depenses_combustibles_liquides_htva = \
                depenses_combustibles_liquides_ajustees - tax_from_expense_including_tax(depenses_combustibles_liquides_ajustees, taux_plein_tva)
            montant_combustibles_liquides_ticpe_ajuste = \
                tax_from_expense_including_tax(depenses_combustibles_liquides_htva, taux_implicite_combustibles_liquides_ajuste)

            return montant_combustibles_liquides_ticpe_ajuste


    class depenses_energies_logement(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en énergies dans le logement après PLF 2019"

        def formula(menage, period):
            return (
                menage('depenses_combustibles_liquides', period)
                + menage('depenses_combustibles_solides', period)
                + menage('depenses_electricite', period)
                + menage('depenses_energie_thermique', period)
                + menage('depenses_gaz_liquefie', period)
                + menage('depenses_gaz_ville', period)
                + menage('tarifs_sociaux_electricite', period)
                )


    class depenses_gaz_ville(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en gaz après réaction à la réforme - taxe carbone"

        def formula(menage, period, parameters):
            depenses_gaz_variables = menage('depenses_gaz_variables', period)
            # Avec la réforme ces tarifs disparaissent, de nouvelles consommations entrent dans les dépenses des ménages :
            # tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)
            # TODO comme ils diparaissent et que l'on veut les reverser dans depenses_gaz_variables il faut le faire
            # seulement pour la réforme dans l'initialisation du TBS (custom_initialize)
            # depenses_gaz_variables = depenses_gaz_variables + tarifs_sociaux_gaz
            depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)  # TODO rapatrier ici ce contenu de la variable depenses_gaz_prix_unitaire
            depenses_gaz_contrat = menage('depenses_gaz_contrat', period)
            prix_unitaire_gdf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc
            delta_prix_unitaire_gdf_kwh_ttc = select(
                [
                    depenses_gaz_contrat == TypesContratGaz.base,
                    depenses_gaz_contrat == TypesContratGaz.b0,
                    depenses_gaz_contrat == TypesContratGaz.b1,
                    depenses_gaz_contrat == TypesContratGaz.b2i,
                    ],
                [
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
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)

            gaz_elasticite_prix = menage('elas_price_2_2', period)
            depenses_gaz_ajustees_variables = \
                depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * delta_prix_unitaire_gdf_kwh_ttc / depenses_gaz_prix_unitaire)

            depenses_gaz_ajustees = depenses_gaz_ajustees_variables
            depenses_gaz_ajustees[numpy.isnan(depenses_gaz_ajustees)] = 0
            depenses_gaz_ajustees[numpy.isinf(depenses_gaz_ajustees)] = 0
            return depenses_gaz_ajustees  + depenses_gaz_tarif_fixe


    # TODO: doit être inclus dans la différence de TVA
    # class gains_tva_carburants_officielle_2019_in_2017(YearlyVariable):
    #     value_type = float
    #     entity = Menage
    #     label = "Recettes en TVA sur les carburants de la réforme"

    #     def formula(menage, period, parameters):
    #         taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
    #         depenses_carburants_corrigees_officielle_2019_in_2017 = \
    #             menage('depenses_carburants', period)
    #         tva_depenses_carburants_corrigees_officielle_2019_in_2017 = (
    #             (taux_plein_tva / (1 + taux_plein_tva))
    #             * depenses_carburants_corrigees_officielle_2019_in_2017
    #             )
    #         depenses_carburants_corrigees = \
    #             menage('poste_carburants', period)
    #         tva_depenses_carburants_corrigees = (
    #             (taux_plein_tva / (1 + taux_plein_tva))
    #             * depenses_carburants_corrigees
    #             )
    #         gains_tva_carburants = (
    #             tva_depenses_carburants_corrigees_officielle_2019_in_2017
    #             - tva_depenses_carburants_corrigees
    #             )
    #         return gains_tva_carburants

    # TODO: doit être inclus dans la différence de TVA
    # class gains_tva_combustibles_liquides_officielle_2019_in_2017(YearlyVariable):
    #     value_type = float
    #     entity = Menage
    #     label = "Recettes de la réforme en TVA sur les combustibles liquides"

    #     def formula(menage, period, parameters):
    #         taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
    #         depenses_combustibles_liquides_officielle_2019_in_2017 = \
    #             menage('depenses_combustibles_liquides', period)
    #         tva_depenses_combustibles_liquides_officielle_2019_in_2017 = (
    #             (taux_plein_tva / (1 + taux_plein_tva))
    #             * depenses_combustibles_liquides_officielle_2019_in_2017
    #             )
    #         depenses_combustibles_liquides = \
    #             menage('poste_combustibles_liquides', period)
    #         tva_depenses_combustibles_liquides = (
    #             (taux_plein_tva / (1 + taux_plein_tva))
    #             * depenses_combustibles_liquides
    #             )
    #         gains_tva_combustibles_liquides = (
    #             tva_depenses_combustibles_liquides_officielle_2019_in_2017
    #             - tva_depenses_combustibles_liquides
    #             )
    #         return gains_tva_combustibles_liquides

    class gains_tva_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur le gaz naturel"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_ville = \
                menage('depenses_gaz_ville', period)
            tva_depenses_gaz_ville_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * (depenses_gaz_ville_officielle_2019_in_2017 - depenses_gaz_tarif_fixe)
                )
            depenses_gaz_ville = \
                menage('depenses_gaz_ville', period)
            tva_depenses_gaz_ville = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * (depenses_gaz_ville - depenses_gaz_tarif_fixe)
                )
            gains_tva_gaz_ville = (
                tva_depenses_gaz_ville_officielle_2019_in_2017
                - tva_depenses_gaz_ville
                )
            return gains_tva_gaz_ville

    # class gains_tva_total_energies_officielle_2019_in_2017(YearlyVariable):
    #     value_type = float
    #     entity = Menage
    #     label = "Recettes de la réforme en TVA sur toutes les énergies"

    #     def formula(menage, period):
    #         gains_carburants = menage('gains_tva_carburants_officielle_2019_in_2017', period)
    #         gains_combustibles_liquides = menage('gains_tva_combustibles_liquides_officielle_2019_in_2017', period)
    #         gains_gaz_ville = menage('gains_tva_gaz_ville_officielle_2019_in_2017', period)

    #         somme_gains = gains_carburants + gains_combustibles_liquides + gains_gaz_ville
    #         return somme_gains


    # class revenu_reforme_officielle_2019_in_2017(YearlyVariable):
    #     value_type = float
    #     entity = Menage
    #     label = "Revenu généré par la réforme officielle 2018 avant redistribution"

    #     def formula(menage, period):
    #         total_taxes_energies = menage('total_taxes_energies', period)
    #         total_taxes_energies_officielle_2019_in_2017 = \
    #             menage('total_taxes_energies_officielle_2019_in_2017', period)
    #         gains_tva_total_energies = menage('gains_tva_total_energies_officielle_2019_in_2017', period)
    #         tarifs_sociaux_electricite = menage('tarifs_sociaux_electricite', period)
    #         tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)

    #         revenu_reforme = (
    #             total_taxes_energies_officielle_2019_in_2017 - total_taxes_energies
    #             + gains_tva_total_energies + tarifs_sociaux_electricite + tarifs_sociaux_gaz
    #             )

    #         return revenu_reforme


    class taxe_gaz_ville_additionnelle(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la taxe sur la consommation de gaz - ceteris paribus"
        # On considère que les contributions sur les taxes précédentes ne sont pas affectées

        def formula(menage, period, parameters):
            quantites_gaz_ajustees = menage('quantites_gaz', period)
            prix_unitaire_gdf_ttc = (
                parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc
                )
            reforme_gaz = (
                prix_unitaire_gdf_ttc.prix_kwh_base_ttc
                - prix_unitaire_gdf_ttc.prix_kwh_base_ttc_reference
                )
            recettes_gaz = quantites_gaz_ajustees * reforme_gaz
            return recettes_gaz

    class total_taxes_energies(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Contributions aux taxes sur l'énergie après la réforme PLF"

        def formula(menage, period):
            essence_ticpe = menage('essence_ticpe', period)
            diesel_ticpe = menage('diesel_ticpe', period)
            combustibles_liquides_ticpe = menage('combustibles_liquides_ticpe', period)
            taxe_gaz_ville_additionnelle = menage('taxe_gaz_ville_additionnelle', period)
            return diesel_ticpe + essence_ticpe + combustibles_liquides_ticpe + taxe_gaz_ville_additionnelle

    def apply(self):
        self.neutralize_variable("tarifs_sociaux_gaz")
        self.neutralize_variable("tarifs_sociaux_electricite")
        self.update_variable(self.cheques_energie)
        self.update_variable(self.depenses_energies_logement)
        # self.update_variable(self.gains_tva_carburants_officielle_2019_in_2017)
        # self.update_variable(self.gains_tva_combustibles_liquides_officielle_2019_in_2017)
        # self.update_variable(self.gains_tva_gaz_ville_officielle_2019_in_2017)
        # self.update_variable(self.gains_tva_total_energies_officielle_2019_in_2017)
        # self.update_variable(self.quantites_gaz_final_officielle_2019_in_2017)
        # self.update_variable(self.revenu_reforme_officielle_2019_in_2017)
        self.update_variable(self.depenses_gaz_ville)
        self.update_variable(self.taxe_gaz_ville_additionnelle)
        self.update_variable(self.total_taxes_energies)
        self.modify_parameters(modifier_function = modify_parameters)
