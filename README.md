# I4.0 Standardized Microservice-based Industrial Agent: I4.0 SMIA 

[![Docker badge](https://img.shields.io/docker/pulls/ekhurtado/aas-manager.svg)](https://hub.docker.com/r/ekhurtado/aas-manager/) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ekhurtado/I4_0_SMIA?sort=semver) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/e87506fff1bb4a438c20e11bb7295f51)](https://app.codacy.com/gh/ekhurtado/I4_0_SMIA/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![Documentation Status](https://readthedocs.org/projects/i4-0-smia/badge/?version=latest)](https://i4-0-smia.readthedocs.io/en/latest/)

![I4.0 SMIA Logo Light](images/I4_0_SMIA_logo_positive.png/#gh-light-mode-only "I4.0 SMIA logo")
![I4.0 SMIA Logo Dark](images/I4_0_SMIA_logo_negative.png/#gh-dark-mode-only "I4.0 SMIA logo")

[//]: # (//Dependiendo del modo de GitHub oscuro o claro se añade una imagen u otra&#41;)

The I4.0 Standardized Microservice-based Industrial Agent (I4.0 SMIA) is a proposal for the concept of the I4.0 Component from the Reference Architectural Model Industrie 4.0 (RAMI 4.0). The features of the I4.0 SMIA include:

- free & open-source (add license)
- easily customizable and configurable
- containerized solution
- Standardized AASs based on SPADE agents.

> [!TIP]
> For more details on I4.0 Standardized Microservice-based Industrial Agent see the [:blue_book: **full documentation**](https://i4-0-smia.readthedocs.io/en/latest/).

## Project structure

The repository of the I4.0 SMIA project is structured as follows:

- [additional_tools](https://github.com/ekhurtado/Component_I4_0/tree/main/additional_tools): additional tools developed related to the I4.0 SMIA (i.e. a SPADE agent with a graphical interface that allows sending FIPA-ACL messages in a user-friendly way).
- [deploy](https://github.com/ekhurtado/Component_I4_0/tree/main/deploy): all the necessary resources for the deployment of the solution. As the execution platform is Kubernetes, these files are in YAML format.
- [src](https://github.com/ekhurtado/Component_I4_0/tree/main/src): the entire source code of the I4.0 SMIA. It is divided into two main subfolders:
  - [AAS_Cores](https://github.com/ekhurtado/Component_I4_0/tree/main/src/AAS_Cores): the code developed for the AAS Cores of the different use cases.
  - [AAS_Manager](https://github.com/ekhurtado/Component_I4_0/tree/main/src/AAS_Manager): the source code for the standardized AAS Manager.

## Usage

> [!IMPORTANT]
> At the moment there is no final version available for the I4.0 SMIA.
> The project is currently under development.
> Therefore, I4.0 SMIA is not a ready-to-use implementation.
> New features and bug fixes will be uploaded during development.

## Discussions

> [!NOTE]
> [Discussions](https://github.com/ekhurtado/Component_I4_0/discussions) page has been set as available to share announcements, create conversations, answer questions, and more.

## License

GNU General Public License v3.0. See `LICENSE` for more information.
