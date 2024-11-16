import asyncio

from owlready2 import get_ontology, Thing

import capability_skill_module


async def print_onto_data(onto):
    print("Classes: {}".format(list(onto.classes())))
    print("Object properties: {}".format(list(onto.object_properties())))
    print("Data properties: {}".format(list(onto.data_properties())))
    print("Annotation properties: {}".format(list(onto.annotation_properties())))
    print("Properties: {}".format(list(onto.properties())))
    print("Namespace (base iri): {}".format(onto.base_iri))


async def main():
    print("Program to work with CSS model extended by GCIS")

    # Import only ontologies in RDF/XML, OWL/XML or NTriples format (otros no funciona, como p.e. Turtle)
    onto = get_ontology("CSS-Ontology-module.owl")
    onto.load()
    await print_onto_data(onto)

    capability1 = onto.Capability()
    capability1.method()
    capability1.method2()

    capability1 = onto.Skill()
    capability1.method3()
    print(capability1)


if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    asyncio.run(main())
