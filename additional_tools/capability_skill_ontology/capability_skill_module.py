from owlready2 import Thing, get_ontology

css_ontology = get_ontology("CSS-Ontology-module.owl")

with css_ontology:
    class Capability(Thing):


        def method(self):
            print("method of capability")

        def method2(self):
            print("method2 of capability")
