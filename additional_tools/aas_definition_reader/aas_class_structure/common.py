"""
This module implements the common structures of the AAS meta-model, including the abstract classes and necessary
enumerations for any higher level class to inherit from them.
"""
import abc
from enum import Enum, unique

from aas_definition_reader.aas_class_structure.aas import AssetAdministrationShell
from aas_definition_reader.aas_class_structure.submodel import Submodel


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
    QualifierType = str
    RevisionType = str
    VersionType = str
    BlobType = bytes


# ----------------------
# Has`Attribute` classes
# ----------------------
class HasExtensions(metaclass=abc.ABCMeta):
    """
    It is used if an element can be extended by proprietary extensions (these do not support global interoperability).
    A Referable element is defined to have extension with HasExtensions, and the information is stored in
    :param: Extension.
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.extension: set[Extension] = set()


class HasKind(metaclass=abc.ABCMeta):
    """
    An element with a kind is an element that can either represent a template or an instance.
    Default for an element is that it is representing an instance.
    """

    @unique
    class ModelingKind(Enum):
        TYPE = 0
        INSTANCE = 1

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.kind: HasKind.ModelingKind


class HasSemantics(metaclass=abc.ABCMeta):
    """
    Determines whether an element can have one semantic definition plus some supplementary semantic definitions.
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.semantic_id: KeyTypes.Reference
        self.supplemental_semantic_id: set[KeyTypes.Reference]


class HasDataSpecification(metaclass=abc.ABCMeta):
    """
    It is used when an element can be extended using data specification templates. This template defines a set of
    additional attributes that an element can or should have. These are specified explicitly with its global ID.
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.data_specification: set[KeyTypes.Reference]


# ------------------------
# Common attribute classes
# ------------------------
class Extension(HasSemantics):
    """
    Single extension of an element.
    """

    def __init__(self, name, value_type, value) -> None:
        super().__init__()
        self.name = name
        self.value_type = value_type
        self.value = value


class Referable(HasExtensions, metaclass=abc.ABCMeta):
    """
    The AAS meta-model distinguishes between identifiable elements, referencable elements or neither. Referencable
    elements are when they can be referenced by idShort. It is unique in its namespace (i.e. a submodel is the namespace
    for the properties it contains).
    """

    @unique
    class ReferableCategoryTypes(Enum):
        """
        This class contains the predefined categories in 'Details of the Asset Administration Shell - Part 1':
         - CONSTANT: value that does not change.
         - PARAMETER: value that typically does not change.
         - VARIABLE: value to be calculated in runtime.
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


class Identifiable(Referable, metaclass=abc.ABCMeta):
    """
    It is used when an element is referenced with a unique global identifier (Identifier). Only the global ID (id)
    should be used and can have administrative information such as, e.g., the version (administration).
    """

    class AdministrativeInformation(HasDataSpecification):
        def __init__(self, revision: KeyTypes.RevisionType, version: KeyTypes.VersionType):
            super().__init__()
            self.revision: KeyTypes.RevisionType = revision
            self.version: KeyTypes.VersionType = version

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.administration = None
        self.id: KeyTypes.Identifier


class Qualifiable(metaclass=abc.ABCMeta):
    """
    The value of a qualifiable element may be further qualified by one or more qualifiers.
    """

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.qualifier: set[Qualifier]


class Qualifier(HasSemantics):
    """
    A qualifier is a type-value-pair that makes additional statements w.r.t. the value of the element. The qualifiers
    can be of the level type (defining the minimum, maximum, a typical and a nominal value), or additional types for,
    e.g., semantic or logical expressions.
    """

    @unique
    class QualifierKind(Enum):
        """
        This class contains the qualifier kinds:
         - ValueQualifier: qualifies a value (that can change in runtime) and is only applicable to instances.
         - ConceptQualifier: qualifies the semantic definition.
         - TemplateQualifier: qualifies the elements of a submodel and is only applicable to templates.
        """
        VALUE_QUALIFIER = 0
        CONCEPT_QUALIFIER = 1
        TEMPLATE_QUALIFIER = 2

    def __init__(self, kind: QualifierKind = QualifierKind.CONCEPT_QUALIFIER, type_: KeyTypes.QualifierType = None,
                 value_type=None, value=None, value_id: KeyTypes.Reference = None):
        super().__init__()
        self.kind: Qualifier.QualifierKind = kind
        self.type: KeyTypes.QualifierType = type_
        self.value_type = value_type
        self.value = value
        self.value_id: KeyTypes.Reference = value_id


