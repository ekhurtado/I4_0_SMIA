# Additional tool: AASX Package Explorer resources

This additional tool for SMIA offers some resources to be added in [Eclipse AASX Package Explorer](https://github.com/eclipse-aaspe/package-explorer) as plugins, in order to simplify and automate the development of the CSS-based AAS model required in the SMIA approach.

Eclipse AASX Package Explorer is a viewer and editor under the Apache License 2.0 for the Asset Administration Shell and allows its extension in the form of plugins. One of these plugins, named ``AasxPluginGenericForms``, enables the automatic creation of submodels based on given templates.

Thus, some JSON files are provided to be added in the AASX Package Explorer as plugins to allow the automatic creation of some required submodels for all assets within the SMIA approach.

- ``IDTA-02017-1-0_Template_Asset_Interfaces_Description.add-options.json`` : JSON file for the plugin of the IDTA submodel [Asset Interfaces Description](https://github.com/admin-shell-io/submodel-templates/tree/main/published/Asset%20Interfaces%20Description/1/0) (license *CC BY 4.0*). It had to be slightly modified to avoid errors when adding it through the plugin.
- ``IDTA-02007-1-0_Template_Software_Nameplate.add-options.json`` : JSON file for the plugin of the IDTA submodel [Nameplate for Software in Manufacturing](https://github.com/admin-shell-io/submodel-templates/tree/main/published/Software%20Nameplate/1/0) (license *CC BY 4.0*). It had to be slightly modified to avoid errors when adding it through the plugin.
- ``SMIA-css-semantic-ids-sm.add-options.json`` : JSON file for the SMIA submodel plugin with all ConceptDescriptions to easily set the required CSS-based semanticIDs in the AAS elements.

> [!NOTE]
> These JSON files need to be saved in the following path: ``<AASX Package Explorer installation path>/AasxPackageExplorer/plugins/AasxPluginGenericForms``.

In addition, to properly customize CSS-based AAS elements, new presets for qualifiers are provided.

- ``SMIA-css-qualifier-presets.json`` : JSON file all Qualifiers to easily customize the required CSS-based AAS elements.

> [!NOTE]
> This ``qualifier-presets.json`` file is located in the following path: ``<AASX Package Explorer installation path>/AasxPackageExplorer``. Be sure to copy the contents to the end of the JSON list in the form of new JSON items.

## Usage

> [!TIP]
> When updating any files within the AASX Package Explorer installation folders (adding new plugins that save JSON files or modifying JSON files such as ``qualifier-presets.json``), the program must be re-run to apply the changes.  

