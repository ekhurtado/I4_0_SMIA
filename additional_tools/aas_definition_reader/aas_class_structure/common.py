"""
This module implements the common structures of the AAS meta-model, including the abstract classes and necessary
enumerations for any higher level class to inherit from them.
"""
import abc
from enum import Enum
from typing import List


class KeyTypes:
    # AasIdentifiables starting from 0
    # keep _ASSET = 0 as a protected enum member here, so 0 isn't reused by a future key type
    _ASSET = 0
    ASSET_ADMINISTRATION_SHELL = 1
    CONCEPT_DESCRIPTION = 2
    SUBMODEL = 3
    # TODO REVISARLO E IR AÑADIENDO

    # Global types
    Reference = str
    Identifier = str
    NameType = str
    PathType = str
    ContentType = str


class HasExtensions(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.extension: []


class Extension:
    """
    #TODO Rellenarlo
    """

    def __init__(self, name, value_type, value) -> None:
        super().__init__()
        self.name = name
        self.value_type = value_type
        self.value = value


class Referable(HasExtensions, metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    class ReferableCategoryTypes(Enum):
        """
        Predefined categories in "Details of the Asset Administration Shell - Part 1."
        """
        CONSTANT = 0
        PARAMETER = 1
        VARIABLE = 2
        NONE = None

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.id_short = None
        self.display_name = None
        self.category: Referable.ReferableCategoryTypes = Referable.ReferableCategoryTypes.NONE
        self.description = None
        self.checksum = None


class Identifiable(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    class AdministrativeInformation:
        def __init__(self):
            super().__init__()
            self.revision = None
            self.version: None

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.administration = None
        self.id: KeyTypes.Identifier


class HasKind(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    class ModelingKind(Enum):
        TYPE = 0
        INSTANCE = 1

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.kind: HasKind.ModelingKind


class HasSemantics(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.semantic_id: KeyTypes.Reference
        self.supplemental_semantic_id: List[KeyTypes.Reference]


class Qualifiable(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.qualifier: List[Qualifier]


class Qualifier(HasSemantics):
    """
    #TODO Rellenarlo
    """

    class QualifierKind(Enum):
        VALUE_QUALIFIER = 0
        CONCEPT_QUALIFIER = 1
        TEMPLATE_QUALIFIER = 2

    def __init__(self, kind: QualifierKind = QualifierKind.CONCEPT_QUALIFIER, type=None,
                 value_type=None, value=None, value_id: KeyTypes.Reference = None):
        super().__init__()
        self.kind: Qualifier.QualifierKind = kind
        self.type = type
        self.value_type = value_type
        self.value = value
        self.value_id: KeyTypes.Reference = value_id


class HasDataSpecification(metaclass=abc.ABCMeta):
    """
    #TODO Rellenarlo
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.data_specification: KeyTypes.Reference
