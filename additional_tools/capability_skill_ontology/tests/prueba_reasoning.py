from owlready2 import get_ontology, sync_reasoner, Thing, OwlReadyInconsistentOntologyError


def main():
    onto = get_ontology("CSS-ontology-smia.owl").load()
    # onto = get_ontology("CSS-Ontology-RDF-XML.owl").load()
    # onto = get_ontology("Prueba_reasoning.owl").load()

    print(list(onto.classes()))
    print(list(onto.properties()))
    print(onto.Capability)
    cap = onto.Capability("cap1")
    non_skill = onto.Capability("non_skill1")
    print(cap)
    skill = onto.Skill("skill1")
    print(skill)

    skill_int = onto.SkillInterface("skillint1")

    print(f"Las clases de capability_instance son: {cap.is_a}")
    print(f"¿Es la instancia de habilidad un Skill? {skill.is_a}")
    print(f"¿Es la instancia de un Skill Interface? {skill_int.is_a}")
    print("IRIs. Capability [{}], Skill [{}]".format(cap.iri, skill.iri))

    cap.isRealizedBy.append(non_skill)
    skill.accessibleThrough.append(non_skill)
    # cap.isRealizedBySkill.append(skill)
    print(cap.isRealizedBy)

    cap.method()
    # non_skill.method_skill()

    agent_cap = onto.AgentCapability("cap2")
    agent_cap.isRealizedBy.append(non_skill)
    # agent_cap.isRealizedBy.append(cap)
    print(f"Las clases de agent capability_instance son: {agent_cap.is_a}")

    with onto:
        sync_reasoner()

    print(non_skill.is_a)
    print(cap.isRealizedBy)
    print(agent_cap.is_a)



if __name__ == '__main__':
    print("Initializing GUI SPADE agent program...")

    # Run main program with SPADE
    main()
