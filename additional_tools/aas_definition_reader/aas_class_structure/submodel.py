"""
This module contains the class for the implementation of the Submodel and related classes.
"""
import abc
from enum import unique, Enum

from . import common


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
        self.semantic_id: common.KeyTypes.Reference = semantic_id
        self.qualifier: common.Qualifier = qualifier
        self.extension: common.Extension = extension
        self.supplemental_semantic_id: set[common.KeyTypes.Reference] = set(supplemental_semantic_id)
        self.embedded_data_specifications = embedded_data_specifications

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Submodel Element.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Submodel element:")
        self.print_sm_element_common_variables(depth_level)

    def print_sm_element_common_variables(self, depth_level):
        """
        This method prints only information of the Submodel Element, i.e. its attributes. By printing only the
        attributes data, this method can be used by any type of submodel element to print the common information shared
        by all these types of elements (DataElement, Property...).
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "    id_short: " + str(self.id_short))
        print(depth_string + "    display_name: " + str(self.display_name))
        print(depth_string + "    category: " + str(self.category))
        print(depth_string + "    description: " + str(self.description))
        print(depth_string + "    semantic_id: " + str(self.semantic_id))
        if self.qualifier is not None:
            self.qualifier.cascade_print(depth_level=depth_level + 1)
        else:
            print(depth_string + "    qualifier: None")
        print(depth_string + "    supplemental_semantic_id: " + str(self.supplemental_semantic_id))
        print(depth_string + "    embedded_data_specifications: " + str(self.embedded_data_specifications))


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

    def __init__(self,
                 id_: common.KeyTypes.Identifier,
                 submodel_element: set[SubmodelElement] = (),
                 id_short: common.KeyTypes.NameType = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 administration: common.Identifiable.AdministrativeInformation = None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: set[common.Qualifier] = (),
                 kind: common.HasKind.ModelingKind = None,
                 extension: set[common.Extension] = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__()
        self.id: common.KeyTypes.Identifier = id_
        self.submodel_element: set[SubmodelElement] = submodel_element
        self.id_short: common.KeyTypes.NameType = id_short
        self.display_name = display_name
        self.category = category
        self.description = description
        self.administration: common.Identifiable.AdministrativeInformation = administration
        self.semantic_id: common.KeyTypes.Reference = semantic_id
        self.qualifier: set[common.Qualifier] = qualifier
        self.kind: common.HasKind.ModelingKind = kind
        self.extension: set[common.Extension] = extension
        self.supplemental_semantic_id: set[common.KeyTypes.Reference] = supplemental_semantic_id
        self.embedded_data_specifications = embedded_data_specifications

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Submodel.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Submodel: ")
        print(depth_string + "    id: " + str(self.id))
        print(depth_string + "    \_ Submodel elements:")
        for sm_element in self.submodel_element:
            sm_element.cascade_print(depth_level + 2)
        print(depth_string + "    id_short: " + str(self.id_short))
        print(depth_string + "    display_name: " + str(self.display_name))
        print(depth_string + "    category: " + str(self.category))
        print(depth_string + "    description: " + str(self.description))
        if self.administration is not None:
            self.administration.cascade_print(depth_level=depth_level + 1)
        else:
            print(depth_string + "    administration: None")
        print(depth_string + "    semantic_id: " + str(self.semantic_id))
        if self.qualifier is not None:
            for qualifier in self.qualifier:
                qualifier.cascade_print(depth_level=depth_level + 1)
        else:
            print(depth_string + "    qualifier: None")
        print(depth_string + "    kind: " + str(self.kind.name))
        print(depth_string + "    extension: " + str(self.extension))
        print(depth_string + "    supplemental_semantic_id: " + str(self.supplemental_semantic_id))
        print(depth_string + "    embedded_data_specifications: " + str(self.embedded_data_specifications))


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
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Data Element. Since DataElement is a SubmodelElement, it uses
        the ``print_sm_element_common_variables`` method of the inherited class to print the common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Data element:")
        super().print_sm_element_common_variables(depth_level)


# -------------------
# Data element types
# -------------------
class Property(DataElement):
    """It is a Data Element that has a unique value. """

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
        self.value = value
        self.value_id: common.KeyTypes.Reference = value_id

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Property. Since Property is a SubmodelElement, it uses
        the ``print_sm_element_common_variables`` method of the inherited class to print the common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Property:")
        print(depth_string + "    value_type: " + str(self.value_type))
        print(depth_string + "    value: " + str(self.value))
        print(depth_string + "    value_id: " + str(self.value_id))
        super().print_sm_element_common_variables(depth_level)


class Range(DataElement):
    """It is a Data Element that defines a range with a minimum and maximum. """

    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_type,
                 min_=None,
                 max_=None,
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
        self.min = min_
        self.max = max_

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Range element. Since Range is a DataElement, and, hence, a
        SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Range:")
        print(depth_string + "    value_type: " + str(self.value_type))
        print(depth_string + "    min: " + str(self.min))
        print(depth_string + "    max: " + str(self.max))
        super().print_sm_element_common_variables(depth_level)


class Blob(DataElement):
    """
    A Blob, or a Binary Large Object, a data element that represents a file that is contained with its source code.
    """

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

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Blob element. Since Blob is a DataElement, and, hence, a
        SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Blob:")
        print(depth_string + "    value_type: " + str(self.value_type))
        print(depth_string + "    content_type: " + str(self.content_type))
        super().print_sm_element_common_variables(depth_level)


class File(DataElement):
    """
    It is a Data Element that represents an address to a file. The value is a URI that can represent an absolute or
    relative path.
    """

    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_: common.KeyTypes.PathType = None,
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
        self.value: common.KeyTypes.PathType = value_
        self.content_type: common.KeyTypes.ContentType = content_type

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the File element. Since File is a DataElement, and, hence, a
        SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ File:")
        print(depth_string + "    value: " + str(self.value))
        print(depth_string + "    content_type: " + str(self.content_type))
        super().print_sm_element_common_variables(depth_level)


class ReferenceElement(DataElement):
    """
    It is a Data Element that defines a logical reference to another element within the same or another AAS or a
    reference to an external object or entity. Its single value attribute contains the global reference to that element.
    """

    def __init__(self,
                 id_short: common.KeyTypes.NameType,
                 value_: common.KeyTypes.Reference = None,
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
        self.value: common.KeyTypes.Reference = value_

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Reference Element. Since ReferenceElement is a DataElement, and,
        hence, a SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to
        print the common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Reference element:")
        print(depth_string + "    value: " + str(self.value))
        super().print_sm_element_common_variables(depth_level)



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
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.order_relevant = order_relevant
        self.semantic_id_list_element = semantic_id_list_element
        self.type_value_list_element = type_value_list_element
        self.value_type_list_element = value_type_list_element
        self.value = value_

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Submodel Element List. Since SubmodelElementList is a
        SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Submodel element list:")
        print(depth_string + "    order_relevant: " + str(self.order_relevant))
        print(depth_string + "    semantic_id_list_element: " + str(self.semantic_id_list_element))
        print(depth_string + "    type_value_list_element: " + str(self.type_value_list_element))
        print(depth_string + "    value_type_list_element: " + str(self.value_type_list_element))
        print(depth_string + "    values list: ")
        for sm_element in self.value:
            sm_element.cascade_print(depth_level + 2)
        super().print_sm_element_common_variables(depth_level)


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
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.value = value_

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Submodel Element Collection. Since SubmodelElementCollection is
        a SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Submodel element list:")
        print(depth_string + "    values list: ")
        for sm_element in self.value:
            sm_element.cascade_print(depth_level + 2)
        super().print_sm_element_common_variables(depth_level)


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
                 specific_asset_id: common.SpecificAssetId = None,
                 display_name=None,
                 category: common.KeyTypes.NameType = None,
                 description=None,
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.statement: set[SubmodelElement] = statement
        self.entity_type: Entity.EntityType = entity_type
        self.global_asset_id: common.KeyTypes.Reference = global_asset_id
        self.specific_asset_id: common.SpecificAssetId = specific_asset_id

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Entity. Since Entity is a SubmodelElement, it uses
        the ``print_sm_element_common_variables`` method of the inherited class to print the common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Entity:")
        print(depth_string + "    entity_type: " + str(self.entity_type.name))
        if self.statement is not None:
            print(depth_string + "    statement: ")
            for statement_elem in self.statement:
                statement_elem.cascade_print(depth_level + 2)
        else:
            print(depth_string + "    statement: None")
        print(depth_string + "    global_asset_id: " + str(self.global_asset_id))
        if self.specific_asset_id is not None:
            print(depth_string + "    specific_asset_id: " + str(self.specific_asset_id.name))
        else:
            print(depth_string + "    specific_asset_id: None")
        super().print_sm_element_common_variables(depth_level)


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
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.input_variable: set[Operation.OperationVariable] = input_variable
        self.output_variable: set[Operation.OperationVariable] = output_variable
        self.inoutput_variable: set[Operation.OperationVariable] = inoutput_variable

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Operation. Since Operation is a SubmodelElement, it uses
        the ``print_sm_element_common_variables`` method of the inherited class to print the common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Operation:")
        if self.input_variable is not None:
            print(depth_string + "    input_variables: ")
            for input_var in self.input_variable:
                input_var.value.cascade_print(depth_level + 2)
        else:
            print(depth_string + "    input_variable: None")
        if self.output_variable is not None:
            print(depth_string + "    output_variable: ")
            for output_var in self.output_variable:
                output_var.value.cascade_print(depth_level + 2)
        else:
            print(depth_string + "    output_variable: None")
        if self.inoutput_variable is not None:
            print(depth_string + "    inoutput_variable: ")
            for inoutput_var in self.inoutput_variable:
                inoutput_var.value.cascade_print(depth_level + 2)
        else:
            print(depth_string + "    inoutput_variable: None")
        super().print_sm_element_common_variables(depth_level)


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
                 semantic_id: common.KeyTypes.Reference = None,
                 qualifier: common.Qualifier = (),
                 extension: common.Extension = (),
                 supplemental_semantic_id: set[common.KeyTypes.Reference] = (),
                 embedded_data_specifications=()):
        super().__init__(id_short, display_name, category, description, semantic_id, qualifier, extension,
                         supplemental_semantic_id, embedded_data_specifications)
        self.first: common.KeyTypes.Reference = first
        self.second: common.KeyTypes.Reference = second

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the Relationship Element. Since RelationshipElement is a
        SubmodelElement, it uses the ``print_sm_element_common_variables`` method of the inherited class to print the
        common attribute data.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Relationship element:")
        print(depth_string + "    first: " + str(self.first))
        print(depth_string + "    second: " + str(self.second))
        super().print_sm_element_common_variables(depth_level)
