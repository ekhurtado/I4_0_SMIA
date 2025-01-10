import basyx
from basyx.aas.model import Qualifier, HasSemantics, Namespace, Qualifiable

from smia.logic.exceptions import AASModelReadingError


class ExtendedQualifier(Qualifier):
    """This class contains methods to be added to Qualifier class of Basyx Python SDK model."""


class ExtendedHasSemantics(HasSemantics):
    """This class contains methods to be added to HasSemantics class of Basyx Python SDK model."""

    def check_semantic_id_exist(self, semantic_id_reference):
        """
        This method checks if a specific semanticID exists in an AAS meta-model element.

        Args:
            semantic_id_reference (str): semantic identifier.

        Returns:
            bool: result of the check (only True if the semanticID exists).
        """
        if self.semantic_id is None:
            return False
        for reference in self.semantic_id.key:
            if reference.value == semantic_id_reference:
                return True
        return False

    def check_suppl_semantic_id_exist(self, suppl_semantic_id_ref):
        """
        This method checks if a specific supplemental semanticID exists in an AAS meta-model element.

        Args:
            suppl_semantic_id_ref (str): supplemental semantic identifier.

        Returns:
            bool: result of the check (only True if the semanticID exists).
        """
        if self.supplemental_semantic_id is None:
            return False
        for suppl_semantic_id in self.supplemental_semantic_id:
            for reference in suppl_semantic_id.key:
                if reference.value == suppl_semantic_id_ref:
                    return True
            return False


class ExtendedNamespace(Namespace):

    def check_if_element_is_structural(self):
        """
        This method checks whether the AAS element is of type structural (Submodel, SubmodelElementCollection or
        SubmodelElementList).

        Returns:
            bool: result of the check
        """
        if isinstance(self, basyx.aas.model.Submodel) \
                or (isinstance(self, basyx.aas.model.SubmodelElementCollection)
                    or isinstance(self, basyx.aas.model.SubmodelElementList)):
            return True
        else:
            return False


class ExtendedQualifiable(Qualifiable):

    def get_qualifier_value_by_type(self, qualifier_type_value):
        """
        This method gets the value of the qualifier that has a given type.

        Args:
            qualifier_type_value (str): type of the qualifier.

        Returns:
            str: value of the qualifier with the given type
        """
        try:
            qualifier_object = self.get_qualifier_by_type(qualifier_type_value)
            if qualifier_object is None:
                raise AASModelReadingError("Qualifier type {} not found in the element {}".format(
                    qualifier_type_value, self), self, 'KeyError in qualifiers')
            else:
                return qualifier_object.value
        except KeyError as e:
            raise AASModelReadingError("Qualifier type {} not found in the element {}".format(
                qualifier_type_value, self), self, 'KeyError in qualifiers')

    def get_qualifier_value_by_semantic_id(self, qualifier_semantic_id):
        """
        This method gets the value of the qualifier that has a given semanticID.

        Args:
            qualifier_semantic_id (str): semanticID of the qualifier.

        Returns:
            str: value of the qualifier with the given type
        """
        try:
            if len(self.qualifier) == 0:
                raise AASModelReadingError("Qualifier not found in the element {} because the element has no "
                                           "qualifier with semanticID {}.".format(self, qualifier_semantic_id),
                                           self, 'KeyError in qualifiers')
            for qualifier in self.qualifier:
                if qualifier.check_semantic_id_exist(qualifier_semantic_id) is True:
                    return qualifier.value
            else:
                raise AASModelReadingError("Qualifier with semanticID {} not found in the element {}".format(
                    qualifier_semantic_id, self), self, 'SemanticIDError in qualifiers')

        except KeyError as e:
            raise AASModelReadingError("Qualifier with semanticID {} not found in the element {}".format(
                qualifier_semantic_id, self), self, 'KeyError in qualifiers')
