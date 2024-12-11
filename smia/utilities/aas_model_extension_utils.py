from basyx.aas.model import AssetAdministrationShell, AssetInformation, Submodel, SubmodelElement, RelationshipElement, \
    AnnotatedRelationshipElement, Capability, Operation, BasicEventElement, Entity, SubmodelElementList, \
    SubmodelElementCollection, Property, MultiLanguageProperty, Range, Blob, File, ReferenceElement, \
    ConceptDescription, Qualifier, HasSemantics, Namespace, Qualifiable


class AASModelExtensionUtils:
    """
    This class contains utility methods related to the extension of the BaSyx Python SDK AAS model.
    """

    @staticmethod
    def extend_basyx_aas_model():

        # The libraries are imported locally to avoid circular import error
        from aas_model.extended_aas import ExtendedAssetAdministrationShell ,ExtendedAssetInformation
        from aas_model.extended_base import ExtendedQualifier, ExtendedHasSemantics, ExtendedNamespace, \
            ExtendedQualifiable
        from aas_model.extended_concept_description import ExtendedConceptDescription
        from aas_model.extended_submodel import ExtendedSubmodel, ExtendedSubmodelElement, ExtendedRelationshipElement, \
            ExtendedAnnotatedRelationshipElement, ExtendedCapability, ExtendedOperation, ExtendedBasicEventElement, \
            ExtendedEntity, ExtendedSubmodelElementList, ExtendedSubmodelElementCollection, ExtendedProperty, \
            ExtendedMultiLanguageProperty, ExtendedRange, ExtendedBlob, ExtendedFile, ExtendedReferenceElement


        all_extension_classes_map = {AssetAdministrationShell: ExtendedAssetAdministrationShell,
                                     AssetInformation: ExtendedAssetInformation,
                                     Submodel: ExtendedSubmodel,
                                     SubmodelElement: ExtendedSubmodelElement,
                                     RelationshipElement: ExtendedRelationshipElement,
                                     AnnotatedRelationshipElement: ExtendedAnnotatedRelationshipElement,
                                     Capability: ExtendedCapability,
                                     Operation: ExtendedOperation,
                                     BasicEventElement: ExtendedBasicEventElement,
                                     Entity: ExtendedEntity,
                                     SubmodelElementList: ExtendedSubmodelElementList,
                                     SubmodelElementCollection: ExtendedSubmodelElementCollection,
                                     Property: ExtendedProperty,
                                     MultiLanguageProperty: ExtendedMultiLanguageProperty,
                                     Range: ExtendedRange,
                                     Blob: ExtendedBlob,
                                     File: ExtendedFile,
                                     ReferenceElement: ExtendedReferenceElement,
                                     ConceptDescription: ExtendedConceptDescription,
                                     Qualifier: ExtendedQualifier,
                                     HasSemantics: ExtendedHasSemantics,
                                     Namespace: ExtendedNamespace,
                                     Qualifiable: ExtendedQualifiable
                                     }
        for model_class, extension_class in all_extension_classes_map.items():
            for method_name in dir(extension_class):
                if callable(getattr(extension_class, method_name)) and not method_name.startswith("__"):
                    # Special methods (e.g., __init__) are excluded.
                    setattr(model_class, method_name, getattr(extension_class, method_name))

