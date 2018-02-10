"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import wlsdeploy.util.dictionary_utils as dictionary_utils
from wlsdeploy.aliases.model_constants import SHUTDOWN_CLASS
from wlsdeploy.aliases.model_constants import STARTUP_CLASS
from wlsdeploy.aliases.wlst_modes import WlstModes
from wlsdeploy.tool.deploy import deployer_utils
from wlsdeploy.tool.deploy.common_resources_deployer import CommonResourcesDeployer
from wlsdeploy.tool.deploy.datasource_deployer import DatasourceDeployer
from wlsdeploy.tool.deploy.deployer import Deployer
from wlsdeploy.tool.deploy.jms_resources_deployer import JmsResourcesDeployer
from wlsdeploy.tool.deploy.multi_tenant_resources_deployer import MultiTenantResourcesDeployer
from wlsdeploy.tool.deploy.wldf_resources_deployer import WldfResourcesDeployer


class ResourcesDeployer(Deployer):
    """
    class docstring
    """
    _class_name = "ResourcesDeployer"

    def __init__(self, model, model_context, aliases, wlst_mode=WlstModes.OFFLINE):
        Deployer.__init__(self, model, model_context, aliases, wlst_mode)
        self._resources = self.model.get_model_resources()

    def deploy(self, location):
        domain_token = deployer_utils.get_domain_token(self.alias_helper)
        location.add_name_token(domain_token, self.model_context.get_domain_name())

        self._add_resources(location)

        multi_tenant_deployer = \
            MultiTenantResourcesDeployer(self.model, self.model_context, self.aliases, self.wlst_mode)
        multi_tenant_deployer.add_multi_tenant_objects()

    def _add_resources(self, location):
        data_source_deployer = DatasourceDeployer(self.model, self.model_context, self.aliases, self.wlst_mode)
        data_source_deployer.add_data_sources(self._resources, location)

        common_deployer = CommonResourcesDeployer(self.model, self.model_context, self.aliases, self.wlst_mode)
        common_deployer.add_self_tuning(self._resources, location)

        self._add_startup_classes(location)
        self._add_shutdown_classes(location)

        common_deployer.add_foreign_jndi_providers(self._resources, location)
        common_deployer.add_file_stores(self._resources, location)
        common_deployer.add_jdbc_stores(self._resources, location)
        common_deployer.add_jms_servers(self._resources, location)
        common_deployer.add_saf_agents(self._resources, location)
        common_deployer.add_path_services(self._resources, location)

        jms_deployer = JmsResourcesDeployer(self.model, self.model_context, self.aliases, wlst_mode=self.wlst_mode)
        jms_deployer.add_jms_system_resources(self._resources, location)

        common_deployer.add_jms_bridge_destinations(self._resources, location)
        common_deployer.add_jms_bridges(self._resources, location)
        common_deployer.add_mail_sessions(self._resources, location)

        wldf_deployer = WldfResourcesDeployer(self.model, self.model_context, self.aliases, self.wlst_mode)
        wldf_deployer.add_wldf_modules(self._resources, location)

        common_deployer.add_coherence_clusters(self._resources, location)
        return

    def _add_startup_classes(self, location):
        startup_nodes = dictionary_utils.get_dictionary_element(self._resources, STARTUP_CLASS)
        self._add_named_elements(STARTUP_CLASS, startup_nodes, location)
        return

    def _add_shutdown_classes(self, location):
        shutdown_nodes = dictionary_utils.get_dictionary_element(self._resources, SHUTDOWN_CLASS)
        self._add_named_elements(SHUTDOWN_CLASS, shutdown_nodes, location)
        return