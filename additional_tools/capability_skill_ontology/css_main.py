import asyncio
import sys

from owlready2 import get_ontology

from capability_skill_module import Capability, Skill, CapabilityConstraint


async def print_onto_data(onto):
    print("Classes: {}".format(list(onto.classes())))
    print("Object properties: {}".format(list(onto.object_properties())))
    print("Data properties: {}".format(list(onto.data_properties())))
    print("Annotation properties: {}".format(list(onto.annotation_properties())))
    print("Properties: {}".format(list(onto.properties())))
    print("Namespace (base iri): {}".format(onto.base_iri))

    print("Capability class: {}".format(onto.Capability))
    print("Skill class: {}".format(onto.Skill))
    print("Cap-Skill relationship class: {}".format(onto.isRealizedBy))
    print("SkillInterface class: {}".format(onto.SkillInterface))
    print("CapabilityConstraint class: {}".format(onto.CapabilityConstraint))
    print("Skill-State Machine relationship class: {}".format(onto.behaviorConformsTo))

    print("SMIA AgentCapability class: {}".format(onto.AgentCapability))
    print("SMIA AssetCapability class: {}".format(onto.AssetCapability))
    print("SMIA AssetCapability class: {}".format(onto.hasLifecycle))




async def main():
    print("Program to work with CSS model extended by GCIS")

    # Import only ontologies in RDF/XML, OWL/XML or NTriples format (otros no funciona, como p.e. Turtle)
    onto = get_ontology("CSS-ontology-smia.owl")
    # onto = get_ontology("CSS-Ontology-RDF-XML.owl")
    onto.load()

    await print_onto_data(onto)

    capability1 = Capability("cap1")
    capability1.method()
    capability1.method2()
    # capability1.method3()
    print(capability1)

    capability1.set_lifecycle("OFFER")

    skill1 = Skill("skill1")
    skill1.method_skill()
    print(skill1)

    skill2 = Skill("skill2")
    capability1.isRealizedBy.append(skill1)
    capability1.isRealizedBy.append(skill2)

    cap_constr1 = CapabilityConstraint("cap_constraint1")
    print(cap_constr1)


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
