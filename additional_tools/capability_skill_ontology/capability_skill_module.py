from owlready2 import Thing, get_ontology

css_ontology = get_ontology("path/to/owl_file")

with css_ontology:
    class Capability(Thing):
        def method(self):
            print("method pf capability")