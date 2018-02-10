"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
from org.python.modules import jarray
import os
import sys
import unittest

from java.lang import String, Long
from java.util import Properties

from oracle.weblogic.deploy.aliases import AliasException
from oracle.weblogic.deploy.util import TypeUtils

from wlsdeploy.aliases.aliases import Aliases
from wlsdeploy.aliases.location_context import LocationContext
import wlsdeploy.aliases.model_constants as FOLDERS
from wlsdeploy.aliases.validation_codes import ValidationCodes
from wlsdeploy.aliases.wlst_modes import WlstModes
from wlsdeploy.exception import exception_helper
import wlsdeploy.logging.platform_logger as platform_logger
from wlsdeploy.util.cla_utils import CommandLineArgUtil
from wlsdeploy.util.model_context import ModelContext
from wlsdeploy.util.weblogic_helper import WebLogicHelper


class AliasesTestCase(unittest.TestCase):
    """
       1) Unit tests must be a class that extends unittest.TestCase
       2) Class methods with names starting with 'test' will be executed by the framework (all others skipped)
    """

    arg_map = {
        CommandLineArgUtil.ORACLE_HOME_SWITCH: os.environ.get('ORACLE_HOME'),
        CommandLineArgUtil.DOMAIN_HOME_SWITCH: ''
    }

    logger = platform_logger.PlatformLogger('wlsdeploy.unittest')
    wlst_version = WebLogicHelper(logger).wl_version_actual
    model_context = ModelContext(sys.argv[0], arg_map)

    # create a set of aliases for use with WLST
    aliases = Aliases(model_context=model_context)
    online_aliases = Aliases(model_context=model_context, wlst_mode=WlstModes.ONLINE)

    def testDomainLevelAttributeAccessibility(self):
        location = LocationContext()
        string_value = ['9002', 9002]
        model_attribute_name = 'AdministrationPort'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])

        wlst_attribute_name = 'AdministrationPort'
        wlst_attribute_value = string_value[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, None)

        location.append_location(FOLDERS.JMX)
        location.add_name_token("JMX", 'mydomain')
        string_value = ['true', 'true']
        model_attribute_name = 'EditMBeanServerEnabled'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])
        return

    def testDatasourceRootPath(self):
        expected = '/JDBCSystemResource/my-datasource'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        path = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(path, expected)

        location = LocationContext()
        kwargs = {token: 'my-datasource'}
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE, **kwargs)
        path = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(path, expected)
        return

    def testDatasourceParamsPath(self):
        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDataSourceParams/NO_NAME_0'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        path = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(path, expected)
        return

    def testDatasourceDriverPropertiesPath(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DRIVER_PARAMS)
        location.append_location(FOLDERS.JDBC_DRIVER_PARAMS_PROPERTIES)
        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/' \
                   'JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property'
        path1 = self.aliases.get_wlst_list_path(location)
        self.assertEqual(path1, expected)

        expected = '/JDBCSystemResources/my-datasource/JDBCResource/my-datasource/' \
                   'JDBCDriverParams/my-datasource/Properties/my-datasource/Properties'
        path2 = self.online_aliases.get_wlst_list_path(location)
        self.assertEqual(path2, expected)

        # Path to access a single property by name (user in this example)
        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/' \
                   'JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property/user'
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'user')
        path1 = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(path1, expected)

        expected = '/JDBCSystemResources/my-datasource/JDBCResource/my-datasource/' \
                   'JDBCDriverParams/my-datasource/Properties/my-datasource/Properties/user'
        path2 = self.online_aliases.get_wlst_attributes_path(location)
        self.assertEqual(path2, expected)
        return

    def testDatasourceMbeanListPath(self):
        expected = '/JDBCSystemResource'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        path = self.aliases.get_wlst_list_path(location)
        self.assertEqual(path, expected)
        return

    def testDatasourceSubfoldersPath(self):
        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE)
        path = self.aliases.get_wlst_subfolders_path(location)
        self.assertEqual(path, expected)
        return

    def testMachineMbeanListPath(self):
        expected = '/Machine'
        location = LocationContext()
        location.append_location(FOLDERS.MACHINE)
        path = self.aliases.get_wlst_list_path(location)
        self.assertEqual(path, expected)
        return

    def testDatasourceMbeanType(self):
        expected = 'JDBCSystemResource'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        mbean_type = self.aliases.get_wlst_mbean_type(location)
        self.assertEqual(mbean_type, expected)
        return

    def testDatasourceSubfolderMbeanType(self):
        expected = 'JDBCDriverParams'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DRIVER_PARAMS)
        mbean_type = self.aliases.get_wlst_mbean_type(location)
        self.assertEqual(mbean_type, expected)
        return

    def testDatasourceSubFolderMbeanName(self):
        expected = 'NO_NAME_0'
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)
        mbean_name = self.aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, expected)
        return

    def testGetModelSubFolders(self):
        expected = ['JDBCOracleParams', 'JDBCConnectionPoolParams', 'JDBCXAParams',
                    'JDBCDataSourceParams', 'JDBCDriverParams']
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'Generic1')

        location.append_location(FOLDERS.JDBC_RESOURCE)
        names = self.aliases.get_model_subfolder_names(location)
        self.assertEqual(len(names), len(expected))
        for name in names:
            self.assertEqual(name in expected, True)
        return

    def testAppDeploymentPathTokenReplacement(self):
        expected = self.model_context.replace_token_string('@@PWD@@/target/applications/simpleear.ear')
        location = LocationContext()
        location.append_location(FOLDERS.APPLICATION)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'simpleear')

        model_attribute_name = 'SourcePath'
        model_attribute_value = '@@PWD@@/target/applications/simpleear.ear'
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, expected)

        expected = self.model_context.replace_token_string('@@WL_HOME@@/common/deployable-libraries/jsf-2.0.war')
        location = LocationContext()
        location.append_location(FOLDERS.LIBRARY)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'jsf#2.0@1.0.0.0_2-0-2')

        model_attribute_name = 'SourcePath'
        model_attribute_value = '@@WL_HOME@@/common/deployable-libraries/jsf-2.0.war'
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, expected)
        return

    def testReadOnlyAttributeAccess(self):
        location = LocationContext()
        location.append_location(FOLDERS.APPLICATION)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'simpleear')

        model_attribute_name = 'SourcePath'
        model_attribute_value = '@@PWD@@/target/applications/simpleear.ear'
        wlst_attribute_name, wlst_attribute_value = \
            self.online_aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_name, None)
        self.assertEqual(wlst_attribute_value, None)
        return

    def testWlstAttributeValueConversion(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        string_value = ['Hello', 'Hello']
        model_attribute_name = 'AlgorithmType'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])

        string_value = ['123', 123]
        model_attribute_name = 'RowPrefetchSize'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])

        string_value = ['3600', Long(3600)]
        jms_location = LocationContext()
        jms_location.append_location(FOLDERS.JMS_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(jms_location)
        if token:
            jms_location.add_name_token(token, 'my-module')

        jms_location.append_location(FOLDERS.JMS_RESOURCE)
        jms_location.append_location(FOLDERS.CONNECTION_FACTORY)
        token = self.aliases.get_name_token(jms_location)
        if token:
            jms_location.add_name_token(token, 'my-connectionfactory')

        jms_location.append_location(FOLDERS.DEFAULT_DELIVERY_PARAMS)
        model_attribute_name = 'DefaultTimeToLive'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(jms_location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])
        self.assertEqual(wlst_attribute_value.getClass().getName(), 'java.lang.Long')

        string_value = [1, 'true']
        model_attribute_name = 'RowPrefetch'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])
        return

    def testWlstAttributeListValueConversion(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        model_attribute_name = 'JNDIName'
        model_attribute_value = 'com.bea.datasource1, com.bea.datasource2'
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, 'com.bea.datasource1,com.bea.datasource2')

        mylist = jarray.zeros(2, String)
        mylist[0] = 'com.bea.datasource1'
        mylist[1] = 'com.bea.datasource2'
        wlst_attribute_name, wlst_attribute_value = \
            self.online_aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, mylist)

        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, mylist)
        self.assertEqual(wlst_attribute_value, 'com.bea.datasource1,com.bea.datasource2')
        return

    def testModelAttributeValueConversion(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        string_value = ['Hello', 'Hello']
        wlst_attribute_name = 'AlgorithmType'
        wlst_attribute_value = string_value[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, string_value[1])

        string_value = ['123', 123]
        wlst_attribute_name = 'RowPrefetchSize'
        wlst_attribute_value = string_value[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, string_value[1])

        string_value = [1, 'true']
        wlst_attribute_name = 'RowPrefetch'
        wlst_attribute_value = string_value[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, string_value[1])
        return

    def testConvertToTypeJarray(self):
        location = LocationContext()
        location.append_location(FOLDERS.SERVER)
        token_name = self.aliases.get_name_token(location)
        location.add_name_token(token_name, 'AdminServer')
        location.append_location('FederationServices')

        wlst_name = 'AssertionConsumerUri'
        wlst_value = jarray.zeros(2, String)
        wlst_value[0] = 'abc'
        wlst_value[1] = 'def'
        model_name, model_value = self.aliases.get_model_attribute_name_and_value(location, wlst_name, wlst_value)
        self.assertEqual(model_name, wlst_name)
        self.assertEqual(type(model_value), list)
        self.assertEqual(model_value, ['abc', 'def'])
        return

    def testGetWlstAttributeNameAndValue(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        # get wlst attribute value should return the value even if its the default
        string_value = ['0', 0]
        model_attribute_name = 'RowPrefetchSize'
        model_attribute_value = string_value[0]
        wlst_attribute_name, wlst_attribute_value = \
            self.aliases.get_wlst_attribute_name_and_value(location, model_attribute_name, model_attribute_value)
        self.assertEqual(wlst_attribute_value, string_value[1])
        return

    def testGetModelAttributeNameAndValue(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        # get model attribute value should return the value only if its NOT the default
        boolean_values = ['false', None]
        wlst_attribute_name = 'RowPrefetch'
        wlst_attribute_value = boolean_values[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, boolean_values[1])

        # get model attribute value should return the value only if its NOT the default
        string_value = [0, None]
        wlst_attribute_name = 'RowPrefetchSize'
        wlst_attribute_value = string_value[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, string_value[1])

        # get model attribute value should return the value only if its NOT the default
        location = LocationContext()
        location.append_location(FOLDERS.SERVER)
        boolean_values = [0, None]
        wlst_attribute_name = 'NetworkClassLoadingEnabled'
        wlst_attribute_value = boolean_values[0]
        model_attribute_name, model_attribute_value = \
            self.aliases.get_model_attribute_name_and_value(location, wlst_attribute_name, wlst_attribute_value)
        self.assertEqual(model_attribute_value, boolean_values[1])
        return

    def testGetWlstAttributeName(self):
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DATASOURCE_PARAMS)

        model_attribute_name = 'RowPrefetch'
        wlst_attribute_name = self.aliases.get_wlst_attribute_name(location, model_attribute_name)
        self.assertEqual(wlst_attribute_name, 'RowPrefetch')
        return

    def testIsWlstModelAttributeName(self):
        wls_version = '10.3.4'
        online_aliases = Aliases(self.model_context, WlstModes.ONLINE, wls_version)
        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE)
        location.append_location(FOLDERS.JDBC_DRIVER_PARAMS)
        model_attribute_name = 'QosDegradationAllowed'
        expected = exception_helper.get_message('WLSDPLY-08041', model_attribute_name,
                                                location.get_folder_path(), wls_version)
        result, message = online_aliases.is_valid_model_attribute_name(location, model_attribute_name)
        self.assertEqual(result, ValidationCodes.INVALID)
        self.assertEqual(message, expected)

        offline_aliases = Aliases(self.model_context, WlstModes.OFFLINE, wls_version)
        location.pop_location()
        location.append_location(FOLDERS.JDBC_ORACLE_PARAMS)
        model_attribute_name = 'OnsWalletPasswordEncrypted'
        expected = exception_helper.get_message('WLSDPLY-08040', model_attribute_name,
                                                location.get_folder_path(), wls_version)
        result, message = offline_aliases.is_valid_model_attribute_name(location, model_attribute_name)
        self.assertEqual(result, ValidationCodes.VALID)
        self.assertEqual(message, expected)

        location.pop_location()
        location.append_location(FOLDERS.JDBC_CONNECTION_POOL_PARAMS)
        model_attribute_name = 'ProfileConnectionLeakTimeoutSeconds'
        earliest_version = '12.2.1'
        expected = exception_helper.get_message('WLSDPLY-08042', model_attribute_name, location.get_folder_path(),
                                                wls_version, earliest_version)
        result, message = online_aliases.is_valid_model_attribute_name(location, model_attribute_name)
        self.assertEqual(result, ValidationCodes.VERSION_INVALID)
        self.assertEqual(message, expected)
        return

    def testPropertyTypes(self):
        expected = Properties()
        expected.put('key1', 'val1')
        expected.put('key2', 'val2')
        expected.put('key3', 'val3')

        test_string = 'key1=val1, key2=val2, key3=val3'
        result = TypeUtils.convertToType('properties', test_string)
        self.assertEqual(expected, result)

        test_dict = {"key1": "val1", "key2": "val2", "key3": "val3"}
        result = TypeUtils.convertToType('properties', test_dict)
        self._assertMapEqual(expected, result)

    def testNewGetWlstPaths(self):
        attr_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0'
        folder_expected = attr_expected
        list_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams'
        create_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource'

        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS)

        result = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)

        result = self.aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)

        result = self.aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)

        result = self.aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)

        attr_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams' \
                        '/NO_NAME_0/Properties/NO_NAME_0/Property/user'
        folder_expected = attr_expected
        list_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams' \
                        '/NO_NAME_0/Properties/NO_NAME_0/Property'
        create_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams' \
                          '/NO_NAME_0/Properties/NO_NAME_0'

        location.append_location(FOLDERS.JDBC_DRIVER_PARAMS_PROPERTIES)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'user')

        result = self.aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)

        result = self.aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)

        result = self.aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)

        result = self.aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)
        return

    def testVersionFilteredFolders(self):
        old_wls_version = '10.3.6'
        new_wls_version = '12.2.1.3'

        old_aliases = Aliases(self.model_context, WlstModes.OFFLINE, old_wls_version)
        new_aliases = Aliases(self.model_context, WlstModes.OFFLINE, new_wls_version)
        location = LocationContext()
        location.append_location(FOLDERS.PARTITION)
        mbean_type = old_aliases.get_wlst_mbean_type(location)
        self.assertEqual(mbean_type, None, 'expected Partition type to be null')
        mbean_type = new_aliases.get_wlst_mbean_type(location)
        self.assertNotEqual(mbean_type, None, 'expected Partition type not to be null')

        location.pop_location()
        location.append_location(FOLDERS.CLUSTER)
        location.append_location(FOLDERS.DYNAMIC_SERVERS)
        mbean_type = old_aliases.get_wlst_mbean_type(location)
        self.assertEqual(mbean_type, None, 'expected DynamicServers type to be null')
        mbean_type = new_aliases.get_wlst_mbean_type(location)
        self.assertNotEqual(mbean_type, None, 'expected DynamicServers type not to be null')
        return

    def testDomainAttributeMethods(self):
        aliases = Aliases(self.model_context, WlstModes.OFFLINE)
        location = LocationContext()
        get_required_attributes = aliases.get_wlst_get_required_attribute_names(location)
        self.assertNotEqual(get_required_attributes, None, 'expected get-required attributes to not be None')
        restart_required_attributes = aliases.get_wlst_get_required_attribute_names(location)
        self.assertNotEqual(restart_required_attributes, None, 'expected restart-required attributes to not be None')
        return

    def testMTAliasLoading(self):
        aliases = Aliases(self.model_context, WlstModes.OFFLINE)

        attr_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0'
        folder_expected = attr_expected
        list_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams'
        create_expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource'

        location = LocationContext()
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS)

        result = aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)
        result = aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)
        result = aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)
        result = aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)

        attr_expected = '/ResourceGroupTemplate/MyResourceGroupTemplate/JDBCSystemResource/my-datasource' \
                        '/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0'
        folder_expected = attr_expected
        list_expected = '/ResourceGroupTemplate/MyResourceGroupTemplate/JDBCSystemResource/my-datasource' \
                        '/JdbcResource/my-datasource/JDBCDriverParams'
        create_expected = '/ResourceGroupTemplate/MyResourceGroupTemplate/JDBCSystemResource/my-datasource' \
                          '/JdbcResource/my-datasource'

        location = LocationContext()
        location.append_location(FOLDERS.RESOURCE_GROUP_TEMPLATE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'MyResourceGroupTemplate')

        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS)


        result = aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)
        result = aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)
        result = aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)
        result = aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)

        attr_expected = '/ResourceGroup/MyResourceGroup/JDBCSystemResource/my-datasource/JdbcResource' \
                        '/my-datasource/JDBCDriverParams/NO_NAME_0'
        folder_expected = attr_expected
        list_expected = '/ResourceGroup/MyResourceGroup/JDBCSystemResource/my-datasource/JdbcResource' \
                        '/my-datasource/JDBCDriverParams'
        create_expected = '/ResourceGroup/MyResourceGroup/JDBCSystemResource/my-datasource/JdbcResource/my-datasource'

        location = LocationContext()
        location.append_location(FOLDERS.RESOURCE_GROUP)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'MyResourceGroup')
        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS)

        result = aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)
        result = aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)
        result = aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)
        result = aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)

        attr_expected = '/Partition/MyPartition/ResourceGroup/MyResourceGroup/JDBCSystemResource' \
                        '/my-datasource/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0'
        folder_expected = attr_expected
        list_expected = '/Partition/MyPartition/ResourceGroup/MyResourceGroup/JDBCSystemResource' \
                        '/my-datasource/JdbcResource/my-datasource/JDBCDriverParams'
        create_expected = '/Partition/MyPartition/ResourceGroup/MyResourceGroup/JDBCSystemResource' \
                          '/my-datasource/JdbcResource/my-datasource'

        location = LocationContext()
        location.append_location(FOLDERS.PARTITION)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'MyPartition')

        location.append_location(FOLDERS.RESOURCE_GROUP)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'MyResourceGroup')

        location.append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token = self.aliases.get_name_token(location)
        if token:
            location.add_name_token(token, 'my-datasource')

        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS)

        result = aliases.get_wlst_attributes_path(location)
        self.assertEqual(result, attr_expected)
        result = aliases.get_wlst_subfolders_path(location)
        self.assertEqual(result, folder_expected)
        result = aliases.get_wlst_list_path(location)
        self.assertEqual(result, list_expected)
        result = aliases.get_wlst_create_path(location)
        self.assertEqual(result, create_expected)
        return

    def testChildNodeTypes(self):
        location = LocationContext()
        location.append_location(FOLDERS.SELF_TUNING)

        result = self.aliases.requires_unpredictable_single_name_handling(location)
        self.assertEqual(result, True)
        result = self.aliases.supports_multiple_mbean_instances(location)
        self.assertEqual(result, False)

        name_token = self.aliases.get_name_token(location)
        self.assertEqual(name_token, 'SELFTUNING')
        location.add_name_token("DOMAIN", 'mydomain')
        mbean_name = self.aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'NO_NAME_0')
        mbean_name = self.online_aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'mydomain')

        location.append_location(FOLDERS.WORK_MANAGER)
        result = self.aliases.requires_unpredictable_single_name_handling(location)
        self.assertEqual(result, False)
        result = self.aliases.supports_multiple_mbean_instances(location)
        self.assertEqual(result, True)

        name_token = self.aliases.get_name_token(location)
        self.assertEqual(name_token, 'WORKMANAGER')
        location.add_name_token(name_token, 'MyWorkManager')
        mbean_name = self.aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'MyWorkManager')
        mbean_name = self.online_aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'MyWorkManager')

        location.append_location('WorkManagerShutdownTrigger')
        result = self.aliases.requires_unpredictable_single_name_handling(location)
        self.assertEqual(result, False)
        result = self.aliases.supports_multiple_mbean_instances(location)
        self.assertEqual(result, False)

        name_token = self.aliases.get_name_token(location)
        self.assertEqual(name_token, None)
        mbean_name = self.aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'NO_NAME_0')
        mbean_name = self.online_aliases.get_wlst_mbean_name(location)
        self.assertEqual(mbean_name, 'MyWorkManager')

        location = LocationContext().append_location(FOLDERS.SECURITY, FOLDERS.GROUP, DOMAIN='mydomain')
        result = self.aliases.supports_multiple_mbean_instances(location)
        self.assertEqual(result, True)
        return

    def testFlattenedFolders(self):
        location = LocationContext().append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token_name = self.aliases.get_name_token(location)
        if token_name is not None:
            location.add_name_token(token_name, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS,
                                 FOLDERS.JDBC_DRIVER_PARAMS_PROPERTIES)
        result = self.aliases.is_flattened_folder(location)
        self.assertEqual(result, True)
        name = self.aliases.get_wlst_flattened_mbean_name(location)
        online_name = self.online_aliases.get_wlst_flattened_mbean_name(location)
        type = self.aliases.get_wlst_flattened_mbean_type(location)
        self.assertEqual(name, 'NO_NAME_0')
        self.assertEqual(online_name, 'my-datasource')
        self.assertEqual(type, 'Properties')

        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0/Properties'
        result = self.aliases.get_wlst_flattened_folder_list_path(location)
        self.assertEqual(result, expected)

        expected = '/JDBCSystemResource/my-datasource/JdbcResource/my-datasource/JDBCDriverParams/NO_NAME_0'
        result = self.aliases.get_wlst_flattened_folder_create_path(location)
        self.assertEqual(result, expected)
        return

    def testModelFolderPath(self):
        location = LocationContext().append_location(FOLDERS.JDBC_SYSTEM_RESOURCE)
        token_name = self.aliases.get_name_token(location)
        if token_name is not None:
            location.add_name_token(token_name, 'my-datasource')
        location.append_location(FOLDERS.JDBC_RESOURCE, FOLDERS.JDBC_DRIVER_PARAMS,
                                 FOLDERS.JDBC_DRIVER_PARAMS_PROPERTIES)

        expected = 'resources:/JDBCSystemResource/my-datasource/JdbcResource/JDBCDriverParams/Properties'
        path = self.aliases.get_model_folder_path(location)
        self.assertEqual(path, expected)

        token_name = self.aliases.get_name_token(location)
        if token_name is not None:
            location.add_name_token(token_name, 'user')

        expected = 'resources:/JDBCSystemResource/my-datasource/JdbcResource/JDBCDriverParams/Properties/user'
        path = self.aliases.get_model_folder_path(location)
        self.assertEqual(path, expected)
        return

    def testIsValidModelFolderName(self):
        location = LocationContext()
        result, message = self.aliases.is_valid_model_folder_name(location, 'ServerTemplate')
        self.assertEqual(result, ValidationCodes.VALID)

        aliases = Aliases(self.model_context, wls_version='12.1.1')
        result, message = aliases.is_valid_model_folder_name(location, 'ServerTemplate')
        self.assertEqual(result, ValidationCodes.VERSION_INVALID)

        result, message = self.aliases.is_valid_model_folder_name(location, 'ServerTemplates')
        self.assertEqual(result, ValidationCodes.INVALID)

        top_level_topology_folders = self.aliases.get_model_topology_top_level_folder_names()

        for folder in top_level_topology_folders:
            result, message = self.aliases.is_valid_model_folder_name(location, folder)
            self.assertEqual(result, ValidationCodes.VALID)

        return

    def testBooleanDefaultValues(self):
        location = LocationContext().append_location(FOLDERS.RESTFUL_MANAGEMENT_SERVICES, DOMAIN='mydomain')
        name, value = self.aliases.get_model_attribute_name_and_value(location, 'JavaServiceResourcesEnabled', 'false')
        self.assertEqual(name, 'JavaServiceResourcesEnabled')
        self.assertEqual(value, None)
        return

    def testSecurityProviderTypeHandling(self):
        location = LocationContext().append_location(FOLDERS.SECURITY_CONFIGURATION)
        token = self.aliases.get_name_token(location)
        location.add_name_token(token, 'my-domain')

        location.append_location(FOLDERS.REALM)
        token = self.aliases.get_name_token(location)
        location.add_name_token(token, 'myrealm')

        location.append_location(FOLDERS.AUTHENTICATION_PROVIDER)
        result = self.aliases.requires_artificial_type_subfolder_handling(location)
        self.assertEqual(result, True)

        location.append_location(FOLDERS.DEFAULT_AUTHENTICATOR)
        try:
            self.aliases.requires_artificial_type_subfolder_handling(location)
            self.assertEqual(True, False, 'Excepted AliasException to be thrown')
        except AliasException, ae:
            pass


    def _assertMapEqual(self, expected, testObject):
        self.assertEqual(expected.size(), testObject.size())
        for key in expected.keys():
            self.assertEqual(expected.get(key), testObject.get(str(key).strip()))
        return

if __name__ == '__main__':
    unittest.main()