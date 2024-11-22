import asyncio

import owlready2
from owlready2 import ThingClass, ObjectPropertyClass, OwlReadyInconsistentOntologyError

from css_ontology.capability_skill_module import Capability, Skill, CapabilityConstraint, SkillInterface
from capability_skill_onto_utils import CapabilitySkillOntologyInfo
from capability_skill_ontology import CapabilitySkillOntology

ontology_class: CapabilitySkillOntology = None


async def primeras_pruebas():

    await ontology_class.print_onto_data(None)
    await ontology_class.print_onto_ns_data(CapabilitySkillOntologyInfo.CSS_NAMESPACE)
    await ontology_class.print_onto_ns_data(CapabilitySkillOntologyInfo.CSS_SMIA_NAMESPACE)

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
    skill1.accessibleThrough.append(capability1)    # TODO RELACION INVALIDA !
    print("SKILL INTERFACE: {}".format(skill_interface1))

    print("CAPABILITY capability1 skills: {}".format(capability1.isRealizedBy))
    print("SKILL skill1 skill interfaces: {}".format(skill1.accessibleThrough))

    owlready2.reasoning.JAVA_MEMORY = 1200  # Necesario para PC laboratorio
    try:
        await ontology_class.execute_ontology_reasoner(debug=True)
    except OwlReadyInconsistentOntologyError as e:
        # Parece que hay que validar manualmente, no ofrece el elemento inconsistente (añadiendo debug=2 sí da una explicacion)
        # TODO de momento se elimina manualmente
        print("Removing inconsistent elements...")
        skill1.accessibleThrough.remove(capability1)
        print("Executing reasoner again...")
        await ontology_class.execute_ontology_reasoner()
        print("Now the ontology is consistent!")
        print("------------------------------")


async def crear_clases_desde_iris():
    # TODO las IRIs se recogeran del modelo AAS, de momento se recogen desde un diccionario
    iris_dict = {
        "http://www.w3id.org/hsu-aut/css#Capability": "cap01",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AgentCapability": "agentcap01",
        "http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability": "assetcap01",
        "http://www.w3id.org/hsu-aut/css#Skill": "skill01",
        "http://www.w3id.org/hsu-aut/css#SkillInterface": "skillInterface01",
        # "http://www.w3id.org/hsu-aut/css#isRealizedBy": "cap01,skill01",
        "http://www.w3id.org/hsu-aut/css#isRealizedBy": "cap01,cap1",   # TODO RELACION INVALIDA !
        "http://www.w3id.org/hsu-aut/css#accessibleThrough": "skill01,skillInterface01",
        "http://www.w3id.org/hsu-aut/css#accessibleThrough": "skill01,skill1",   # TODO RELACION INVALIDA !
        }

    print("Creating ontology instances from dictionary data...")
    for iri_found, name in iris_dict.items():
        class_generator = await ontology_class.get_ontology_class_by_iri(iri_found)
        if isinstance(class_generator, ThingClass):
            # Al generar una instancia, se almacena directamente en la ontologia
            # class_generator(name)
            created_instance = await ontology_class.create_ontology_object_instance(class_generator, name)
            if isinstance(created_instance, Capability):
                created_instance.set_lifecycle("OFFER")
        if isinstance(class_generator, ObjectPropertyClass):
            await ontology_class.add_object_property_to_instances_by_iris(class_generator, name.split(',')[0], name.split(',')[1])

    try:
        print("Analyzing ontology with new instances...")
        await ontology_class.execute_ontology_reasoner(debug=True)
    except OwlReadyInconsistentOntologyError as e:
        print("ERROR: the new ontology instances has not been added properly. The created instances need to be checked.")
        for name in iris_dict.values():
            await ontology_class.check_instance_by_name(name)
        await ontology_class.execute_ontology_reasoner(debug=True)

    skill1 = await ontology_class.seek_instance_by_name('skill1')
    print("skill1 sigue siendo solo del tipo 'Skill'? {}\n".format(skill1.is_a))

    # LEYENDO LAS INSTANCIAS CREADAS...
    print("READING ONTOLOGY INSTANCES...")
    for i in ontology_class.ontology.individuals():
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

    print("\nGetting the IRIs of a given class and subclasses...")
    capability_class = await ontology_class.get_class_by_name('Capability')
    print("IRI of Capability class: {}".format(capability_class.iri))
    for subclass in await ontology_class.get_all_subclasses_of_class(capability_class):
        print("IRI of subclass {} class: {}".format(subclass.name,subclass.iri))





async def main():
    print("Program to work with CSS model extended by GCIS")

    global ontology_class
    ontology_class = CapabilitySkillOntology()
    await ontology_class.initialize_ontology()

    await primeras_pruebas()

    await crear_clases_desde_iris()


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
