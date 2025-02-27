Glossary
========

.. _glossary:

.. glossary::
    :sorted:

    **API**
        Application Programming Interface. A set of routines, protocols, and tools for building software applications.

    **IDE**
        Integrated Development Environment. A software suite that consolidates the basic tools developers need to write and test software.

    **Asset**
        Physical, digital (e.g. software) or intangible (e.g. software license) entity that has value to an individual, an organisation or a government [`IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_].

    **AAS**
        The Asset Administration Shell or AAS is the standardized :term:`digital representation <Digital representation>` of an asset. It is also seen as one interoperable manifestation of a :term:`Digital Twin` in manufacturing that facilitates tighter integration within and across the three dimensions mentioned above [`IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_].

    **AAS interaction patterns**
        An interaction is the behavior that is specified by a sequence of messages between two or more system entities. Different interaction patterns can be generated among AAS-related entities: type 1 (passive), where the exchange is in form of a file; type 2 (reactive), which need a standardized interface to AAS content to another I4.0 system participant; adn type 3 (proactive), which need peer-to-peer interactions between AAS of I4.0 components through the exchange of messages based on an :term:`I4.0 language` [from `Functional View of the AAS <https://www.plattform-i40.de/IP/Redaktion/EN/Downloads/Publikation/Functional-View.pdf?__blob=publicationFile&v=1>`_].

    **Digital representation**
        Information and services representing an entity from a given point of view, such as its characteristics and behavior. The data is represented in a digital and formalized manner suitable for communication, storage, interpretation or processing, while the behavior includes functionality (description and execution). Even so, it is an administrative representation, i.e., it represents functionality but is not capable of performing it [adapted from `IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_ and `Plattform I4.0 glossary <https://www.plattform-i40.de/IP/Navigation/EN/Industrie40/Glossary/glossary.html>`_].

    **FIPA-ACL**
        The goal of the Foundation for Intelligent Physical Agents (FIPA) is to produce software standards for heterogeneous and interacting agents and agent-based systems. Among FIPA specifications, FIPA ACL (Agent Communication Language) is a language in which communicative acts can be expressed and hence messages constructed that represents an standardized :term:`I4.0 language` [`FIPA <http://www.fipa.org/about/index.html>`_].

    **I4.0 language**
        System of rules that enables interoperable communication between :term:`I4.0 Components <I4.0 Component>` in an :term:`I4.0 System`, for both vertical and horizontal interactions. The goal is to create a standardized language that enables machines to exchange information, negotiate tasks and activate themselves autonomously within a value chain.

    **I4.0 Component**
        Globally uniquely identifiable participant with communication capability consisting of an asset and its :term:`AAS` within an :term:`I4.0 System` which there offers services with defined QoS (quality of service) characteristics. So, in order to be part of an I4.0 System, It consists of the asset and an AAS-compliant :term:`Digital Twin`, i.e. it is the combination of the standardized asset and the software necessary to generate a representative of the asset within a standardized distributed system [adapted from `Plattform I4.0 glossary <https://www.plattform-i40.de/IP/Navigation/EN/Industrie40/Glossary/glossary.html>`_].

    **I4.0 System**
        System, consisting of :term:`I4.0 Components <I4.0 Component>` (interacting, interrelated, or interdependent elements), which serves a specific purpose, has defined properties, and supports standardized services and states [adapted from `IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_ and `Plattform I4.0 glossary <https://www.plattform-i40.de/IP/Navigation/EN/Industrie40/Glossary/glossary.html>`_].

    **Inter SMIA Interaction**
        Interaction type that takes place between :term:`SMIA` instances. These interactions are based on a :term:`I4.0 language` such as :term:`FIPA-ACL`. In this way, SMIA instances communicate in a :term:`AAS proactive (type 3) interaction <AAS interaction patterns>`.

    **Industrial Agent**
        An industrial agent is defined as a key enabler for industrial applications, focusing on core functionalities relevant to the application, especially in the context of cyber-physical systems and their utilization in industrial environments. There are cognitive entities with an inherent social capability to compete and/or collaborate with each other to achieve both their own and global, offering flexibility, reconfigurability and autonomy [adapted from `ScienceDirect <https://www.sciencedirect.com/topics/computer-science/industrial-agent>`_].

    **Multi-Agent System**
        A multi-agent system (MAS) is a computerized system composed of multiple interacting intelligent agents, capable of perceiving their environment and taking decisions based on it. Typically agents refers to software agents, but could equally well be specific type of agents such as :term:`Industrial Agents <Industrial Agent>`. The work toward a common goal that goes beyond their individual goals, increasing the adaptability and robustness.

    **SMIA**
        The Self-configurable Manufacturing Industrial Agent approach seeks to provide a solution for the integration of standardized manufacturing assets and their inclusion in flexible production systems in a way that achieves the demanding requirements imposed during the digital transformation by the Industry 4.0 paradigm. In order to achieve this goal, it considers several axes as key aspects of development: interoperability, autonomy, accessibility and scalability. To achieve this, a solution is presented based on the self-configuration of :term:`Digital Twins <Digital Twin>` implemented through :term:`industrial agents <Industrial Agent>` as asset representatives, based on their standardized descriptions such as the :term:`AAS` and enriched with architectural styles such as the :term:`CSS model`.

    **Digital Twin**
        :term:`Digital representation`, sufficient to meet the requirements of a set of use cases. That is, it is the software needed to access the administrative part of the asset and allow that information to be exposed to other software applications. In addition, it must also provide the ability to communicate with the asset [adapted from `Specification of the AAS Part 1: Metamodel <https://industrialdigitaltwin.org/en/content-hub/aasspecifications/specification-of-the-asset-administration-shell-part-1-metamodel-idta-number-01001-3-0-1>`_].

    **CSS model**
        The :term:`Capability`, :term:`Skill` and Service (CSS) model is an architectural style specially designed for the flexible manufacturing environment, which proposes the modularization of production resources and requirements, by abstracting production functionalities on multiple levels. Some (such as Service) are proposed for application areas with cross-company shared production, and others focus on intra-company production: distinguishing the description of a functionality (Capability) and its implementation (Skill) [`scientific paper <https://www.degruyter.com/document/doi/10.1515/auto-2022-0117/html?lang=en>`_].

    **Capability**
        In the :term:`SMIA` approach the Capability concept is taken from the :term:`CSS model`: an implementation-independent specification of a function in industrial production to achieve an effect in the physical or virtual world [`scientific paper <https://www.degruyter.com/document/doi/10.1515/auto-2022-0117/html?lang=en>`_]. In the SMIA approach, two types of capabilities are distinguished for each type of entity (the asset and its representative software): **Asset Capabilities** and **Agent Capabilities**.

    **Skill**
        In the :term:`SMIA` approach the Skill concept is taken from the :term:`CSS model`: an executable asset-dependent implementation of an encapsulated (automation) function specified by a :term:`capability <Capability>`. [`scientific paper <https://www.degruyter.com/document/doi/10.1515/auto-2022-0117/html?lang=en>`_].

    **Service**
        In the :term:`SMIA` approach the Skill concept is not taken from the :term:`CSS model`, because SMIA remains in intra-company environment. It is a distinct part of the functionality that is provided by an entity through interfaces, where some operations can be assigned to it [`IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_]. As well as with :term:`capabilities <Capability>`, two types of services are distinguished for each type of entity (the asset and its representative software): **Asset Services** (mentioned in `IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_) and **Agent Services**. In the SMIA approach, the infrastructure services proposed in the `Functional View of the AAS <https://www.plattform-i40.de/IP/Redaktion/EN/Downloads/Publikation/Functional-View.pdf?__blob=publicationFile&v=1>`_ are also supported as part of :term:`Inter SMIA interactions <Inter SMIA Interaction>`.

    **Ontology**
        It is an explicit specification of a shared conceptualization, in the form of a set of axioms, where each concept is constituted by an identifier, name, description, and additional entities and where relationships between concepts can be described without restriction. So, it constitutes a reusable information model that captures the knowledge of a domain independent of specific applications and is used as semantically rich schema for knowledge graphs [`IEC 63278-1 <https://webstore.iec.ch/en/publication/65628>`_ and `scientific paper <https://www.degruyter.com/document/doi/10.1515/auto-2022-0117/html?lang=en>`_].

    **OWL**
        The OWL Web Ontology Language is a designed for use by applications that need to process the content of information instead of just presenting information to humans by using :term:`ontologies <Ontology>`. This standard proposed by World Wide Web Consortium (W3C) within the Semantic Web Ontologies, offers the implementation of a conceptual model specification in a computational form independent of specific programming languages, which can be directly instantiated in applications [`W3C OWL <https://www.w3.org/TR/2004/REC-owl-features-20040210/>`_].

    **SPADE**
        Smart Python Agent Development Environment (SPADE) is a :term:`multi-agent systems <Multi-Agent System>` development platform written in Python and based on instant messaging (XMPP). It presents a simple approach, based on asynchronous execution, which offers the ability to develop agents that can execute several behaviors simultaneously [`SPADE documentation <https://spade-mas.readthedocs.io/en/latest/readme.html>`_].


