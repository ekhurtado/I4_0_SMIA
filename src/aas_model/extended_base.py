from basyx.aas.model import Qualifier, HasSemantics


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

