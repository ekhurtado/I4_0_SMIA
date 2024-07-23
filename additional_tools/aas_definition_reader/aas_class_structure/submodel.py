"""
This module contains the class for the implementation of the Submodel and related classes.
"""
import abc

from aas_definition_reader.aas_class_structure.common import Referable, HasKind, Qualifiable, HasSemantics, \
    HasDataSpecification, KeyTypes, Identifiable


class SubmodelElement(Referable, HasKind, Qualifiable, HasSemantics, HasDataSpecification, metaclass=abc.ABCMeta):
    """
    TODO rellenarlo
    """

    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 display_name,
                 category: KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier=None,
                 extension=None,
                 supplemental_semantic_id: set[KeyTypes.Reference] = (),
                 embedded_data_specifications=None):
        super().__init__()
        self.id_short: KeyTypes.Reference = id_short
        self.display_name = display_name
        self.category: KeyTypes.Reference = category
        self.description = description
        self.parent = parent
        self.semantic_id: KeyTypes.Reference = semantic_id
        self.qualifier = qualifier
        self.extension = extension
        self.supplemental_semantic_id: set[KeyTypes.Reference] = set(supplemental_semantic_id)
        self.embedded_data_specifications = set(embedded_data_specifications)


class Submodel(Identifiable, HasKind, HasSemantics, Qualifiable, HasDataSpecification):
    """
    TODO rellenarlo
    """

    def __init__(self, sm_elements: set[SubmodelElement] = None):
        super().__init__()
        self.sm_elements: set[SubmodelElement] = sm_elements


# Submodel types
# --------------
class DataElement():
    #TODO

class Property():
    #TODO

class Range():
    #TODO


class Blob():
    #TODO


class File():
    #TODO


class ReferenceElement():
    # TODO


class SubmodelElementCollection():
    # TODO


class SubmodelElementCollection():
    # TODO

class Entity():
    # TODO

class Operation():
    # TODO

