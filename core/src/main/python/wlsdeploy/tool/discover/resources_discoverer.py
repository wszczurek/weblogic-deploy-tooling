"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

import wlsdeploy.logging.platform_logger as platform_logger
import wlsdeploy.tool.discover.discoverer as discoverer
from wlsdeploy.aliases.wlst_modes import WlstModes
from wlsdeploy.tool.discover.common_resources_discoverer import CommonResourcesDiscoverer
from wlsdeploy.tool.discover.global_resources_discoverer import GlobalResourcesDiscoverer
from wlsdeploy.tool.discover.multi_tenant_resources_discoverer import MultiTenantResourcesDiscoverer

_class_name = 'ResourcesDiscoverer'
_logger = platform_logger.PlatformLogger(discoverer.get_discover_logger_name())


class ResourcesDiscoverer(object):
    """
    Discover the weblogic resources from the domain. This includes the global resources and the
    resources common to both global and multi-tenant.
    """

    def __init__(self, model_context, resource_dictionary, wlst_mode=WlstModes.OFFLINE):
        self._model_context = model_context
        self._dictionary = resource_dictionary
        self._wlst_mode = wlst_mode

    def discover(self):
        """
        Discover weblogic resources from the on-premise domain.
        :return: resources: dictionary
        """
        _method_name = 'discover'
        _logger.entering(class_name=_class_name, method_name=_method_name)
        _logger.info('WLSDPLY-06300', class_name=_class_name, method_name=_method_name)
        GlobalResourcesDiscoverer(self._model_context, self._dictionary, self._wlst_mode).discover()
        CommonResourcesDiscoverer(self._model_context, self._dictionary, self._wlst_mode).discover()
        _logger.exiting(class_name=_class_name, method_name=_method_name)
        return self._dictionary