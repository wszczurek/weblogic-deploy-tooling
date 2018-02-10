"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
from java.lang import String
from oracle.weblogic.deploy.encrypt import EncryptionException
from oracle.weblogic.deploy.encrypt import EncryptionUtils
from oracle.weblogic.deploy.util import TypeUtils
from oracle.weblogic.deploy.util import VersionUtils

from wlsdeploy.aliases.alias_constants import ChildFoldersTypes
from wlsdeploy.aliases.alias_entries import AliasEntries
from wlsdeploy.aliases.validation_codes import ValidationCodes
from wlsdeploy.aliases.wlst_modes import WlstModes
from wlsdeploy.exception import exception_helper
from wlsdeploy.logging.platform_logger import PlatformLogger
from wlsdeploy.aliases import alias_utils
from wlsdeploy.util import string_utils
from wlsdeploy.util.weblogic_helper import WebLogicHelper

from wlsdeploy.aliases.alias_constants import ACCESS
from wlsdeploy.aliases.alias_constants import ALIAS_LIST_TYPES
from wlsdeploy.aliases.alias_constants import ALIAS_MAP_TYPES
from wlsdeploy.aliases.alias_constants import ATTRIBUTES
from wlsdeploy.aliases.alias_constants import DEFAULT
from wlsdeploy.aliases.alias_constants import FLATTENED_FOLDER_DATA
from wlsdeploy.aliases.alias_constants import FOLDERS
from wlsdeploy.aliases.alias_constants import GET
from wlsdeploy.aliases.alias_constants import GET_MBEAN_TYPE
from wlsdeploy.aliases.alias_constants import GET_METHOD
from wlsdeploy.aliases.alias_constants import JARRAY
from wlsdeploy.aliases.alias_constants import LIST
from wlsdeploy.aliases.alias_constants import LSA
from wlsdeploy.aliases.alias_constants import MBEAN
from wlsdeploy.aliases.alias_constants import MERGE
from wlsdeploy.aliases.alias_constants import MODEL_NAME
from wlsdeploy.aliases.alias_constants import PREFERRED_MODEL_TYPE
from wlsdeploy.aliases.alias_constants import PROPERTIES
from wlsdeploy.aliases.alias_constants import RESTART_REQUIRED
from wlsdeploy.aliases.alias_constants import SET_MBEAN_TYPE
from wlsdeploy.aliases.alias_constants import SET_METHOD
from wlsdeploy.aliases.alias_constants import USES_PATH_TOKENS
from wlsdeploy.aliases.alias_constants import VALUE
from wlsdeploy.aliases.alias_constants import WLST_NAME
from wlsdeploy.aliases.alias_constants import WLST_TYPE


class Aliases(object):
    """
    The public interface into the aliases subsystem that abstracts out the WLST knowledge base from the
    rest of the tooling.
    """
    _class_name = 'Aliases'

    def __init__(self, model_context, wlst_mode=WlstModes.OFFLINE, wls_version=None, logger=None):
        self._model_context = model_context
        self._wlst_mode = wlst_mode

        if logger is None:
            self._logger = PlatformLogger('wlsdeploy.aliases')
        else:
            self._logger = logger

        self._wls_helper = WebLogicHelper(self._logger)
        if wls_version is None:
            self._wls_version = self._wls_helper.wl_version_actual
        else:
            self._wls_version = wls_version

        self._alias_entries = AliasEntries(wlst_mode, self._wls_version)
        return

    ###########################################################################
    #              Model folder navigation-related methods                    #
    ###########################################################################

    def get_model_top_level_folder_names(self):
        """
        Returns a list of the recognized top-level model folders corresponding to the known WLST top-level folders.
        :return: a list of the recognized top-level model folder names
        """
        return self._alias_entries.get_model_domain_subfolder_names()

    def get_model_topology_top_level_folder_names(self):
        """
        Returns a list of the recognized top-level model folders in the topology section corresponding to the
        known WLST top-level folders.
        :return: a list of the recognized top-level model folder names
        """
        return self._alias_entries.get_model_topology_subfolder_names()

    def get_model_resources_top_level_folder_names(self):
        """
        Returns a list of the recognized top-level model folders in the resources section corresponding to the
        known WLST top-level folders.
        :return: a list of the recognized top-level model folder names
        """
        return self._alias_entries.get_model_resources_subfolder_names()

    def get_model_app_deployments_top_level_folder_names(self):
        """
        Returns a list of the recognized top-level model folders in the appDeployments section corresponding to the
        known WLST top-level folders.
        :return: a list of the recognized top-level model folder names
        """
        return self._alias_entries.get_model_app_deployments_subfolder_names()

    def get_model_subfolder_names(self, location):
        """
        Get the list of model folder names for subfolders of the specified location.
        :param location: the location
        :return: list[string]: the list of model subfolder names or an empty list if there are none
        :raises: AliasException: if an error occurs while getting or processing the folders for the specified location
        """
        return self._alias_entries.get_model_subfolder_names_for_location(location)

    def get_name_token(self, location):
        """
        Get the name token for the specified location.
        :param location: the location
        :return: the name token or None, if no new name token is required
        :raises: AliasException: if an error occurs while getting or processing the folder for the specified location
        """
        return self._alias_entries.get_name_token_for_location(location)

    def get_model_folder_path(self, location):
        """
        Get a slash delimited string of the path in the model to the specified location.
        :param location: the location
        :return: the model path string
        :raises: AliasException: if an error occurs while getting or processing the folders for the specified location
        """
        return self._alias_entries.get_model_folder_path_for_location(location)

    ###########################################################################
    #                      WLST Path-related methods                          #
    ###########################################################################

    def get_wlst_attributes_path(self, location):
        """
        Get the WLST path where the attributes for the specified location are found.
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_attribute_path_for_location(location)

    def get_wlst_subfolders_path(self, location):
        """
        Get the WLST path where the subfolders for the specified location are found.
        :param location: the location to use
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_subfolders_path_for_location(location)

    def get_wlst_list_path(self, location):
        """
        Get the WLST path where to list the existing instances of the type corresponding to the specified location.
        :param location: the location to use
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_list_path_for_location(location)

    def get_wlst_create_path(self, location):
        """
        Get the WLST path where to create new instances of the type corresponding to the specified location.
        :param location: the location to use
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_create_path_for_location(location)

    def get_wlst_flattened_folder_list_path(self, location):
        """
        Get the WLST path where to list the existing instances of the flattened type corresponding to
        the specified location.
        :param location: the location to use
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_flattened_folder_list_path_for_location(location)

    def get_wlst_flattened_folder_create_path(self, location):
        """
        Get the WLST path where to create new instances of the flattened type corresponding to the specified location.
        :param location: the location to use
        :return: the WLST path
        :raises AliasException: if the location is missing required name tokens or
                                the alias data for the location is bad
        """
        return self._alias_entries.get_wlst_flattened_folder_create_path_for_location(location)

    ###########################################################################
    #                    Child folder-related methods                         #
    ###########################################################################

    def requires_unpredictable_single_name_handling(self, location):
        """
        Does the location folder specified require unpredicatable single name handling?
        :param location: the location
        :return: True, if the location requires unpredicatable single name handling, False otherwise
        :raises: AliasException: if an error occurs while getting the folder for the location or if the
                                 specified type doesn't match and the actual type is 'none'
        """
        return self._alias_entries.is_location_child_folder_type(location, ChildFoldersTypes.SINGLE_UNPREDICTABLE)

    def supports_multiple_mbean_instances(self, location):
        """
        Does the location folder specified support multiple MBean instances of the parent node type?
        :param location: the location
        :return: True, if the location supports multiple named child nodes, False otherwise
        :raises: AliasException: if an error occurs while getting the folder for the location or if the
                                 specified type doesn't match and the actual type is 'none'
        """
        return self._alias_entries.is_location_child_folder_type(location, ChildFoldersTypes.MULTIPLE)

    def requires_artificial_type_subfolder_handling(self, location):
        """
        Does the location folder specified both support multiple MBean instances of the parent node type
        and require the use of a subtype, defined by an contained subfolder, to create the MBeans?
        :param location: the location
        :return: True, if so, False otherwise
        :raises: AliasException: if an error occurs while getting the folder for the location or if the
                                 specified type doesn't match and the actual type is 'none'
        """
        return self._alias_entries.is_location_child_folder_type(location,
                                                                 ChildFoldersTypes.MULTIPLE_WITH_TYPE_SUBFOLDER)

    def supports_single_mbean_instance(self, location):
        """
        Does the location folder specified support only a single MBean instance of the parent node type?
        :param location: the location
        :return: True, if so, False otherwise
        :raises: AliasException: if an error occurs while getting the folder for the location or if the
                                 specified type doesn't match and the actual type is 'none'
        """
        return self._alias_entries.is_location_child_folder_type(location, ChildFoldersTypes.SINGLE)

    def is_artificial_type_folder(self, location):
        """
        Is the location folder specified an artificial subtype folder?
        :param location: the location
        :return: True, if so, False otherwise
        :raises: AliasException: if an error occurs while getting the folder for the location
        """
        return self._alias_entries.is_location_child_folder_type(location, ChildFoldersTypes.NONE)

    ###########################################################################
    #                     WLST Folder create-related methods                  #
    ###########################################################################

    def get_wlst_mbean_name(self, location):
        """
        Get the WLST MBean name for the specified location
        :param location: the location to use
        :return: the WLST MBean name
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        return self._alias_entries.get_wlst_mbean_name_for_location(location)

    def get_wlst_mbean_type(self, location):
        """
        Get the WLST MBean type for the specified location
        :param location: the location to use
        :return: the WLST MBean type
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        return self._alias_entries.get_wlst_mbean_type_for_location(location)

    def is_flattened_folder(self, location):
        """
        Is the current location one that contains a flattened WLST folder?
        :param location: the location
        :return: True, if the specified location contains a flattened WLST tuple of folders, False otherwise
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        return self._alias_entries.location_contains_flattened_folder(location)

    def get_wlst_flattened_mbean_name(self, location):
        """
        Get the flattened WLST folder name.
        :param location: the location
        :return: the flattened folder name
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        return self._alias_entries.get_wlst_flattened_name_for_location(location)

    def get_wlst_flattened_mbean_type(self, location):
        """
        Get the flattened WLST folder type.
        :param location: the location
        :return: the flattened folder type
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        return self._alias_entries.get_wlst_flattened_type_for_location(location)

    ###########################################################################
    #                   WLST attribute-related methods                        #
    ###########################################################################

    def get_wlst_attribute_name_and_value(self, location, model_attribute_name, model_attribute_value,
                                          existing_wlst_value=None):
        """
        Returns the WLST attribute name and value for the specified model attribute name and value.

        wlst_attribute_value should return the correct type and value, even if the value
        is the default value for model_attribute_name.
        :param location: the location to use
        :param model_attribute_name: string
        :param model_attribute_value: value of the appropriate type
        :param existing_wlst_value: existing value of the appropriate type
        :return: the WLST name and value (which may be None)
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        _method_name = 'get_wlst_attribute_name_and_value'

        wlst_attribute_name = None
        wlst_attribute_value = None

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        if model_attribute_name not in module_folder[ATTRIBUTES]:
            ex = exception_helper.create_alias_exception('WLSDPLY-08004', model_attribute_name,
                                                         location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        attribute_info = module_folder[ATTRIBUTES][model_attribute_name]

        if attribute_info and not self.__is_model_attribute_read_only(location, attribute_info):
            wlst_attribute_name = attribute_info[WLST_NAME]
            if USES_PATH_TOKENS in attribute_info and string_utils.to_boolean(attribute_info[USES_PATH_TOKENS]):
                model_attribute_value = self._model_context.replace_token_string(model_attribute_value)

            data_type = attribute_info[WLST_TYPE]
            if data_type == 'password':
                try:
                    wlst_attribute_value = self.__decrypt_password(model_attribute_value)
                except EncryptionException, ee:
                    ex = exception_helper.create_alias_exception('WLSDPLY-08011', model_attribute_name,
                                                                 location.get_folder_path(),
                                                                 ee.getLocalizedMessage(), error=ee)
                    self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                    raise ex
            else:
                if data_type in ALIAS_LIST_TYPES or data_type in ALIAS_MAP_TYPES:
                    merge = True
                    if MERGE in attribute_info:
                        merge = alias_utils.convert_boolean(attribute_info[MERGE])

                    if merge and data_type in ALIAS_MAP_TYPES:
                        model_val = TypeUtils.convertToType(PROPERTIES, model_attribute_value)
                        existing_val = TypeUtils.convertToType(PROPERTIES, existing_wlst_value)
                        merged_value = alias_utils.merge_model_and_existing_properties(model_val, existing_val)
                    elif merge and alias_utils.is_attribute_server_start_arguments(location, model_attribute_name):
                        merged_value = \
                            alias_utils.merge_server_start_argument_values(model_attribute_value, existing_wlst_value)
                    elif merge:
                        model_val = TypeUtils.convertToType(LIST, model_attribute_value)
                        existing_val = TypeUtils.convertToType(LIST, existing_wlst_value)
                        merged_value = alias_utils.merge_model_and_existing_lists(model_val, existing_val)
                    else:
                        merged_value = model_attribute_value

                    if data_type == JARRAY:
                        subtype = 'java.lang.String'
                        if SET_MBEAN_TYPE in attribute_info:
                            subtype = attribute_info[SET_MBEAN_TYPE]
                        wlst_attribute_value = alias_utils.convert_to_type(data_type, merged_value, subtype=subtype)
                    else:
                        wlst_attribute_value = alias_utils.convert_to_type(data_type, merged_value)
                else:
                    wlst_attribute_value = alias_utils.convert_to_type(data_type, model_attribute_value)

        return wlst_attribute_name, wlst_attribute_value

    def get_wlst_attribute_name(self, location, model_attribute_name):
        """
        Returns the WLST attribute name and value for the specified model attribute name and value.

        wlst_attribute_value should return the correct type and value, even if the value
        is the default value for model_attribute_name.
        :param location:
        :param model_attribute_name:
        :return: the WLST attribute name or None, if it is not relevant
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        _method_name = 'get_wlst_attribute_name'

        self._logger.entering(location, model_attribute_name, class_name=self._class_name, method_name=_method_name)
        wlst_attribute_name = None
        alias_attr_dict = self._alias_entries.get_alias_attribute_entry_by_model_name(location, model_attribute_name)
        if alias_attr_dict is not None and not self.__is_model_attribute_read_only(location, alias_attr_dict):
            if WLST_NAME in alias_attr_dict:
                wlst_attribute_name = alias_attr_dict[WLST_NAME]
            else:
                ex = exception_helper.create_alias_exception('WLSDPLY-08053', model_attribute_name, location, WLST_NAME)
                self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                raise ex

        return wlst_attribute_name

    def get_wlst_get_required_attribute_names(self, location):
        """
        Get the list of attribute names that have their get_method specified as GET.
        :param location: the location
        :return: list[string]: the list of attribute names
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        _method_name = 'get_wlst_get_required_attribute_names'

        wlst_attribute_names = []

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_METHOD in value and value[GET_METHOD] == GET:
                wlst_attribute_names.append(value[WLST_NAME])

        return wlst_attribute_names

    def get_wlst_lsa_required_attribute_names(self, location):
        """
        Get the list of attribute names that have their get_method specified as LSA.
        :param location: the location
        :return: list[string]: the list of attribute names
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        _method_name = 'get_wlst_lsa_required_attribute_names'

        wlst_attribute_names = []

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_METHOD in value and value[GET_METHOD] == LSA:
                wlst_attribute_names.append(value[WLST_NAME])

        return wlst_attribute_names

    def get_wlst_get_returns_mbean_attribute_names_and_types(self, location):
        """
        Get the dictionary of attribute names and types that have their get_mbean_type specified.
        :param location: the location
        :return: dictionary: a dictionary with the attribute names as keys and the MBean types as values
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """
        _method_name = 'get_wlst_get_required_attribute_names'

        wlst_attribute_names = dict()

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_MBEAN_TYPE in value:
                wlst_attribute_names[value[WLST_NAME]] = value[GET_MBEAN_TYPE]
            else:
                wlst_attribute_names[value[WLST_NAME]] = None

        return wlst_attribute_names

    ###########################################################################
    #                    Model folder-related methods                         #
    ###########################################################################

    def get_model_subfolder_name(self, location, wlst_subfolder_name):
        """
        Get the model folder name for the WLST subfolder name at the specified location.
        :param location: the location
        :param wlst_subfolder_name: the WLST folder name
        :return: the model folder name, or None if the folder is not needed for the model.
        :raises: AliasException: if an error occurs due to a bad location or bad alias data
        """

        model_subfolder_name = None

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        for key, value in module_folder[FOLDERS].iteritems():
            # value will be None if the folder is not the correct version
            if value is not None:
                wlst_type = value[WLST_TYPE]
                if (wlst_subfolder_name == wlst_type) or \
                        (FLATTENED_FOLDER_DATA in value and WLST_TYPE in value[FLATTENED_FOLDER_DATA] and
                         wlst_subfolder_name == value[FLATTENED_FOLDER_DATA][WLST_TYPE]):
                    model_subfolder_name = key
                    break

        return model_subfolder_name

    def is_valid_model_folder_name(self, location, model_folder_name):
        """
        Return whether or not location's model folders list has a subfolder
        with the name assigned to the model_folder_name parameter.

        :param location: the location
        :param model_folder_name: the model folder name
        :return: ValidationCode, message
        :raises: AliasException: if an error occurred
        """
        _method_name = 'is_valid_model_folder_name'

        self._logger.entering(str(location), model_folder_name,
                              class_name=self._class_name, method_name=_method_name)
        result, valid_version_range = \
            self._alias_entries.is_valid_model_folder_name_for_location(location, model_folder_name)

        if result == ValidationCodes.VALID:
            message = exception_helper.get_message('WLSDPLY-08071', model_folder_name,
                                                   location.get_folder_path(), self._wls_version)
        elif result == ValidationCodes.INVALID:
            message = exception_helper.get_message('WLSDPLY-08072', model_folder_name,
                                                   location.get_folder_path(), self._wls_version)
        elif result == ValidationCodes.VERSION_INVALID:
            message = \
                VersionUtils.getValidFolderVersionRangeMessage(model_folder_name, location.get_folder_path(),
                                                               self._wls_version, valid_version_range,
                                                               WlstModes.from_value(self._wlst_mode))
        else:
            ex = exception_helper.create_alias_exception('WLSDPLY-08045', model_folder_name,
                                                         location.get_folder_path(), self._wls_version,
                                                         ValidationCodes.from_value(result))
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        self._logger.exiting(class_name=self._class_name, method_name=_method_name, result=result)
        return result, message

    ###########################################################################
    #                  Model attribute-related methods                        #
    ###########################################################################

    def get_model_password_type_attribute_names(self, location):
        """
        Get the attributes in the current location whose types are passwords.
        :param location: the location
        :return: list of the attribute names
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_password_type_attribute_names'

        password_attribute_names = []
        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if WLST_TYPE in value and value[WLST_TYPE] == 'password':
                password_attribute_names.append(key)
        return password_attribute_names


    def get_model_restart_required_attribute_names(self, location):
        """
        :param location: Model folder name
        :return: list[string] Model attribute names at specified location
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_restart_required_attribute_names'

        restart_attribute_names = []

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if RESTART_REQUIRED in value:
                restart_required_value = value[RESTART_REQUIRED]
                if "true" == restart_required_value.lower():
                    restart_attribute_names.append(key)

        return restart_attribute_names

    def get_model_get_required_attribute_names(self, location):
        """
        Get the list of attribute names that have their get_method specified as GET.
        :param location: the location
        :return: list[string]: the list of attribute names
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_get_required_attribute_names'

        wlst_attribute_names = []

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_METHOD in value and value[GET_METHOD] == GET:
                wlst_attribute_names.append(key)

        return wlst_attribute_names

    def get_model_lsa_required_attribute_names(self, location):
        """
        Get the model attribute names that require the use of LSA to get the accurate value from WLST.
        :param location: the location
        :return: the list of attribute names
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_lsa_required_attribute_names'

        lsa_required_attribute_names = []

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_METHOD in value and LSA in value[GET_METHOD]:
                lsa_required_attribute_names.append(key)

        return lsa_required_attribute_names

    def get_model_get_returns_mbean_attribute_names_and_types(self, location):
        """
        Get the dictionary of attribute names and types that have their get_mbean_type specified.
        :param location: the location
        :return: dictionary: a dictionary with the attribute names as keys and the MBean types as values
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_get_returns_mbean_attribute_names_and_types'

        model_attribute_names = dict()

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if GET_MBEAN_TYPE in value:
                model_attribute_names[key] = value[GET_MBEAN_TYPE]
            else:
                model_attribute_names[key] = None

        return model_attribute_names

    def get_model_mbean_set_method_attribute_names_and_types(self, location):
        """
        Get the list of model attribute names and types where the set method requires an MBean.
        :param location: the location
        :return: a dictionary keyed by model attribute names with the set_method and set_mbean_type fields set
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_mbean_set_method_attribute_names_and_types'

        model_attributes_dict = dict()

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if SET_METHOD in value and value[SET_METHOD].startswith(MBEAN):
                attr_dict = dict()

                attr_set_method_name = None
                set_method_value_components = value[SET_METHOD].split('.')
                if len(set_method_value_components) == 2:
                    attr_set_method_name = set_method_value_components[1]

                attr_dict[SET_METHOD] = attr_set_method_name
                if SET_MBEAN_TYPE in value:
                    attr_dict[SET_MBEAN_TYPE] = value[SET_MBEAN_TYPE]
                else:
                    attr_dict[SET_MBEAN_TYPE] = None

                model_attributes_dict[key] = attr_dict

        return model_attributes_dict

    def get_model_merge_required_attribute_names(self, location):
        """
        Get the list of attribute names where merging the new and old values is required.
        :param location: the location
        :return: dictionary: a list of the model attribute names
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_merge_required_attribute_names'

        model_attribute_names = list()

        module_folder = self._alias_entries.get_dictionary_for_location(location)
        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if WLST_TYPE in value and (value[WLST_TYPE] in ALIAS_LIST_TYPES or value[WLST_TYPE] in ALIAS_MAP_TYPES):
                merge = True
                if MERGE in value:
                    merge = alias_utils.convert_boolean(value[MERGE])
                if merge:
                    model_attribute_names.append(key)

        return model_attribute_names

    def get_model_attribute_name_and_value(self, location, wlst_attribute_name, wlst_attribute_value):
        """
        Returns the model attribute name and value for the specified WLST attribute name and value.

        model_attribute_value will be set to None, if value assigned to wlst_attribute_value arg
        is the default value for model_attribute_name.
        :param location: the location
        :param wlst_attribute_name: the WLST attribute name
        :param wlst_attribute_value: the WLST attribute value
        :return: the name and value
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_attribute_name_and_value'

        self._logger.entering(str(location), wlst_attribute_name, wlst_attribute_value,
                              class_name=self._class_name, method_name=_method_name)
        model_attribute_name = None
        # Assume wlst_attribute_value is the same as default value of model_attribute_name
        model_attribute_value = None

        attribute_info = self._alias_entries.get_alias_attribute_entry_by_wlst_name(location, wlst_attribute_name)
        if attribute_info is not None:
            data_type, delimiter = \
                alias_utils.compute_read_data_type_and_delimiter_from_attribute_info(attribute_info,
                                                                                     wlst_attribute_value)

            converted_value = alias_utils.convert_to_type(data_type, wlst_attribute_value, delimiter=delimiter)
            model_attribute_name = attribute_info[MODEL_NAME]
            default_value = attribute_info[VALUE][DEFAULT]
            if data_type == 'password':
                if wlst_attribute_value is None or converted_value == default_value:
                    model_attribute_value = None
                else:
                    model_attribute_value = "--FIX ME--"
            elif data_type == 'boolean':
                wlst_val = alias_utils.convert_boolean(converted_value)
                default_val = alias_utils.convert_boolean(default_value)
                if wlst_val == default_val:
                    model_attribute_value = None
                else:
                    model_attribute_value = converted_value
            elif (data_type in ALIAS_LIST_TYPES or data_type in ALIAS_MAP_TYPES) and \
                    (converted_value is None or len(converted_value) == 0):
                if default_value == '[]' or default_value == 'None':
                    model_attribute_value = None
            elif str(converted_value) != str(default_value):
                model_attribute_value = converted_value
                if USES_PATH_TOKENS in attribute_info:
                    model_attribute_value = self._model_context.tokenize_path(model_attribute_value)

        if wlst_attribute_name not in ('Id', 'Tag', 'Name') and model_attribute_name is None:
            ex = exception_helper.create_alias_exception('WLSDPLY-08007', wlst_attribute_name,
                                                         location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex
        self._logger.exiting(class_name=self._class_name, method_name=_method_name,
                             result={model_attribute_name: model_attribute_value})
        return model_attribute_name, model_attribute_value

    def get_model_attribute_names_and_types(self, location):
        """
        Returns the model attribute name and type for the specified WLST attribute name and value.
        :param location:
        :return: a dictionary keyed on model attribute names with the type as the value
        :raises: AliasException: if an error occurs
        """
        _method_name = 'get_model_attribute_names_and_types'

        self._logger.entering(str(location), class_name=self._class_name, method_name=_method_name)
        result = {}
        attributes_dict = self._alias_entries.get_alias_attribute_entries_by_location(location)
        for key, value in attributes_dict.iteritems():
            if PREFERRED_MODEL_TYPE in value:
                result[key] = value[PREFERRED_MODEL_TYPE]
            elif WLST_TYPE in value:
                result[key] = value[WLST_TYPE]
            else:
                result[key] = None

        self._logger.exiting(class_name=self._class_name, method_name=_method_name, result=result)
        return result

    def attribute_values_are_equal(self, location, model_attribute_name, model_attribute_value, wlst_attribute_value):
        """
        Returns whether or not the model and WLST values for a given model attribute,
        should be considered equal.

        :param location:
        :param model_attribute_name:
        :param model_attribute_value:
        :param wlst_attribute_value:
        :return: boolean
        :raises: AliasException: if an error occurs
        """

        _method_name = 'attribute_values_are_equal'

        result = False

        module_folder = self._alias_entries.get_dictionary_for_location(location)

        if ATTRIBUTES not in module_folder:
            ex = exception_helper.create_alias_exception('WLSDPLY-08002', location.get_folder_path())
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        for key, value in module_folder[ATTRIBUTES].iteritems():
            if key == model_attribute_name:
                attribute_info = module_folder[ATTRIBUTES][key]
                if attribute_info and VALUE in attribute_info and DEFAULT in attribute_info[VALUE]:
                    result = (model_attribute_value == wlst_attribute_value
                              and model_attribute_value == attribute_info[VALUE][DEFAULT])

        return result

    def is_valid_model_attribute_name(self, location, model_attribute_name):
        """
        Return whether or not location's model folders list has an attribute
        with the name assigned to the model_attribute_name parameter.

        If so, it returns True and a message stating that value assigned to
        model_attribute_name parameter is supported in the specified WLST
        version. Otherwise, it returns False and a message stating which, if
        any, WLST version(s) the value assigned to the model_attribute_name
        parameter is supported in.

        :param location: the location
        :param model_attribute_name: the model attribute name
        :return: ValidationCode, message
        :raises: AliasException: if an error occurred
        """
        _method_name = 'is_wlst_version_model_attribute_name'

        self._logger.entering(str(location), model_attribute_name,
                              class_name=self._class_name, method_name=_method_name)
        result, valid_version_range = \
            self._alias_entries.is_valid_model_attribute_name_for_location(location, model_attribute_name)

        if result == ValidationCodes.VALID:
            message = exception_helper.get_message('WLSDPLY-08040', model_attribute_name,
                                                   location.get_folder_path(), self._wls_version)
        elif result == ValidationCodes.INVALID:
            message = exception_helper.get_message('WLSDPLY-08041', model_attribute_name,
                                                   location.get_folder_path(), self._wls_version)
        elif result == ValidationCodes.VERSION_INVALID:
            message = \
                VersionUtils.getValidAttributeVersionRangeMessage(model_attribute_name, location.get_folder_path(),
                                                                  self._wls_version, valid_version_range,
                                                                  WlstModes.from_value(self._wlst_mode))
        else:
            ex = exception_helper.create_alias_exception('WLSDPLY-08045', model_attribute_name,
                                                         location.get_folder_path(), self._wls_version,
                                                         ValidationCodes.from_value(result))
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        self._logger.exiting(class_name=self._class_name, method_name=_method_name, result=result)
        return result, message

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __decrypt_password(self, text):
        """
        Internal method to determine if the provided password text needs to be decrypted
        :param text: the text to check and decrypt, if needed
        :return: the clear text
        :raises EncryptionException: if an error occurs while decrypting the password
        """
        if text is None or len(str(text)) == 0 or \
                not self._model_context.is_using_encryption() or\
                not EncryptionUtils.isEncryptedString(text):

            rtnval = text
        else:
            passphrase = self._model_context.get_encryption_passphrase()
            rtnval = EncryptionUtils.decryptString(text, String(passphrase).toCharArray())

        return rtnval

    def __is_model_attribute_read_only(self, location, attribute_info):
        """
        Is the model attribute read-only?
        :param location: the location
        :param attribute_info: the attribute tuple
        :return: True if the attribute is read-only, False otherwise
        """
        _method_name = '__is_model_attribute_read_only'
        rtnval = False
        if ACCESS in attribute_info and attribute_info[ACCESS] in ('RO', 'VO'):
            self._logger.finer('WLSDPLY-08049', attribute_info[MODEL_NAME], location.get_folder_path(),
                               WlstModes.from_value(self._wlst_mode),
                               class_name=self._class_name, method_name=_method_name)
            rtnval = True

        return rtnval