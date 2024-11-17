from owlready2 import get_ontology, sync_reasoner, Thing


def main():
    onto = get_ontology("Prueba_reasoning.owl").load()

    with onto:
        class Capability(Thing):
            pass
        class Skill(Thing):
            pass
        class NonSkill(Thing):
            pass
        class isRealizedBy(Capability >> Skill):
            # class_property_type = ["only"]
            pass

    print(onto.classes())
    print(onto.Capability)
    cap = onto.Capability("cap1")
    non_skill = NonSkill("non_skill1")
    print(cap)
    skill = onto.Skill()
    print(skill)

    cap.isRealizedBy.append(non_skill)
    print(cap.isRealizedBy)

    print(f"Las clases de capability_instance son: {cap.is_a}")
    print(f"¿Es la instancia de habilidad un Skill? {skill.is_a}")

    with onto:
        sync_reasoner()
    print(non_skill.is_a)
    print(cap.isRealizedBy)



if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    main()