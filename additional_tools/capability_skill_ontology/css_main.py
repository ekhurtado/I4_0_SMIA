import asyncio
import sys

from owlready2 import get_ontology, onto_path, get_namespace, ThingClass, Ontology, DataPropertyClass, \
    ObjectPropertyClass, sync_reasoner

from capability_skill_module import Capability, Skill, CapabilityConstraint, SkillInterface
from capability_skill_onto_utils import CapabilitySkillOntologyNS

onto: Ontology = None


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


async def primeras_pruebas():
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
    # skill1.accessibleThrough.append(capability1)
    print("SKILL INTERFACE: {}".format(skill_interface1))

    print("CAPABILITY capability1 skills: {}".format(capability1.isRealizedBy))
    print("SKILL skill1 skill interfaces: {}".format(skill1.accessibleThrough))

    # with onto:
    #     sync_reasoner()


async def crear_clases_desde_iris():
    # TODO las IRIs se recogeran del modelo AAS, de momento se recogen desde un diccionario
    iris_dict = {
        "http://www.w3id.org/hsu-aut/css#Capability": "cap1",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AgentCapability": "agentcap1",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability": "assetcap1",
        "http://www.w3id.org/hsu-aut/css#Skill": "skill1",
        "http://www.w3id.org/hsu-aut/css#SkillInterface": "skillInterface1",
        "http://www.w3id.org/hsu-aut/css#isRealizedBy": "cap1,skill1",
        "http://www.w3id.org/hsu-aut/css#accessibleThrough": "skill1,skillInterface1",
        }

    generated_classes = []

    for iri_found, name in iris_dict.items():
        result_classes = onto.search(iri=iri_found)
        if len(result_classes) == 0:
            print("ERROR: clase no encontrada con IRI [{}]".format(iri_found))
            break
        if len(result_classes) > 1:
            print("HAY MAS DE UNA CLASE CON IRI [{}], CUIDADO".format(iri_found))
        class_generator = result_classes[0]
        if isinstance(class_generator, ThingClass):
            # TODO de momento se añade directamente en el diccionario
            generated_classes.append(class_generator(name))
        if isinstance(class_generator, ObjectPropertyClass):
            first_elem = await seek_elem_by_name(generated_classes, name.split(',')[0])
            second_elem = await seek_elem_by_name(generated_classes, name.split(',')[1])
            getattr(first_elem, class_generator.name).append(second_elem)
    print(generated_classes)
    for i in generated_classes:
        print("Properties of class {}: {}".format(i, i.get_properties()))
        for prop in i.get_properties():
            if 'isRealizedBy' == prop.name:
                print("\tThe capability {} has the skill {}".format(i, i.isRealizedBy))
            if 'accessibleThrough' == prop.name:
                print("\tThe skill {} has the skill interface {}".format(i, i.accessibleThrough))

    with onto:
        sync_reasoner()


async def seek_elem_by_name(generated_classes, name):
    for owl_class in generated_classes:
        if owl_class.name == name:
            return owl_class
    return None

async def main():
    print("Program to work with CSS model extended by GCIS")

    # Import only ontologies in RDF/XML, OWL/XML or NTriples format (otros no funciona, como p.e. Turtle)
    global onto
    onto = get_ontology("CSS-ontology-smia.owl")
    # onto = get_ontology("CSS-Ontology-RDF-XML.owl")
    # onto = get_ontology("CASK-RDF.owl")
    onto.load()

    await primeras_pruebas()

    await crear_clases_desde_iris()


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
