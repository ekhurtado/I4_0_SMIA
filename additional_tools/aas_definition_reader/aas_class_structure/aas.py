"""
This module contains the class for the implementation of the Asset Administration Shell.
"""
from enum import Enum, unique
from typing import Iterable

from . import common, _string_constraints
from .submodel import Submodel


@_string_constraints.constrain_identifier("asset_type")
# The decorator @_string_constraints.constrain_identifier("asset_type") in the AssetInformation class in the aas.py
# file is used to enforce certain constraints on the asset_type attribute of the AssetInformation class (in this case
# "check_identifier" is used so the asset_type value must have a minimum length of 1 and a maximum length of 2000)
class AssetInformation:
    """
    This class collects the meta-information of the asset being represented. The asset can be either a type or an
    instance. The asset has a globally unique identifier and, if needed, an additional domain-specific identifier.

    **Constraint AASd-131:**  The globalAssetId or at least one specificAssetId shall be defined for AssetInformation. (TODO comprobar que funciona)

    Attributes:
        asset_kind (AssetKind): Indicates whether the asset is of :class:`AssetKind` ``TYPE`` or ``INSTANCE``. The default is ``INSTANCE``.
        specific_asset_id (common.SpecificAssetId): Additional domain-specific, typically proprietary identifier (Set of  :class:`SpecificAssetIds <common.SpecificAssetId>` for the asset as e.g. serial number, etc.
        TODO finalizarlo
    """

    @unique
    class AssetKind(Enum):
        TYPE = 0
        INSTANCE = 1
        NOT_APPLICABLE = 2

    @unique
    class AssetType(Enum):
        """
        This class is an own proposal to distinguish between logical and physical assets. The asset type are defined in
        IEC 63278-1:2024 standard.
        """
        PHYSICAL = 0
        DIGITAL = 1
        INTANGIBLE = 2
        NOT_APPLICABLE = 3

    class Resource:
        """This class represents an address to a file, either in absolute or relative path."""

        def __init__(self):
            self.path = None
            self.content_type = None

    def __init__(self,
                 asset_kind: AssetKind = AssetKind.INSTANCE,
                 specific_asset_id: Iterable[common.SpecificAssetId] = (),  # It is used Iterable instead of set to provide flexibility (can accept any iterable type, not only sets)
                 global_asset_id: common.KeyTypes.Reference = None,
                 default_thumbnail: Resource = None,
                 asset_type: AssetType = None,
                 ):
        super().__init__()
        self.asset_kind: AssetInformation.AssetKind = asset_kind
        self.specific_asset_id: Iterable[common.SpecificAssetId] = specific_asset_id
        self.global_asset_id: common.KeyTypes.Reference = global_asset_id
        self.default_thumbnail: AssetInformation.Resource = default_thumbnail
        self.asset_type: AssetInformation.AssetType = asset_type

    def cascade_print(self, depth_level):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the asset.
        :param depth_level: this attribute sets the depth level to print correctly on the console.
        """
        depth_string = "    " * depth_level
        print(depth_string + "\_ Asset information: ")
        print(depth_string + "    asset_kind: " + str(self.asset_kind.name))
        print(depth_string + "    specific_asset_id: " + str(self.specific_asset_id))
        print(depth_string + "    global_asset_id: " + str(self.global_asset_id))
        print(depth_string + "    default_thumbnail: " + str(self.default_thumbnail))
        print(depth_string + "    asset_type: " + str(self.asset_type.name))


class AssetAdministrationShell(common.Identifiable, common.HasDataSpecification):
    """
    An AAS is uniquely identifiable because it inherits from :param: Identifiable. As it inherits from both :param:
    Identifiable (and this in turn from :param: Referable) and :param: HasDataSpecification, all these inherited
    variables are added in the constructor of the AAS.
    """

    def __init__(self,
                 asset_information: AssetInformation,
                 id_: common.KeyTypes.Identifier,
                 id_short,
                 display_name,
                 category,
                 description,
                 administration: common.Identifiable.AdministrativeInformation,
                 submodel: set[Submodel],
                 derived_from,
                 embedded_data_specifications,
                 extension):
        super().__init__()
        self.id: common.KeyTypes.Identifier = id_
        self.asset_information: AssetInformation = asset_information
        self.id_short = id_short
        self.display_name = display_name
        self.category = category
        self.description = description
        self.administration: common.Identifiable.AdministrativeInformation = administration
        self.derived_from = derived_from
        self.submodel = set() if submodel is None else submodel
        self.embedded_data_specifications = embedded_data_specifications
        self.extension = extension

    def cascade_print(self):
        """
        This method is developed on each element of the AAS meta-model to print its specific information. In this
        case, this method prints the information of the AAS. SSince the AAS is the main element, this method does not
        have a depth level, something that the cascading methods within the other elements do have, which is initially
        set by this first cascading print.

        For each attribute of the AAS the information is printed directly or, in the case where the attribute is an AAS
        meta-model element, its cascade print method is called.
        """

        print("\_ AAS information: ")
        print("    id: " + str(self.id))
        self.asset_information.cascade_print(depth_level=1)
        print("    id_short: " + str(self.id_short))
        print("    display_name: " + str(self.display_name))
        print("    category: " + str(self.category))
        print("    description: " + str(self.description))
        if self.administration is not None:
            self.administration.cascade_print(depth_level=1)
        print("    derived_from: " + str(self.derived_from))
        print("    \_ Submodels:")
        for submodel in self.submodel:
            submodel.cascade_print(depth_level=2)
        print("        embedded_data_specifications: " + str(self.embedded_data_specifications))
        print("        extension: " + str(self.extension))
