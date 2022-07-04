from openfisca_france_indirect_taxation.variables.base import Menage, Variable, YEAR

# montant TVA sur different type de gazole:


# TVA sur gazole B7:

class tva_sur_ht_gazole_b7(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la part produit de gazole B7'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period, parameters):
        cout_gazole_b7_ht = menage('cout_gazole_b7_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_gazole_b7_ht * (1 / (1 + taux_plein_tva))
        tva = cout_gazole_b7_ht - hors_tva
        return tva


class tva_sur_ticpe_gazole_b7(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la part TICPE de gazole B7'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period, parameters):
        gazole_b7_ticpe = menage('gazole_b7_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = gazole_b7_ticpe * (1 / (1 + taux_plein_tva))
        tva = gazole_b7_ticpe - hors_tva
        return tva


class tva_sur_gazole_b7(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la consommation de gazole B7'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period, parameters):
        tva_sur_ht_gazole_b7 = menage('tva_sur_ht_gazole_b7', period)
        tva_sur_ticpe_gazole_b7 = menage('tva_sur_ticpe_gazole_b7', period)
        tva = tva_sur_ht_gazole_b7 + tva_sur_ticpe_gazole_b7
        return tva


# TVA sur gazole B10

class tva_sur_ht_gazole_b10(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la part produit de gazole B10'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period, parameters):
        cout_gazole_b10_ht = menage('cout_gazole_b10_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_gazole_b10_ht * (1 / (1 + taux_plein_tva))
        tva = cout_gazole_b10_ht - hors_tva
        return tva


class tva_sur_ticpe_gazole_b10(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la part TICPE de gazole B10'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period, parameters):
        gazole_b10_ticpe = menage('gazole_b10_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = gazole_b10_ticpe * (1 / (1 + taux_plein_tva))
        tva = gazole_b10_ticpe - hors_tva
        return tva


class tva_sur_gazole_b10(Variable):
    value_type = float
    entity = Menage
    label = 'TVA sur la consommation de gazole B10'
    definition_period = YEAR
    default_value = 0

    def formula(menage, period):
        tva_sur_ht_gazole_b10 = menage('tva_sur_ht_gazole_b10', period)
        tva_sur_ticpe_gazole_b10 = menage('tva_sur_ticpe_gazole_b10', period)
        tva = tva_sur_ht_gazole_b10 + tva_sur_ticpe_gazole_b10
        return tva


# montant TVA sur gazole total:


class tva_sur_gazole_total(Variable):
    value_type = float
    entity = Menage
    label = 'TVA total sur le gazole'
    definition_period = YEAR
    default_value = 0

    def formula_2017(menage, period):
        tva_sur_gazole_b7 = menage('tva_sur_gazole_b7', period)
        tva_sur_gazole_b10 = menage('tva_sur_gazole_b10', period)
        tva_sur_gazole_total = (tva_sur_gazole_b7 + tva_sur_gazole_b10)
        return tva_sur_gazole_total

    def formula(menage, period):
        tva_sur_gazole_b7 = menage('tva_sur_gazole_b7', period)
        tva_sur_gazole_total = tva_sur_gazole_b7
        return tva_sur_gazole_total


# montant TVA sur different type d'essence:


# mantant TVA sur essence sp95 e10


class tva_sur_ht_essence_sp95_e10(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de l'essence sp95 e10"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        cout_essence_sp95_e10_ht = menage('cout_essence_sp95_e10_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_essence_sp95_e10_ht * (1 / (1 + taux_plein_tva))
        tva = cout_essence_sp95_e10_ht - hors_tva
        return tva


class tva_sur_ticpe_essence_sp95_e10(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de l'essence sp95 e10"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        essence_sp95_e10_ticpe = menage('essence_sp95_e10_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = essence_sp95_e10_ticpe * (1 / (1 + taux_plein_tva))
        tva = essence_sp95_e10_ticpe - hors_tva
        return tva


class tva_sur_essence_sp95_e10(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de l'essence sp95 e10"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period):
        tva_sur_ht_essence_sp95_e10 = menage('tva_sur_ht_essence_sp95_e10', period)
        tva_sur_ticpe_essence_sp95_e10 = menage('tva_sur_ticpe_essence_sp95_e10', period)
        tva = tva_sur_ht_essence_sp95_e10 + tva_sur_ticpe_essence_sp95_e10
        return tva


# mantant TVA sur essence sp95

class tva_sur_ht_essence_sp95(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de l'essence sp95"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        cout_essence_sp95_ht = menage('cout_essence_sp95_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_essence_sp95_ht * (1 / (1 + taux_plein_tva))
        tva = cout_essence_sp95_ht - hors_tva
        return tva


class tva_sur_ticpe_essence_sp95(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de l'essence sp95"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        essence_sp95_ticpe = menage('essence_sp95_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = essence_sp95_ticpe * (1 / (1 + taux_plein_tva))
        tva = essence_sp95_ticpe - hors_tva
        return tva


class tva_sur_essence_sp95(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de l'essence sp95"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period):
        tva_sur_ht_essence_sp95 = menage('tva_sur_ht_essence_sp95', period)
        tva_sur_ticpe_essence_sp95 = menage('tva_sur_ticpe_essence_sp95', period)
        tva = tva_sur_ht_essence_sp95 + tva_sur_ticpe_essence_sp95
        return tva


# mantant TVA sur essence sp98:


class tva_sur_ht_essence_sp98(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de l'essence sp98"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        cout_essence_sp98_ht = menage('cout_essence_sp98_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_essence_sp98_ht * (1 / (1 + taux_plein_tva))
        tva = cout_essence_sp98_ht - hors_tva
        return tva


class tva_sur_ticpe_essence_sp98(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de l'essence sp98"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        essence_sp98_ticpe = menage('essence_sp98_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = essence_sp98_ticpe * (1 / (1 + taux_plein_tva))
        tva = essence_sp98_ticpe - hors_tva
        return tva


class tva_sur_essence_sp98(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de l'essence sp98"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period):
        tva_sur_ht_essence_sp98 = menage('tva_sur_ht_essence_sp98', period)
        tva_sur_ticpe_essence_sp98 = menage('tva_sur_ticpe_essence_sp98', period)
        tva = tva_sur_ht_essence_sp98 + tva_sur_ticpe_essence_sp98
        return tva


# mantant TVA sur essence super plombé:


class tva_sur_ht_essence_super_plombe(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de l'essence super plombé"
    definition_period = YEAR
    default_value = 0
    end = '2006-12-31'

    def formula(menage, period, parameters):
        cout_essence_super_plombe_ht = menage('cout_essence_super_plombe_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_essence_super_plombe_ht * (1 / (1 + taux_plein_tva))
        tva = cout_essence_super_plombe_ht - hors_tva
        return tva


class tva_sur_ticpe_essence_super_plombe(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de l'essence super plombé"
    definition_period = YEAR
    default_value = 0
    end = '2006-12-31'

    def formula(menage, period, parameters):
        essence_super_plombe_ticpe = menage('essence_super_plombe_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = essence_super_plombe_ticpe * (1 / (1 + taux_plein_tva))
        tva = essence_super_plombe_ticpe - hors_tva
        return tva


class tva_sur_essence_super_plombe(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de l'essence super plombé"
    definition_period = YEAR
    default_value = 0
    end = '2006-12-31'

    def formula(menage, period):
        tva_sur_ht_essence_super_plombe = menage('tva_sur_ht_essence_super_plombe', period)
        tva_sur_ticpe_essence_super_plombe = menage('tva_sur_ticpe_essence_super_plombe', period)
        tva = tva_sur_ht_essence_super_plombe + tva_sur_ticpe_essence_super_plombe
        return tva


# mantant TVA sur essence e85:

class tva_sur_ht_essence_e85(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de l'essence e85"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        cout_essence_e85_ht = menage('cout_essence_e85_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_essence_e85_ht * (1 / (1 + taux_plein_tva))
        tva = cout_essence_e85_ht - hors_tva
        return tva


class tva_sur_ticpe_essence_e85(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de l'essence e85"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        essence_e85_ticpe = menage('essence_e85_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = essence_e85_ticpe * (1 / (1 + taux_plein_tva))
        tva = essence_e85_ticpe - hors_tva
        return tva


class tva_sur_essence_e85(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de l'essence e85"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period):
        tva_sur_ht_essence_e85 = menage('tva_sur_ht_essence_e85', period)
        tva_sur_ticpe_essence_e85 = menage('tva_sur_ticpe_essence_e85', period)
        tva = tva_sur_ht_essence_e85 + tva_sur_ticpe_essence_e85
        return tva


# montant TVA total sur l'essence

class tva_sur_essence_total(Variable):
    value_type = float
    entity = Menage
    label = "Calcul du montant de la TVA sur tous les types d'essences cumulés"
    definition_period = YEAR

    def formula_2009(menage, period):
        tva_sur_essence_sp95 = menage('tva_sur_essence_sp95', period)
        tva_sur_essence_sp98 = menage('tva_sur_essence_sp98', period)
        tva_sur_essence_e85 = menage('tva_sur_essence_e85', period)
        tva_sur_essence_sp95_e10 = menage('tva_sur_essence_sp95_e10', period)
        tva_sur_essence_total = (tva_sur_essence_sp95 + tva_sur_essence_sp98 + tva_sur_essence_e85 + tva_sur_essence_sp95_e10)
        return tva_sur_essence_total

    def formula_2007(menage, period):
        tva_sur_essence_sp95 = menage('tva_sur_essence_sp95', period)
        tva_sur_essence_sp98 = menage('tva_sur_essence_sp98', period)
        tva_sur_essence_e85 = menage('tva_sur_essence_e85', period)
        tva_sur_essence_total = (tva_sur_essence_sp95 + tva_sur_essence_sp98 + tva_sur_essence_e85)
        return tva_sur_essence_total

    def formula_1990(menage, period):
        tva_sur_essence_sp95 = menage('tva_sur_essence_sp95', period)
        tva_sur_essence_sp98 = menage('tva_sur_essence_sp98', period)
        tva_sur_essence_super_plombe = menage('tva_sur_essence_super_plombe', period)
        tva_sur_essence_total = (tva_sur_essence_sp95 + tva_sur_essence_sp98 + tva_sur_essence_super_plombe)
        return tva_sur_essence_total


# montant TVA sur le gaz de pétrole liquéfié carburant:


class tva_sur_ht_gpl_carburant(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part ht de gaz de pétrole liquéfié carburant"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        cout_gpl_carburant_ht = menage('cout_gpl_carburant_ht', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = cout_gpl_carburant_ht * (1 / (1 + taux_plein_tva))
        tva = cout_gpl_carburant_ht - hors_tva
        return tva


class tva_sur_ticpe_gpl_carburant(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la part TICPE de gaz de pétrole liquéfié carburant"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period, parameters):
        gpl_carburant_ticpe = menage('gpl_carburant_ticpe', period)
        taux_plein_tva = parameters(period).imposition_indirecte.tva.taux_de_tva.taux_normal
        hors_tva = gpl_carburant_ticpe * (1 / (1 + taux_plein_tva))
        tva = gpl_carburant_ticpe - hors_tva
        return tva


class tva_sur_gpl_carburant(Variable):
    value_type = float
    entity = Menage
    label = "TVA sur la consommation de gaz de pétrole liquéfié carburant"
    definition_period = YEAR
    default_value = 0

    def formula_2009(menage, period):
        tva_sur_ht_gpl_carburant = menage('tva_sur_ht_gpl_carburant', period)
        tva_sur_ticpe_gpl_carburant = menage('tva_sur_ticpe_gpl_carburant', period)
        tva = tva_sur_ht_gpl_carburant + tva_sur_ticpe_gpl_carburant
        return tva


# montant carburant total:

class tva_sur_carburant_total(Variable):
    value_type = float
    entity = Menage
    label = 'Calcul du montant de la TVA sur tous les carburants cumulés'
    definition_period = YEAR

    def formula(menage, period):
        tva_sur_essence_total = menage('tva_sur_essence_total', period)
        tva_sur_gazole_total = menage('tva_sur_gazole_total', period)
        tva_sur_gpl_carburant = menage('tva_sur_gpl_carburant', period)
        tva_sur_carburant_total = tva_sur_gazole_total + tva_sur_essence_total + tva_sur_gpl_carburant
        return tva_sur_carburant_total
