import asyncio
import sys

from owlready2 import get_ontology, onto_path, get_namespace

from capability_skill_module import Capability, Skill, CapabilityConstraint


async def print_onto_data(onto):
    print("READING ONTOLOGY:")
    print("-----------------")
    print("Classes: {}".format(list(onto.classes())))
    print("Object properties: {}".format(list(onto.object_properties())))
    print("Data properties: {}".format(list(onto.data_properties())))
    print("Annotation properties: {}".format(list(onto.annotation_properties())))
    print("Properties: {}".format(list(onto.properties())))
    print("Namespace (base iri): {}".format(onto.base_iri))

    obo = onto.get_namespace("http://www.w3id.org/hsu-aut/css#")
    print("Capability class: {}".format(onto.Capability))
    print("Capability class: {}".format(obo.Capability))    # CUIDADO, LA ONTOLOGIA ORIGINAL ESTA EN OTRO NAMESPACE (en el de hsu-aut)
    print("Skill class: {}".format(onto.Skill))
    print("Cap-Skill relationship class: {}".format(onto.isRealizedBy))
    print("SkillInterface class: {}".format(onto.SkillInterface))
    print("CapabilityConstraint class: {}".format(onto.CapabilityConstraint))
    print("Skill-State Machine relationship class: {}".format(onto.behaviorConformsTo))

    print("SMIA AgentCapability class: {}".format(onto.AgentCapability))
    print("SMIA AssetCapability class: {}".format(onto.AssetCapability))
    print("SMIA Capability hasLifecycle attribute: {}".format(onto.hasLifecycle))
    print("-----------------")




async def main():
    print("Program to work with CSS model extended by GCIS")

    # Import only ontologies in RDF/XML, OWL/XML or NTriples format (otros no funciona, como p.e. Turtle)
    onto_path.append("CSS-Ontology-RDF-XML.owl")

    onto = get_ontology("CSS-ontology-smia.owl")
    # onto = get_ontology("CSS-Ontology-RDF-XML.owl")
    # onto = get_ontology("CASK-RDF.owl")
    onto.load()

    await print_onto_data(onto)

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

    print("CAPABILITY capability1 skills: {}".format(capability1.isRealizedBy))




if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
