import asyncio
import sys

import owlready2
from owlready2 import get_ontology, onto_path, get_namespace, ThingClass, Ontology, DataPropertyClass, \
    ObjectPropertyClass, sync_reasoner, OwlReadyInconsistentOntologyError, sync_reasoner_pellet, Nothing

import capability_skill_module
from capability_skill_module import Capability, Skill, CapabilityConstraint, SkillInterface
from capability_skill_onto_utils import CapabilitySkillOntologyNS

onto: Ontology = None


async def print_onto_data(namespace):
    print("READING ONTOLOGY:")
    print("-----------------")
    print("Classes: {}".format(list(onto.classes())))
    print("Object properties: {}".format(list(onto.object_properties())))
    print("Data properties: {}".format(list(onto.data_properties())))
    print("Annotation properties: {}".format(list(onto.annotation_properties())))
    print("Properties: {}".format(list(onto.properties())))
    print("Namespace (base iri): {}".format(onto.base_iri))

    await print_onto_ns_data(namespace)
    print("-----------------")


async def print_onto_ns_data(namespace):
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

    await print_onto_data(None)
    await print_onto_ns_data(CapabilitySkillOntologyNS.CSS_NAMESPACE)
    await print_onto_ns_data(CapabilitySkillOntologyNS.CSS_SMIA_NAMESPACE)

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

    owlready2.reasoning.JAVA_MEMORY = 1600  # Necesario para PC laboratorio
    try:
        await execute_ontology_reasoner(debug_value=2)
    except OwlReadyInconsistentOntologyError as e:
        # Parece que hay que validar manualmente, no ofrece el elemento inconsistente (añadiendo debug=2 sí da una explicacion)
        # TODO de momento se elimina manualmente
        print("Removing inconsistent elements...")
        skill1.accessibleThrough.remove(capability1)
        print("Executing reasoner again...")
        await execute_ontology_reasoner(None)


async def crear_clases_desde_iris():
    # TODO las IRIs se recogeran del modelo AAS, de momento se recogen desde un diccionario
    iris_dict = {
        "http://www.w3id.org/hsu-aut/css#Capability": "cap01",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AgentCapability": "agentcap01",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability": "assetcap01",
        "http://www.w3id.org/hsu-aut/css#Skill": "skill01",
        "http://www.w3id.org/hsu-aut/css#SkillInterface": "skillInterface01",
        "http://www.w3id.org/hsu-aut/css#isRealizedBy": "cap01,skill01",
        "http://www.w3id.org/hsu-aut/css#accessibleThrough": "skill01,skillInterface01",
        }

    for iri_found, name in iris_dict.items():
        result_classes = onto.search(iri=iri_found)
        if len(result_classes) == 0:
            print("ERROR: clase no encontrada con IRI [{}]".format(iri_found))
            break
        if len(result_classes) > 1:
            print("HAY MAS DE UNA CLASE CON IRI [{}], CUIDADO".format(iri_found))
        class_generator = result_classes[0]
        if isinstance(class_generator, ThingClass):
            # Al generar una instancia, se almacena directamente en la ontologia
            class_generator(name)
        if isinstance(class_generator, ObjectPropertyClass):
            first_elem = await seek_elem_by_name(name.split(',')[0])
            second_elem = await seek_elem_by_name(name.split(',')[1])
            if first_elem is None or second_elem is None:
                print("ERROR: the relation is not valid")
            else:
                getattr(first_elem, class_generator.name).append(second_elem)

    for i in onto.individuals():
        print("{}: {}".format(i.name, i.is_a))

    try:
        await execute_ontology_reasoner(debug_value=1)
    except OwlReadyInconsistentOntologyError as e:
        print("ERROR...")

    for i in onto.individuals():
        if isinstance(i, Capability):
            i.method()
        if isinstance(i, Skill):
            i.method_skill()
        if isinstance(i, SkillInterface):
            i.method_skill_interface()
        print("Properties of class {}: {}".format(i, i.get_properties()))
        for prop in i.get_properties():
            if 'isRealizedBy' == prop.name:
                print("\tThe capability {} has the skill {}".format(i, i.isRealizedBy))
            if 'accessibleThrough' == prop.name:
                print("\tThe skill {} has the skill interface {}".format(i, i.accessibleThrough))





async def execute_ontology_reasoner(debug_value):
    if debug_value is None:
        debug_value = 1
    try:
        with onto:
            sync_reasoner_pellet(debug=debug_value)
    except OwlReadyInconsistentOntologyError as e:
        print("ERROR: INCONSISTENT ONTOLOGY!")
        print(e)
        raise OwlReadyInconsistentOntologyError(e)

async def seek_elem_by_name(name):
    for owl_class in onto.individuals():
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
