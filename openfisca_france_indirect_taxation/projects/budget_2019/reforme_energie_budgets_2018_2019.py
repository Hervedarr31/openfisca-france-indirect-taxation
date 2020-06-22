# -*- coding: utf-8 -*-

import numpy

from openfisca_core.reforms import Reform
from openfisca_france_indirect_taxation import FranceIndirectTaxationTaxBenefitSystem
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore
from openfisca_france_indirect_taxation.reforms.reforme_energie_test import build_prix_carburants_reference


def modify_parameters(parameters):
    period = '2016'
    parameters = build_prix_carburants_reference(parameters)

    reference_value = parameters(period).prix_carburants.diesel_ttc_reference
    parameters.prix_carburants.diesel_ttc.update(
        period = period,
        value = reference_value + 1 * 2.6 + 266 * (0.0446 - 0.0305)  # 266 = valeur du contenu carbone du diesel (source : Ademe)
        )

    reference_value = parameters(period).prix_carburants.super_95_ttc_reference
    parameters.prix_carburants.super_95_ttc.update(
        period = period,
        value = reference_value + 242 * (0.0446 - 0.0305)  # 242 = valeur du contenu carbone du diesel (source : Ademe)
        )

    reference_value = \
        parameters(period).tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre_reference
    parameters.tarifs_energie.prix_fioul_domestique.prix_annuel_moyen_fioul_domestique_ttc_livraisons_2000_4999_litres_en_euro_par_litre.update(
        period = period,
        value = reference_value + 3.24 * (0.0446 - 0.0305)  # (en euros par litre)
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
        node.update(
            period = period,
            value = reference_value + 0.241 * (0.0446 - 0.0305)  # (en euros par kWh)
            )
    # # node = ParameterNode(
    # #     'officielle_2019_in_2017',
    # #     data = {
    # #         "description": "officielle_2019_in_2017",
    # #         "diesel_2019_in_2017": {
    # #             "description": "Surcroît de prix du diesel (en euros par hectolitres)",
    # #             "unit": 'currency',
    # #             "values": {'2016-01-01':
    # #             },
    #         # "essence_2019_in_2017": {
    #         #     "description": "Surcroît de prix de l'essence (en euros par hectolitres)",
    #         #     "unit": 'currency',
    #         #     "values": {'2016-01-01': 242 * (0.0446 - 0.0305)},
    #         #     },
    #         "combustibles_liquides_2019_in_2017": {
    #             "description": "Surcroît de prix du fioul domestique (en euros par litre)",
    #             "unit": 'currency',
    #             "values": {'2016-01-01': 3.24 * (0.0446 - 0.0305)},
    #             },
    #         "gaz_ville_2019_in_2017": {
    #             "description": "Surcroît de prix du gaz (en euros par kWh)",
    #             "unit": 'currency',
    #             "values": {'2016-01-01': 0.241 * (0.0446 - 0.0305)},
    #             },
    #         }
    #     )
    # parameters.add_child('officielle_2019_in_2017', node)

    parameters.prestations.add_child(
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
            revenu_fiscal = numpy.maximum(0.0, menage('revdecm', period) / 1.22)
            ocde10 = menage('ocde10', period)
            revenu_fiscal_uc = revenu_fiscal / ocde10
            bareme_cheque_energie_reforme = parameters(period).prestations.cheque_energie_reforme

            return numpy.select(
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

            depenses_combustibles_liquides_ajustees = menage('depenses_combustibles_liquides_officielle_2019_in_2017', period)
            depenses_combustibles_liquides_htva = \
                depenses_combustibles_liquides_ajustees - tax_from_expense_including_tax(depenses_combustibles_liquides_ajustees, taux_plein_tva)
            montant_combustibles_liquides_ticpe_ajuste = \
                tax_from_expense_including_tax(depenses_combustibles_liquides_htva, taux_implicite_combustibles_liquides_ajuste)

            return montant_combustibles_liquides_ticpe_ajuste


    class depenses_energies_logement_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Dépenses en énergies dans le logement après la réforme"

        def formula(menage, period):
            depenses_electricite = menage('depenses_electricite', period)
            tarifs_sociaux_electricite = menage('tarifs_sociaux_electricite', period)
            depenses_gaz_ville_ajustees = menage('depenses_gaz_ville_officielle_2019_in_2017', period)
            depenses_gaz_liquefie = menage('depenses_gaz_liquefie', period)
            depenses_combustibles_liquides_ajustees = menage('depenses_combustibles_liquides_officielle_2019_in_2017', period)
            depenses_combustibles_solides = menage('depenses_combustibles_solides', period)
            depenses_energie_thermique = menage('depenses_energie_thermique', period)
            depenses_energies_logement_officielle_2019_in_2017 = (
                depenses_electricite + tarifs_sociaux_electricite + depenses_gaz_ville_ajustees + depenses_gaz_liquefie
                + depenses_combustibles_liquides_ajustees + depenses_combustibles_solides + depenses_energie_thermique
                )

            return depenses_energies_logement_officielle_2019_in_2017


class depenses_gaz_ville(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en gaz après réaction à la réforme - taxe carbone"

    def formula(menage, period, parameters):
        depenses_gaz_variables = menage('depenses_gaz_variables', period)
        # Avec la réforme ces tarifs disparaissent, de nouvelles consommations entrent dans les dépenses des ménages :
        tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)
        depenses_gaz_variables = depenses_gaz_variables + tarifs_sociaux_gaz
        depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
        depenses_gaz_contrat = menage('depenses_gaz_contrat', period)
        try:
            prix_unitaire_gdf_ttc = parameters(period.start).tarifs_energie.tarifs_reglementes_gdf.prix_unitaire_gdf_ttc
            gaz_prix_unitaire_reference = select(
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
            delta_prix_unitaire_gdf_kwh_ttc = depenses_gaz_prix_unitaire - gaz_prix_unitaire_reference

        except ParameterNotFound:
            delta_prix_unitaire_gdf_kwh_ttc = None

        depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)

        if delta_prix_unitaire_gdf_kwh_ttc is not None:
            gaz_elasticite_prix = menage('elas_price_2_2', period)
            depenses_gaz_ajustees_variables = \
                depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * delta_prix_unitaire_gdf_kwh_ttc / depenses_gaz_prix_unitaire)

            depenses_gaz_ajustees = depenses_gaz_ajustees_variables + depenses_gaz_tarif_fixe

            depenses_gaz_ajustees[numpy.isnan(depenses_gaz_ajustees)] = 0
            depenses_gaz_ajustees[numpy.isinf(depenses_gaz_ajustees)] = 0
            return depenses_gaz_ajustees

        else:
            return depenses_gaz_variables + depenses_gaz_tarif_fixe

    # class depenses_gaz_ville_officielle_2019_in_2017(YearlyVariable):
    #     value_type = float
    #     entity = Menage
    #     label = "Dépenses en gaz après réaction à la réforme"

    #     def formula(menage, period, parameters):
    #         depenses_gaz_variables = menage('depenses_gaz_variables', period)
    #         # Avec la réforme ces tarifs disparaissent, de nouvelles consommations entrent dans les dépenses des ménages :
    #         tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)
    #         depenses_gaz_variables = depenses_gaz_variables + tarifs_sociaux_gaz

    #         depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
    #         reforme_gaz = \
    #             parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017
    #         gaz_elasticite_prix = menage('elas_price_2_2', period)
    #         depenses_gaz_variables = \
    #             depenses_gaz_variables * (1 + (1 + gaz_elasticite_prix) * reforme_gaz / depenses_gaz_prix_unitaire)
    #         depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
    #         depenses_gaz_ajustees = depenses_gaz_variables + depenses_gaz_tarif_fixe
    #         depenses_gaz_ajustees = numpy.array(depenses_gaz_ajustees, dtype = float)
    #         depenses_gaz_ajustees[numpy.isnan(depenses_gaz_ajustees)] = 0
    #         depenses_gaz_ajustees[numpy.isinf(depenses_gaz_ajustees)] = 0

    #         return depenses_gaz_ajustees


    class gains_tva_carburants_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes en TVA sur les carburants de la réforme"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_carburants_corrigees_officielle_2019_in_2017 = \
                menage('depenses_carburants', period)
            tva_depenses_carburants_corrigees_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_carburants_corrigees_officielle_2019_in_2017
                )
            depenses_carburants_corrigees = \
                menage('poste_carburants', period)
            tva_depenses_carburants_corrigees = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_carburants_corrigees
                )
            gains_tva_carburants = (
                tva_depenses_carburants_corrigees_officielle_2019_in_2017
                - tva_depenses_carburants_corrigees
                )
            return gains_tva_carburants

    class gains_tva_combustibles_liquides_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur les combustibles liquides"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_combustibles_liquides_officielle_2019_in_2017 = \
                menage('depenses_combustibles_liquides', period)
            tva_depenses_combustibles_liquides_officielle_2019_in_2017 = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_combustibles_liquides_officielle_2019_in_2017
                )
            depenses_combustibles_liquides = \
                menage('poste_combustibles_liquides', period)
            tva_depenses_combustibles_liquides = (
                (taux_plein_tva / (1 + taux_plein_tva))
                * depenses_combustibles_liquides
                )
            gains_tva_combustibles_liquides = (
                tva_depenses_combustibles_liquides_officielle_2019_in_2017
                - tva_depenses_combustibles_liquides
                )
            return gains_tva_combustibles_liquides

    class gains_tva_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur le gaz naturel"

        def formula(menage, period, parameters):
            taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_ville_officielle_2019_in_2017 = \
                menage('depenses_gaz_ville_officielle_2019_in_2017', period)
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

    class gains_tva_total_energies_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la réforme en TVA sur toutes les énergies"

        def formula(menage, period):
            gains_carburants = menage('gains_tva_carburants_officielle_2019_in_2017', period)
            gains_combustibles_liquides = menage('gains_tva_combustibles_liquides_officielle_2019_in_2017', period)
            gains_gaz_ville = menage('gains_tva_gaz_ville_officielle_2019_in_2017', period)

            somme_gains = gains_carburants + gains_combustibles_liquides + gains_gaz_ville
            return somme_gains

    class quantites_gaz_final_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Quantités de gaz consommées après la réforme"

        def formula(menage, period, parameters):
            depenses_gaz_ville_officielle_2019_in_2017 = menage('depenses_gaz_ville_officielle_2019_in_2017', period)
            depenses_gaz_tarif_fixe = menage('depenses_gaz_tarif_fixe', period)
            depenses_gaz_variables = depenses_gaz_ville_officielle_2019_in_2017 - depenses_gaz_tarif_fixe

            depenses_gaz_prix_unitaire = menage('depenses_gaz_prix_unitaire', period)
            reforme_gaz = \
                parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017

            quantites_gaz_ajustees = depenses_gaz_variables / (depenses_gaz_prix_unitaire + reforme_gaz)

            return quantites_gaz_ajustees


    class revenu_reforme_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Revenu généré par la réforme officielle 2018 avant redistribution"

        def formula(menage, period):
            total_taxes_energies = menage('total_taxes_energies', period)
            total_taxes_energies_officielle_2019_in_2017 = \
                menage('total_taxes_energies_officielle_2019_in_2017', period)
            gains_tva_total_energies = menage('gains_tva_total_energies_officielle_2019_in_2017', period)
            tarifs_sociaux_electricite = menage('tarifs_sociaux_electricite', period)
            tarifs_sociaux_gaz = menage('tarifs_sociaux_gaz', period)

            revenu_reforme = (
                total_taxes_energies_officielle_2019_in_2017 - total_taxes_energies
                + gains_tva_total_energies + tarifs_sociaux_electricite + tarifs_sociaux_gaz
                )

            return revenu_reforme


    class taxe_gaz_ville_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Recettes de la taxe sur la consommation de gaz - ceteris paribus"
        # On considère que les contributions sur les taxes précédentes ne sont pas affectées

        def formula(menage, period, parameters):
            quantites_gaz_ajustees = menage('quantites_gaz_final_officielle_2019_in_2017', period)
            reforme_gaz = parameters(period.start).officielle_2019_in_2017.gaz_ville_2019_in_2017
            recettes_gaz = quantites_gaz_ajustees * reforme_gaz

            return recettes_gaz

    class total_taxes_energies_officielle_2019_in_2017(YearlyVariable):
        value_type = float
        entity = Menage
        label = "Différence entre les contributions aux taxes sur l'énergie après la hausse cce 2016-2018"

        def formula(menage, period):
            essence_ticpe = menage('essence_ticpe', period)
            diesel_ticpe = menage('diesel_ticpe', period)
            combustibles_liquides_ticpe = menage('combustibles_liquides_ticpe', period)
            taxe_gaz_ville = menage('taxe_gaz_ville_officielle_2019_in_2017', period)
            return diesel_ticpe + essence_ticpe + combustibles_liquides_ticpe + taxe_gaz_ville

    def apply(self):
        self.update_variable(self.cheques_energie)
        self.update_variable(self.depenses_energies_logement_officielle_2019_in_2017)
        # self.update_variable(self.depenses_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_carburants_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_combustibles_liquides_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.gains_tva_total_energies_officielle_2019_in_2017)
        self.update_variable(self.quantites_gaz_final_officielle_2019_in_2017)
        self.update_variable(self.revenu_reforme_officielle_2019_in_2017)
        self.update_variable(self.taxe_gaz_ville_officielle_2019_in_2017)
        self.update_variable(self.total_taxes_energies_officielle_2019_in_2017)
        self.modify_parameters(modifier_function = modify_parameters)
