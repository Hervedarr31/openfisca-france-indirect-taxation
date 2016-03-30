# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from openfisca_core import reforms
from openfisca_core.tools import assert_near

from .. import init_country
from ..reforms import (
    taxes_carburants,
    taxe_carbone,
    )


__all__ = [
    'assert_near',
    'get_cached_composed_reform',
    'get_cached_reform',
    'tax_benefit_system',
    'TaxBenefitSystem',
    ]

# Initialize a tax_benefit_system

TaxBenefitSystem = init_country()
tax_benefit_system = TaxBenefitSystem()
tax_benefit_system.prefill_cache()

build_reform_function_by_key = {
    'taxes_carburants': taxes_carburants.build_reform,
    'taxe_carbone': taxe_carbone.build_reform,
    }
reform_by_full_key = {}


# Reforms cache, used by long scripts like test_yaml.py

def get_cached_composed_reform(reform_keys, tax_benefit_system):
    full_key = '.'.join(
        [tax_benefit_system.full_key] + reform_keys
        if isinstance(tax_benefit_system, reforms.AbstractReform)
        else reform_keys
        )
    composed_reform = reform_by_full_key.get(full_key)
    if composed_reform is None:
        build_reform_functions = []
        for reform_key in reform_keys:
            assert reform_key in build_reform_function_by_key, \
                'Error loading cached reform "{}" in build_reform_functions'.format(reform_key)
            build_reform_function = build_reform_function_by_key[reform_key]
            build_reform_functions.append(build_reform_function)
        composed_reform = reforms.compose_reforms(
            build_functions_and_keys = zip(build_reform_functions, reform_keys),
            tax_benefit_system = tax_benefit_system,
            )
        assert full_key == composed_reform.full_key
        reform_by_full_key[full_key] = composed_reform
    return composed_reform


def get_cached_reform(reform_key, tax_benefit_system):
    return get_cached_composed_reform([reform_key], tax_benefit_system)
