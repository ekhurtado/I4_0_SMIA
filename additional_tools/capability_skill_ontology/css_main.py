import asyncio
import sys

from owlready2 import get_ontology, onto_path, get_namespace

from capability_skill_module import Capability, Skill, CapabilityConstraint, SkillInterface
from capability_skill_onto_utils import CapabilitySkillOntologyNS


async def print_onto_data(onto, namespace):
    print("READING ONTOLOGY:")
    print("-----------------")
    print("Classes: {}".format(list(onto.classes())))
    print("Object properties: {}".format(list(onto.object_properties())))
    print("Data properties: {}".format(list(onto.data_properties())))
    print("Annotation properties: {}".format(list(onto.annotation_properties())))
    print("Properties: {}".format(list(onto.properties())))
    print("Namespace (base iri): {}".format(onto.base_iri))

    await print_onto_ns_data(onto, namespace)
    print("-----------------")


async def print_onto_ns_data(onto, namespace):
    if namespace:
        ns = onto.get_namespace(namespace)
    else:
        # El namespace por defecto es SMIA en esta ontologia
        # TODO si mas adelante dejamos definir otras ontologias extendidas de la nuestra, esto habria que cambiarlo
        ns = onto

    print("Ontology namespace data:")
    print("\tCapability class: {}".format(ns.Capability))
    print("\tSkill class: {}".format(ns.Skill))
    print("\tCap-Skill relationship class: {}".format(ns.isRealizedBy))
    print("\tSkillInterface class: {}".format(ns.SkillInterface))
    print("\tCapabilityConstraint class: {}".format(ns.CapabilityConstraint))
    print("\tSkill-State Machine relationship class: {}".format(ns.behaviorConformsTo))

    print("\tSMIA AgentCapability class: {}".format(ns.AgentCapability))
    print("\tSMIA AssetCapability class: {}".format(ns.AssetCapability))
    print("\tSMIA Capability hasLifecycle attribute: {}".format(ns.hasLifecycle))
    print()


async def main():
    print("Program to work with CSS model extended by GCIS")

    # Import only ontologies in RDF/XML, OWL/XML or NTriples format (otros no funciona, como p.e. Turtle)
    onto = get_ontology("CSS-ontology-smia.owl")
    # onto = get_ontology("CSS-Ontology-RDF-XML.owl")
    # onto = get_ontology("CASK-RDF.owl")
    onto.load()

    await print_onto_data(onto, None)
    await print_onto_ns_data(onto, CapabilitySkillOntologyNS.CSS_NAMESPACE)
    await print_onto_ns_data(onto, CapabilitySkillOntologyNS.CSS_SMIA_NAMESPACE)

    # CREATING CAPABILITIES
    capability1 = Capability("cap1")
    capability1.method()
    capability1.method2()
    # capability1.method3()
    print("CAPABILITY: {}".format(capability1))

    capability1.set_lifecycle("OFFER")

    cap_constr1 = CapabilityConstraint("cap_constraint1")
    print("CAPABILITY CONSTRAINT: {}".format(cap_constr1))
    print("CAPABILITY capability1 related constraints: {}".format(capability1.isRestrictedBy))
    capability1.isRestrictedBy.append(cap_constr1)
    print("CAPABILITY capability1 updated constraints: {}".format(capability1.isRestrictedBy))

    # CREATING SKILLS
    skill1 = Skill("skill1")
    skill1.method_skill()
    print("SKILL: {}".format(skill1))

    skill2 = Skill("skill2")
    capability1.isRealizedBy.append(skill1)
    capability1.isRealizedBy.append(skill2)
    print("SKILL: {}".format(skill2))

    skill_interface1 = SkillInterface("skillInterface1")
    skill1.accessibleThrough.append(capability1)
    print("SKILL INTERFACE: {}".format(skill_interface1))

    print("CAPABILITY capability1 skills: {}".format(capability1.isRealizedBy))
    print("SKILL skill1 skill interfaces: {}".format(skill1.accessibleThrough))




if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
