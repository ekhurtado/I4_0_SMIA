AAS Developer Guide
===================

This guide is a comprehensive resource for developing the :term:`AAS`. In this approach, the AAS is composed by the :term:`AAS Manager` and the :term:`AAS Core`. Therefore, this guide is divided into two parts. The guide is intended for both new and experienced contributors.

Development of the AAS Manager
------------------------------

The AAS Manager only needs to be parameterised, as it is provided by the platform and it is the common part of all AASs. To parameterise it, it has to perform thee definition of the overall AAS in form of an XML document.

The definition of the AAS must follow the official AAS meta-model, presented by Plattform Industrie 4.0 in cooperation with IDTA and ZVEI. This meta-model specifies that an environment has to be defined where all AAS, sub-models and concept descriptions will be placed. So, the AAS definition will have three main elements:

.. code-block:: xml
    :caption: Main groups in the AAS definition in the form of an XML document.

    <aas:environment xmlns:aas="https://admin-shell.io/aas/3/0">
        <aas:assetAdministrationShells>
            <aas:assetAdministrationShell>
                <!-- AAS Manager definition -->
            </aas:assetAdministrationShell>
            <aas:assetAdministrationShell>
                <!-- AAS Core definition -->
            </aas:assetAdministrationShell>
        <aas:assetAdministrationShells>
        <aas:submodels>
            <aas:submodel>
                <!-- Submodel definition -->
            </aas:submodel>
        </aas:submodels>
        <aas:conceptDescriptions>
            <aas:conceptDescription>
                <!-- concept description definition -->
            </aas:conceptDescription>
        </aas:conceptDescriptions>
    </aas:environment>

TODO: TO BE FINALISED

Development of the AAS Core
---------------------------

The AAS Core is the specific part of the AAS, and it is developed by the user, so this guide will especially detail how the interaction between the Manager and the Core works and some tips for the development of the AAS Core source code.


Some tests with code blocks
---------------------------


TODO: TO BE FINALISED (THIS IS A TEST PAGE OF CODE ADDITION)

Code blocks and examples are an essential part of technical project
documentation. Sphinx provides syntax highlighting for these
out-of-the-box, through Pygments.

.. tab:: Option 1

    .. code::

       Code blocks in Markdown can be created in various ways.

           Indenting content by 4 spaces.
           This will not have any syntax highlighting.


       Wrapping text with triple backticks also works.
       This will have default syntax highlighting (highlighting a few words and "strings").

    .. code:: python

       python
       print("And with the triple backticks syntax, you can have syntax highlighting.")


       none
       print("Or disable all syntax highlighting.")


       There's a lot of power hidden underneath the triple backticks in MyST Markdown,
       as seen in <https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html>.

.. tab:: Option 2

    .. code::

       Code blocks in reStructuredText can be created in various ways::

           Indenting content by 4 spaces, after a line ends with "::".
           This will have default syntax highlighting (highlighting a few words and "strings").

    .. code::

       You can also use the code directive, or an alias: code-block, sourcecode.
       This will have default syntax highlighting (highlighting a few words and "strings").

    .. code:: python

       print("And with the directive syntax, you can have syntax highlighting.")

    .. code:: none

       print("Or disable all syntax highlighting.")


There's a lot more forms of "blocks" in reStructuredText that can be used, as
seen in https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#literal-blocks.

With the "sphinx-design" extension we can also add dropdowns:

.. dropdown:: Dropdown title

    Dropdown content


Event dropdowns with an icon:

.. dropdown:: Dropdown with icon
    :octicon:`code-square;1em;sd-text-info`

    Dropdown content


Test for a subsection
~~~~~~~~~~~~~~~~~~~~~

TODO