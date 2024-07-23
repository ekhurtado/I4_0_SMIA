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
class DataElement(SubmodelElement, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 display_name = None,
                 category: KeyTypes.NameType = None,
                 description = None,
                 parent = None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier = (),
                 extension = (),
                 supplemental_semantic_id = (),
                 embedded_data_specifications = ()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)

class Property(DataElement):
    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 value_type,
                 value = None,
                 value_id: KeyTypes.Reference = None,
                 display_name=None,
                 category: KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier=(),
                 extension=(),
                 supplemental_semantic_id=(),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type = value_type
        self._value = value
        self.value_id: KeyTypes.Reference = value_id

class Range(DataElement):
    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 value_type,
                 _min = None,
                 _max = None,
                 display_name=None,
                 category: KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier=(),
                 extension=(),
                 supplemental_semantic_id=(),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type = value_type
        self.min = _min
        self.max = _max


class Blob(DataElement):
    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 value_type,
                 content_type: KeyTypes.ContentType = None,
                 display_name=None,
                 category: KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier=(),
                 extension=(),
                 supplemental_semantic_id=(),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type = value_type
        self.content_type: KeyTypes.ContentType = content_type


class File(DataElement):
    @abc.abstractmethod
    def __init__(self,
                 id_short: KeyTypes.NameType,
                 _value: KeyTypes.PathType = None,
                 content_type: KeyTypes.ContentType = None,
                 display_name=None,
                 category: KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: KeyTypes.Reference = None,
                 qualifier=(),
                 extension=(),
                 supplemental_semantic_id=(),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value: KeyTypes.PathType = _value
        self.content_type: KeyTypes.ContentType = content_type


class ReferenceElement(DataElement):
    # TODO


class SubmodelElementList(DataElement):
    # TODO


class SubmodelElementCollection(DataElement):
    # TODO

class Entity(DataElement):
    # TODO

class Operation(DataElement):
    # TODO

