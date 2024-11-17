from owlready2 import OneOf


class CapabilitySkillOntologyUtils:
    """
    This class contains some utils methods related to the ontology of Capability-Skill.
    """

    @staticmethod
    def get_possible_values_of_datatype(datatype):
        """
        This method returns all possible values of an OWL data type. If the data type does not have the equivalent
        'OneOf', so the values do not need to be constrained and validated, it returns None.

        Args:
            datatype (owlready2.Oneof): OWL datatype object.

        Returns:
            list: possible values of datatype in form of a list of strings.
        """
        possible_values = []
        if datatype.equivalent_to:  # Comprobar si hay clases equivalentes
            for equivalent in datatype.equivalent_to:
                if isinstance(equivalent, OneOf):
                    for value in equivalent.instances:
                        possible_values.append(str(value))
        if len(possible_values) == 0:
            return None
        return possible_values

