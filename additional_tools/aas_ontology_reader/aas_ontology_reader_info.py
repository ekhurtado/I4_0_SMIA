import abc


class ExtendedClasses:
    class ExtendedGenericCSSClass(metaclass=abc.ABCMeta):

        def add_old_sme_class(self, sme_class):
            """
            This method adds the old Basyx SubmodelElement class to be stored to the correct execution of the software.

            Args:
                sme_class (basyx.aas.model.SubmodelElement): old submodel element class in BaSyx Python structure.
            """
            self.old_sme_class = sme_class

    class ExtendedCapability(ExtendedGenericCSSClass):
        pass

    class ExtendedSkill(ExtendedGenericCSSClass):
        pass

    class ExtendedSkillInterface(ExtendedGenericCSSClass):
        pass


class AASOntologyReaderInfo:
    """
    This class contains the configuration of the AAS Ontology Reader. To read an AAS model with a specific ontology,
     it is necessary to modify these variables.
    """

    CSS_ONTOLOGY_CAPABILITY_IRI = 'http://www.w3id.org/hsu-aut/css#Capability'
    CSS_ONTOLOGY_SKILL_IRI = 'http://www.w3id.org/hsu-aut/css#Skill'
    CSS_ONTOLOGY_SKILL_INTERFACE_IRI = 'http://www.w3id.org/hsu-aut/css#SkillInterface'

    CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI = 'http://www.w3id.org/hsu-aut/css#isRealizedBy'
    CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI = 'http://www.w3id.org/hsu-aut/css#accessibleThrough'


    # Ontology class identifiers to be found in the AAS model (IRIs in OWL)
    CSS_ONTOLOGY_THING_CLASSES_IRIS = [CSS_ONTOLOGY_CAPABILITY_IRI,
                                       CSS_ONTOLOGY_SKILL_IRI,
                                       CSS_ONTOLOGY_SKILL_INTERFACE_IRI,
                                       ]

    # Identifiers for the relations between ontology classes (Object Properties in OWL)
    CSS_ONTOLOGY_OBJECT_PROPERTIES_IRIS = [CSS_ONTOLOGY_PROP_ISREALIZEDBY_IRI,
                                           CSS_ONTOLOGY_PROP_ACCESSIBLETHROUGH_IRI,
                                           ]

    # The relations between the BaSyx SDK AAS classes and extended classes for specific ontologies
    CSS_ONTOLOGY_AAS_MODEL_LINK = {
        CSS_ONTOLOGY_CAPABILITY_IRI: ExtendedClasses.ExtendedCapability,
        CSS_ONTOLOGY_SKILL_IRI: ExtendedClasses.ExtendedSkill,
        CSS_ONTOLOGY_SKILL_INTERFACE_IRI: ExtendedClasses.ExtendedSkillInterface,
    }