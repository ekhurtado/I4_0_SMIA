from basyx.aas.model import ConceptDescription


class ExtendedConceptDescription(ConceptDescription):
    """This class contains methods to be added to ConceptDescription class of Basyx Python SDK model."""

    def print_concept_description_information(self):
        print("Concept Description information:")
        print("\tid: {}".format(self.id))
        print("\tid_short: {}".format(self.id_short))
        print("\tdisplayName: {}".format(self.display_name))
        print("\tdescription: {}".format(self.description))
        print("\tcategory: {}".format(self.category))
        for embedded_ds in self.embedded_data_specifications:
            print("\tdataSpecification ref: {}".format(embedded_ds.data_specification))
            print("\tdataSpecification content:")
            print("\t\tpreferredName: {}".format(embedded_ds.data_specification_content.preferred_name))
            print("\t\tdefinition: {}".format(embedded_ds.data_specification_content.definition))

