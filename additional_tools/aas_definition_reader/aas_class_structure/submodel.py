"""
This module contains the class for the implementation of the Submodel and related classes.
"""
import abc
from enum import unique, Enum

from aas_definition_reader.aas_class_structure import common
from aas_definition_reader.aas_class_structure.aas import AssetInformation


class SubmodelElement(common.Referable, common.HasKind, common.Qualifiable, common.HasSemantics,
                      common.HasDataSpecification, metaclass=abc.ABCMeta):
    """
    Submodel elements are qualifiable elements, i.e., one or more qualifiers can be defined for each of them.

    Submodel elements may also have data specification templates. For example, a template may be defined to reflect some
    of the attributes of a property concept definition if a corresponding concept description is not available.
    Otherwise, only the property definition referenced by semanticId will be available for the property. Like the
    submodel, elements are also template if Kind=Template and instances if Kind=Instance.

    In this case, all the variables of the classes it inherits are also added in its constructor.
    """

    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 display_name,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = None,
                 extension: common.Extension = None,
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=None):
        super().__init__()
        self.id_short: common.KeyTypes.Reference = id_short
        self.display_name = display_name
        self.category: common.KeyTypes.Reference = category
        self.description = description
        self.parent = parent
        self.semantic_id: common.KeyTypes.Reference = semantic_id
        self.qualifier: common.Qualifier = qualifier
        self.extension: common.Extension = extension
        self.supplemental_semantic_id: set[common.KeyTypes.Reference] = set(supplemental_semantic_id)
        self.embedded_data_specifications = set(embedded_data_specifications)


class Submodel(common.Identifiable, common.HasKind, common.HasSemantics, common.Qualifiable,
               common.HasDataSpecification):
    """
    A submodel defines a specific aspect of the asset. It is used to structure the digital representation and technical
    functionality of an AAS into distinguishable parts. Each submodel refers to a well-defined domain, and can be
    standardized and thus converted into submodel templates.

    Their only attribute is submodelElement, which is a list of none or several submodel elements. It is recommended to
    add a semanticId for submodels. On the other hand, it can be Qualifiable. Both submodels and their elements can
    have data specification templates. If the submodel is Kind=Template (within your HasKind attribute), the elements
    within that submodel are templates, if, on the other hand, it is Kind=Instance, the elements within that submodel
    are instances.
    """

    def __init__(self, sm_elements: set[SubmodelElement] = None):
        super().__init__()
        self.sm_elements: set[SubmodelElement] = sm_elements


# ----------------------
# Submodel element types
# ----------------------
class DataElement(SubmodelElement, metaclass=abc.ABCMeta):
    """
    It is a submodel element that is not itself composed of other submodel elements. A Data Element is a submodel
    element that has a value or a predefined number of values. The type of value varies according to the subtypes of
    data elements.

    Since the attributes are added in the global constructor of SubmodelElement, use is made of the method inherited
    from the constructor.
    """
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)


# -------------------
# Data element types
# -------------------
class Property(DataElement):
    """It is a Data Element that has a unique value. """
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_type,
                 value=None,
                 value_id: common.KeyTypes.Reference = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type = value_type
        self._value = value
        self.value_id: common.KeyTypes.Reference = value_id


class Range(DataElement):
    """It is a Data Element that defines a range with a minimum and maximum. """
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_type,
                 _min=None,
                 _max=None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type = value_type
        self.min = _min
        self.max = _max


class Blob(DataElement):
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_type: common.KeyTypes.BlobType,
                 content_type: common.KeyTypes.ContentType = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value_type: common.KeyTypes.BlobType = value_type
        self.content_type: common.KeyTypes.ContentType = content_type


class File(DataElement):
    """
    It is a Data Element that represents an address to a file. The value is a URI that can represent an absolute or
    relative path.
    """
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 _value: common.KeyTypes.PathType = None,
                 content_type: common.KeyTypes.ContentType = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value: common.KeyTypes.PathType = _value
        self.content_type: common.KeyTypes.ContentType = content_type


class ReferenceElement(DataElement):
    """
    It is a Data Element that defines a logical reference to another element within the same or another AAS or a
    reference to an external object or entity. Its single value attribute contains the global reference to that element.
    """
    @abc.abstractmethod
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 _value: common.KeyTypes.Reference = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value: common.KeyTypes.Reference = _value


# ----------------------
# Submodel element types
# ----------------------
class SubmodelElementList(SubmodelElement):
    """
    They are used to group Submodel Elements in lists, for sets (unordered collections without duplicates), ordered
    lists (ordered collections with duplicates), bags (unordered collections with duplicates), and for ordered sets
    (ordered collections without duplicates). Submodel element lists are also used to create multidimensional arrays
    (leveraging collections and lists). Its attributes are:
      - orderRelevant: defines whether the order in relevant: False (for set or bag) and True.
      - semanticIdListElement: the semanticIDs of the Submodel Elements.
      - typeValueListElement: type of Submodel Elements.
      - valueTypeListElement: data type of the Submodel Elements.
      - value: the Submodel Elements that are part of the list
    """
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 order_relevant: bool = True,
                 semantic_id_list_element: common.KeyTypes.Reference = None,
                 type_value_list_element=None,
                 value_type_list_element=None,
                 value_: set[SubmodelElement] = None,  # Ordered list of submodel elements.
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.order_relevant = order_relevant
        self.semantic_id_list_element = semantic_id_list_element
        self.type_value_list_element = type_value_list_element
        self.value_type_list_element = value_type_list_element
        self.value = value_


class SubmodelElementCollection(SubmodelElement):
    """
    It is used for entities with a fixed set of properties with unique names within the structure. Each property within
    the collection must have clearly defined semantics. A property of a structure can be any Submodel Element with a
    value. That is, it is used to group Submodel Elements that are related to each other.
    """
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_: set[SubmodelElement] = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value = value_


class Entity(SubmodelElement):
    """
    An entity is a Submodel Element that is used to model entities. It has the following attributes:
      - statement: statements applicable to the entity by a set of submodel elements, usually with a qualified value.
      - entityType: type of entity, can be:
        - co-managed: there is no independent AAS, so they must be part of a self-managed entity.
        - self-managed: they have their own AAS (but may be part of the BOM of a composite self-managed entity).
          The asset of an I4.0 Component is of this type by definition.
      - globalAssetId: globally unique identifier of the asset it represents.
      - specificAssetId: specific identifier of the asset (it is a supplementary identifier, e.g. serial number).
    """
    @unique
    class EntityType(Enum):
        CO_MANAGED_ENTITY = 0
        SELF_MANAGED_ENTITY = 1

    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 entity_type: EntityType,
                 statement: set[SubmodelElement] = None,
                 global_asset_id: common.KeyTypes.Reference = None,
                 specific_asset_id: AssetInformation.SpecificAssetId = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.statement: set[SubmodelElement] = statement
        self.entity_type: Entity.EntityType = entity_type
        self.global_asset_id: common.KeyTypes.Reference = global_asset_id
        self.specific_asset_id: AssetInformation.SpecificAssetId = specific_asset_id


class Operation(SubmodelElement):
    """
    It is a Submodel Element that has input and output variables. Its attributes have a value that is a Submodel Element
     that describes the argument or the result of the operation.
    """
    class OperationVariable:
        def __init__(self, value_: SubmodelElement):
            self.value: SubmodelElement = value_

    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 input_variable: set[OperationVariable] = None,
                 output_variable: set[OperationVariable] = None,
                 inoutput_variable: set[OperationVariable] = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.input_variable: set[Operation.OperationVariable] = input_variable
        self.output_variable: set[Operation.OperationVariable] = output_variable
        self.inoutput_variable: set[Operation.OperationVariable] = inoutput_variable


class RelationshipElement(SubmodelElement):
    """
    It is used to define a relationship between two elements, either referable (reference to the model) or external
    (global reference). Its attributes are:
      - first: first element, which has the role of the subject
      - second: second element, which has the role of the object
    """
    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 first: common.KeyTypes.Reference = None,
                 second: common.KeyTypes.Reference = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 parent=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, parent, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.first: common.KeyTypes.Reference = first
        self.second: common.KeyTypes.Reference = second
