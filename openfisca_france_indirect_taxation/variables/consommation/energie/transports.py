from openfisca_core.parameters import ParameterNotFound
from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


class depenses_carburants(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Consommation de carburants"

    def formula(menage, period):
        return menage('depenses_diesel', period) + menage('depenses_essence', period)


class depenses_diesel_ht(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en diesel ht (prix brut sans TVA ni TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        majoration_ticpe_diesel = \
            parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_gazole.alsace
        accise_diesel = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.gazole

        accise_diesel_ticpe = (
            accise_diesel + majoration_ticpe_diesel
            if majoration_ticpe_diesel is not None
            else accise_diesel
            )
        prix_diesel_ttc = parameters(period.start).prix_carburants.diesel_ttc
        taux_implicite_diesel = (
            (accise_diesel_ticpe * (1 + taux_plein_tva))
            / (prix_diesel_ttc - accise_diesel_ticpe * (1 + taux_plein_tva))
            )

        depenses_diesel_htva = menage('depenses_diesel_htva', period)
        depenses_diesel_ht = \
            depenses_diesel_htva - tax_from_expense_including_tax(depenses_diesel_htva, taux_implicite_diesel)

        return depenses_diesel_ht


class depenses_diesel_htva(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en diesel htva (mais incluant toujours la TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        depenses_diesel = menage('depenses_diesel', period)
        depenses_diesel_htva = depenses_diesel - tax_from_expense_including_tax(depenses_diesel, taux_plein_tva)

        return depenses_diesel_htva


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


class depenses_diesel_recalculees(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en diesel recalculées à partir du prix ht"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        depenses_diesel_ht = menage('depenses_diesel_ht', period)
        majoration_ticpe_diesel = \
            parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_gazole.alsace
        accise_diesel = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.gazole

        accise_diesel_ticpe = (
            accise_diesel + majoration_ticpe_diesel
            if majoration_ticpe_diesel is not None
            else accise_diesel
            )
        prix_diesel_ttc = parameters(period.start).prix_carburants.diesel_ttc
        taux_implicite_diesel = (
            (accise_diesel_ticpe * (1 + taux_plein_tva))
            / (prix_diesel_ttc - accise_diesel_ticpe * (1 + taux_plein_tva))
            )

        depenses_diesel_recalculees = depenses_diesel_ht * (1 + taux_plein_tva) * (1 + taux_implicite_diesel)

        return depenses_diesel_recalculees


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


class depenses_essence_ht(Variable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence hors taxes (HT, i.e. sans TVA ni TICPE)"
    definition_period = YEAR

    def formula_2009(menage, period):
        depenses_sp_95_ht = menage('depenses_sp_95_ht', period)
        depenses_sp_98_ht = menage('depenses_sp_98_ht', period)
        depenses_sp_e10_ht = menage('depenses_sp_e10_ht', period)
        depenses_essence_ht = (depenses_sp_95_ht + depenses_sp_98_ht + depenses_sp_e10_ht)
        return depenses_essence_ht

    def formula_2007(menage, period):
        depenses_sp_95_ht = menage('depenses_sp_95_ht', period)
        depenses_sp_98_ht = menage('depenses_sp_98_ht', period)
        depenses_essence_ht = (depenses_sp_95_ht + depenses_sp_98_ht)
        return depenses_essence_ht

    def formula_1990(menage, period):
        depenses_sp_95_ht = menage('depenses_sp_95_ht', period)
        depenses_sp_98_ht = menage('depenses_sp_98_ht', period)
        depenses_super_plombe_ht = menage('depenses_super_plombe_ht', period)
        depenses_essence_ht = (depenses_sp_95_ht + depenses_sp_98_ht + depenses_super_plombe_ht)
        return depenses_essence_ht


class depenses_sp_e10(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par pondération des dépenses spécifiques au sans plomb e10"

    def formula(menage, period, parameters):
        poste_essence = menage('poste_essence', period)
        part_sp_e10 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_e10
        depenses_sp_e10 = poste_essence * part_sp_e10

        return depenses_sp_e10


class depenses_sp_e10_ht(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence sans plomb e10 hors taxes (HT, i.e. sans TVA ni TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        depenses_essence = menage('depenses_essence', period)
        part_sp_e10 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_e10
        depenses_sp_e10 = depenses_essence * part_sp_e10
        depenses_sp_e10_htva = depenses_sp_e10 - tax_from_expense_including_tax(depenses_sp_e10, taux_plein_tva)

        accise_super_e10 = \
            parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_e10
        majoration_ticpe_super_e10 = \
            parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace
        accise_ticpe_super_e10 = (
            accise_super_e10 + majoration_ticpe_super_e10
            if majoration_ticpe_super_e10 is not None
            else accise_super_e10
            )

        super_95_e10_ttc = parameters(period.start).prix_carburants.super_95_e10_ttc
        taux_implicite_sp_e10 = (
            (accise_ticpe_super_e10 * (1 + taux_plein_tva))
            / (super_95_e10_ttc - accise_ticpe_super_e10 * (1 + taux_plein_tva))
            )
        depenses_sp_e10_ht = \
            depenses_sp_e10_htva - tax_from_expense_including_tax(depenses_sp_e10_htva, taux_implicite_sp_e10)

        return depenses_sp_e10_ht


class depenses_sp_95(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par pondération des dépenses spécifiques au sans plomb 95"

    def formula(menage, period, parameters):
        depenses_essence = menage('depenses_essence', period)
        part_sp95 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_95
        depenses_sp_95 = depenses_essence * part_sp95

        return depenses_sp_95


class depenses_sp_95_ht(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence sans plomb 95 hors taxes (HT, i.e. sans TVA ni TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

        try:
            accise_super95 = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_95_98
            majoration_ticpe_super95 = \
                parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace
            accise_ticpe_super95 = accise_super95 + majoration_ticpe_super95
        except Exception as e:
            log.debug(e)
            accise_ticpe_super95 = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_95_98

        super_95_ttc = parameters(period.start).prix_carburants.super_95_ttc
        taux_implicite_sp95 = (
            (accise_ticpe_super95 * (1 + taux_plein_tva))
            / (super_95_ttc - accise_ticpe_super95 * (1 + taux_plein_tva))
            )
        depenses_essence = menage('depenses_essence', period)
        part_sp95 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_95
        depenses_sp_95 = depenses_essence * part_sp95
        depenses_sp_95_htva = depenses_sp_95 - tax_from_expense_including_tax(depenses_sp_95, taux_plein_tva)
        depenses_sp_95_ht = \
            depenses_sp_95_htva - tax_from_expense_including_tax(depenses_sp_95_htva, taux_implicite_sp95)

        return depenses_sp_95_ht


class depenses_sp_98(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par pondération des dépenses spécifiques au sans plomb 98"

    def formula(menage, period, parameters):
        depenses_essence = menage('depenses_essence', period)
        part_sp98 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_98
        depenses_sp_98 = depenses_essence * part_sp98

        return depenses_sp_98


class depenses_sp_98_ht(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence sans plomb 98 hors taxes (HT, i.e. sans TVA ni TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal

        accise_super98 = parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_95_98
        majoration_ticpe_super98 = \
            parameters(period.start).imposition_indirecte.produits_energetiques.major_regionale_ticpe_super.alsace
        accise_ticpe_super98 = (
            accise_super98 + majoration_ticpe_super98
            if majoration_ticpe_super98 is not None
            else accise_super98
            )

        super_98_ttc = parameters(period.start).prix_carburants.super_98_ttc
        taux_implicite_sp98 = (
            (accise_ticpe_super98 * (1 + taux_plein_tva))
            / (super_98_ttc - accise_ticpe_super98 * (1 + taux_plein_tva))
            )
        depenses_essence = menage('depenses_essence', period)
        part_sp98 = parameters(period.start).imposition_indirecte.part_type_supercarburants.sp_98
        depenses_sp_98 = depenses_essence * part_sp98
        depenses_sp_98_htva = depenses_sp_98 - tax_from_expense_including_tax(depenses_sp_98, taux_plein_tva)
        depenses_sp_98_ht = \
            depenses_sp_98_htva - tax_from_expense_including_tax(depenses_sp_98_htva, taux_implicite_sp98)

        return depenses_sp_98_ht


class depenses_super_plombe(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par pondération des dépenses spécifiques au super plombe"

    def formula(menage, period, parameters):
        depenses_essence = menage('depenses_essence', period)
        part_super_plombe = \
            parameters(period.start).imposition_indirecte.part_type_supercarburants.super_plombe
        depenses_super_plombe = depenses_essence * part_super_plombe

        return depenses_super_plombe


class depenses_super_plombe_ht(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Dépenses en essence super plombée hors taxes (HT, i.e. sans TVA ni TICPE)"

    def formula(menage, period, parameters):
        taux_plein_tva = parameters(period.start).imposition_indirecte.tva.taux_de_tva.taux_normal
        accise_super_plombe_ticpe = \
            parameters(period.start).imposition_indirecte.produits_energetiques.ticpe.super_plombe
        super_plombe_ttc = parameters(period.start).prix_carburants.super_plombe_ttc
        taux_implicite_super_plombe = (
            (accise_super_plombe_ticpe * (1 + taux_plein_tva))
            / (super_plombe_ttc - accise_super_plombe_ticpe * (1 + taux_plein_tva))
            )
        depenses_essence = menage('depenses_essence', period)
        part_super_plombe = \
            parameters(period.start).imposition_indirecte.part_type_supercarburants.super_plombe
        depenses_super_plombe = depenses_essence * part_super_plombe
        depenses_super_plombe_htva = \
            depenses_super_plombe - tax_from_expense_including_tax(depenses_super_plombe, taux_plein_tva)
        depenses_super_plombe_ht = (
            depenses_super_plombe_htva
            - tax_from_expense_including_tax(depenses_super_plombe_htva, taux_implicite_super_plombe)
            )

        return depenses_super_plombe_ht


class poste_carburants(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Poste de onsommation de carburants"

    def formula(menage, period):
        return menage('poste_07_2_2_1_1', period)


class poste_diesel(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par pondération des dépenses spécifiques au diesel"

    def formula(menage, period, parameters):
        conso_totale_vp_diesel = parameters(period.start).quantite_carbu_vp.diesel
        conso_totale_vp_essence = parameters(period.start).quantite_carbu_vp.essence
        taille_parc_diesel = parameters(period.start).parc_vp.diesel
        taille_parc_essence = parameters(period.start).parc_vp.essence

        conso_moyenne_vp_diesel = conso_totale_vp_diesel / taille_parc_diesel
        conso_moyenne_vp_essence = conso_totale_vp_essence / taille_parc_essence

        nombre_vehicules_diesel = menage('veh_diesel', period)
        nombre_vehicules_essence = menage('veh_essence', period)
        nombre_vehicules_total = nombre_vehicules_diesel + nombre_vehicules_essence

        # to compute part_conso_diesel we need to avoid dividing by zero for those we do not have any vehicle
        # Thus, we choose arbitrarily to divide it by 1, but this choice won't affect the result as long as it is not 0
        denominateur = (
            (nombre_vehicules_diesel * conso_moyenne_vp_diesel) + (nombre_vehicules_essence * conso_moyenne_vp_essence)
            ) * (nombre_vehicules_total != 0) + 1 * (nombre_vehicules_total == 0)

        part_conso_diesel = (nombre_vehicules_diesel * conso_moyenne_vp_diesel) / denominateur

        poste_carburants = menage('poste_carburants', period)

        poste_diesel = poste_carburants * (
            (nombre_vehicules_total == 0) * (
                conso_totale_vp_diesel / (conso_totale_vp_diesel + conso_totale_vp_essence)
                )
            + (nombre_vehicules_total != 0) * part_conso_diesel
            )

        return poste_diesel


class poste_essence(YearlyVariable):
    value_type = float
    entity = Menage
    label = "Construction par déduction des dépenses spécifiques à l'essence"

    def formula(menage, period):
        poste_carburants = menage('poste_carburants', period)
        poste_diesel = menage('poste_diesel', period)
        poste_essence = poste_carburants - poste_diesel

        return poste_essence
