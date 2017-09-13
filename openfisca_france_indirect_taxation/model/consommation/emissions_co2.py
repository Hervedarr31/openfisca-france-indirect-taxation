# -*- coding: utf-8 -*-

from __future__ import division


from openfisca_france_indirect_taxation.model.base import * # noqa analysis:ignore


# Source : Ademe, Documentation des facteurs d'émissions de la Base Carbone
# http://www.bilans-ges.ademe.fr/static/documents/[Base%20Carbone]%20Documentation%20g%C3%A9n%C3%A9rale%20v11.0.pdf

class emissions_CO2_carburants(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation de carburants, en kg de CO2"

    def formula(self, simulation, period):
        quantites_diesel = simulation.calculate('quantites_diesel', period)
        quantites_essence = simulation.calculate('quantites_essence', period)
        emissions_diesel = \
            simulation.legislation_at(period.start).imposition_indirecte.emissions_CO2.carburants.CO2_diesel
        emissions_essence = \
            simulation.legislation_at(period.start).imposition_indirecte.emissions_CO2.carburants.CO2_essence
        emissions = quantites_diesel * emissions_diesel + quantites_essence * emissions_essence  # Source : Ademe

        return emissions


class emissions_CO2_energies_totales(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation d'énergies totale, en kg de CO2"

    def formula(self, simulation, period):
        emissions_energies_logement = simulation.calculate('emissions_CO2_energies_logement', period)
        emissions_carburants = simulation.calculate('emissions_CO2_carburants', period)
        emissions = emissions_energies_logement + emissions_carburants

        return emissions


class emissions_CO2_energies_logement(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation d'énergies dans leur logement, en kg de CO2"

    def formula(self, simulation, period):
        emissions_electricite = simulation.calculate('emissions_CO2_electricite', period)
        emissions_gaz = simulation.calculate('emissions_CO2_gaz', period)
        emissions_combustibles_liquides = simulation.calculate('emissions_CO2_combustibles_liquides', period)
        emissions = emissions_electricite + emissions_gaz + emissions_combustibles_liquides  # Source : Ademe

        return emissions


class emissions_CO2_gaz(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation de gaz, en kg de CO2"

    def formula(self, simulation, period):
        quantites_gaz = simulation.calculate('quantites_gaz_contrat_optimal', period)
        emissions_gaz = \
            simulation.legislation_at(period.start).imposition_indirecte.emissions_CO2.energie_logement.CO2_gaz
        emissions = quantites_gaz * emissions_gaz

        return emissions


class emissions_CO2_electricite(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation d'électricité, en kg de CO2"

    def formula(self, simulation, period):
        quantites_eletricite = simulation.calculate('quantites_electricite_selon_compteur', period)
        emissions_electricite = \
            simulation.legislation_at(period.start).imposition_indirecte.emissions_CO2.energie_logement.CO2_electricite
        emissions = quantites_eletricite * emissions_electricite

        return emissions


class emissions_CO2_combustibles_liquides(YearlyVariable):
    column = FloatCol
    entity = Menage
    label = u"Emissions de CO2 des ménages via leur consommation de combustibles liquides, en kg de CO2"

    def formula(self, simulation, period):
        quantite_combustibles_liquides = simulation.calculate('quantites_combustibles_liquides', period)
        emissions_combustibles_liquidies = \
            simulation.legislation_at(period.start).imposition_indirecte.emissions_CO2.energie_logement.CO2_combustibles_liquides
        emissions = quantite_combustibles_liquides * emissions_combustibles_liquidies

        return emissions
