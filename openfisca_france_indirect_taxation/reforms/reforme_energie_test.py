from openfisca_core.reforms import Reform


from openfisca_france_indirect_taxation.variables.base import *  # noqa analysis:ignore


parameters_path = os.path.join(os.path.dirname(__file__), 'parameters')


def modify_parameters(parameters):
    parameters = build_prix_carburants_reference(parameters)
    reference_value = parameters.prix_carburants.diesel_ttc_reference(2014)
    parameters.prix_carburants.diesel_ttc.update(
        period = '2014',
        value = reference_value + 10
        )
    return parameters


class reforme_energie_test(Reform):
    key = 'reforme_energie_test'
    name = "Reforme test de l'imposition indirecte des carburants"

    def apply(self):
        self.modify_parameters(modifier_function = modify_parameters)


# Helpers

def build_prix_carburants_reference(parameters):

    for node in [parameters.prix_carburants, parameters.tarifs_energie.prix_fioul_domestique]:
        for child_key, child_node in node.children.copy().items():
            reference = child_node.clone()
            parameters.prix_carburants.add_child("{}_reference".format(child_key), reference)

    return parameters
