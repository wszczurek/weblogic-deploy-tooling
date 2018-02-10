/*
 * Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
 * The Universal Permissive License (UPL), Version 1.0
 */
package oracle.weblogic.deploy.util;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

import oracle.weblogic.deploy.exception.ExceptionHelper;
import oracle.weblogic.deploy.logging.PlatformLogger;
import oracle.weblogic.deploy.logging.WLSDeployLogFactory;

/**
 * Utility methods related to file handling.
 */
public final class FileUtils {
    private static final String CLASS = FileUtils.class.getName();
    private static final PlatformLogger LOGGER = WLSDeployLogFactory.getLogger("wlsdeploy.util");
    private static final boolean WINDOWS = File.separatorChar == '\\';

    private static final int NUMBER_OF_FILENAME_COMPONENTS = 2;
    private static final int FILE_NAME_POS = 0;
    private static final int FILE_EXT_POS = 1;

    private FileUtils() {
        // hide the constructor for this utility class
    }

    /**
     * Get the specified resource as an InputStream.
     *
     * @param fileName the resource to get
     * @return the InputStream, or null if it was not found
     */
    public static InputStream getResourceAsStream(String fileName) {
        return FileUtils.class.getClassLoader().getResourceAsStream(fileName);
    }

    /**
     * Convert a file path into one that Jython will handle.
     *
     * @param filename the filename to convert
     * @return the converted filename that is Jython compatible
     */
    public static String fixupFileSeparatorsForJython(String filename) {
        String newFileName = filename;
        if (WINDOWS) {
            newFileName = newFileName.replace('\\', '/');
        }
        return newFileName;
    }

    /**
     * Create a temporary directory.
     *
     * @param parent the parent directory
     * @param dirBaseName the base name for the new directory
     * @return the temporary directory file
     * @throws IOException if an error occurs while create the temporary directory
     */
    public static File createTempDirectory(File parent, String dirBaseName) throws IOException {
        return getCanonicalFile(Files.createTempDirectory(parent.toPath(), dirBaseName).toFile());
    }

    /**
     * Create a temporary directory.
     *
     * @param dirBaseName the base name for the new directory
     * @return the temporary directory file
     * @throws IOException if an error occurs while create the temporary directory
     */
    public static File createTempDirectory(String dirBaseName) throws IOException {
        return getCanonicalFile(Files.createTempDirectory(dirBaseName).toFile());
    }

    /**
     * A exception free version of getCanonicalFile() that falls back to the absolute file if getCanonicalFile fails.
     *
     * @param f the input file
     * @return the canonical file
     */
    public static File getCanonicalFile(File f) {
        File canonicalFile = null;
        if (f != null) {
            try {
                canonicalFile = f.getCanonicalFile();
            } catch (IOException ioe) {
                LOGGER.warning("WLSDPLY-03000", ioe, f.getPath(), ioe.getLocalizedMessage());
                canonicalFile = f.getAbsoluteFile();
            }
        }
        return canonicalFile;
    }

    /**
     * This method validates that the specified file name is an existing file that is not a directory.
     *
     * @param fileName the file name to validate
     * @return the canonical file representing the file name
     * @throws IllegalArgumentException if the file name is not valid or does not exist
     */
    public static File validateExistingFile(String fileName) {
        final String METHOD = "validateFileName";

        LOGGER.entering(CLASS, METHOD, fileName);
        File file = FileUtils.validateFileName(fileName);
        if (!file.exists()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03002", file.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, file);
        return file;
    }

    /**
     * This method validates that the specified directory name is an existing directory.
     *
     * @param directoryName the directory name to validate
     * @return the canonical file representing the directory name
     * @throws IllegalArgumentException if the directory name is empty,
     *     not a directory, or the directory does not exist
     */
    public static File validateExistingDirectory(String directoryName) {
        final String METHOD = "validateExistingDirectory";

        LOGGER.entering(CLASS, METHOD, directoryName);
        File directory = FileUtils.validateDirectoryName(directoryName);
        if (!directory.exists()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03069", directory.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, directory);
        return directory;
    }

    /**
     * This method validates that the specified file name is writable.
     *
     * @param fileName the file name to validate
     * @return the canonical file representing the file name
     * @throws IllegalArgumentException if the file name is not valid or is not writable
     */
    public static File validateWritableFile(String fileName) {
        final String METHOD = "validateWritableFile";

        LOGGER.entering(CLASS, METHOD, fileName);
        File file = FileUtils.validateFileName(fileName);
        if (file.exists() && !file.canWrite()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03004", file.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, file);
        return file;
    }

    /**
     * This method validates that the specified directory name is writable.
     *
     * @param directoryName the directory name to validate
     * @return the canonical file representing the directory name
     * @throws IllegalArgumentException if the directory name is not valid, doesn't exist, or is not writable
     */
    public static File validateWritableDirectory(String directoryName) {
        final String METHOD = "validateWritableDirectory";

        LOGGER.entering(CLASS, METHOD, directoryName);
        File directory = FileUtils.validateDirectoryName(directoryName);
        if (directory.exists() && !directory.canWrite()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03004", directory.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, directory);
        return directory;
    }

    /**
     * Parses the filename to separate the base name and extension.
     *
     * @param f File object to use
     * @return 2 element array (where the first element is the base name and the second is the extension)
     *          or null if the argument is null
     */
    public static String[] parseFileName(File f) {
        if (f == null) {
            return new String[0];
        }
        return parseFileName(f.getName());
    }

    /**
     * Parses the filename to separate the base name and extension.
     *
     * @param filename the file name to parse
     * @return 2 element array where the first element is the base name and the second is the extension,
     *      or null if the argument was either null or an empty string
     */
    public static String[] parseFileName(String filename) {

        if (StringUtils.isEmpty(filename)) {
            return new String[0];
        }

        String[] nameComponents = new String[NUMBER_OF_FILENAME_COMPONENTS];
        int idx = filename.lastIndexOf('.');
        switch (idx) {
            case -1:
                // no extension
                nameComponents[FILE_NAME_POS] = filename;
                nameComponents[FILE_EXT_POS] = "";
                break;

            case 0:
                // dot file or "."
                if (filename.length() > 1) {
                    nameComponents[FILE_NAME_POS] = "";
                    nameComponents[FILE_EXT_POS] = filename.substring(1);
                } else {
                    nameComponents[FILE_NAME_POS] = ".";
                    nameComponents[FILE_EXT_POS] = "";
                }
                break;

            default:
                if (filename.length() > idx) {
                    // normal case
                    nameComponents[FILE_NAME_POS] = filename.substring(0, idx);
                    nameComponents[FILE_EXT_POS] = filename.substring(idx + 1);
                } else {
                    //pathological case
                    nameComponents[FILE_NAME_POS] = filename.substring(0, idx);
                    nameComponents[FILE_EXT_POS] = "";
                }
                break;
        }
        return nameComponents;
    }

    /**
     * Whether or not the specified file has a YAML file extension.
     *
     * @param file the file
     * @return true, if the file extension matches the known YAML file extensions
     */
    public static boolean isYamlFile(File file) {
        String fileName = file.getName().toLowerCase(Locale.ENGLISH);
        return fileName.endsWith(".yaml") || fileName.endsWith(".yml");
    }

    /**
     * Whether or not the specified file has a JSON file extension.
     *
     * @param file the file
     * @return true, if the file extension matches the known JSON file extensions
     */
    public static boolean isJsonFile(File file) {
        String fileName = file.getName().toLowerCase(Locale.ENGLISH);
        return fileName.endsWith(".json");
    }

    /**
     * Whether or not the specified file has a ZIP extension.
     *
     * @param file the file
     * @return true, if the file extension matches the known ZIP file extensions
     */
    public static boolean isZipFile(File file) {
        String fileName = file.getName().toLowerCase(Locale.ENGLISH);
        return fileName.endsWith(".zip");
    }

    /**
     * Get the model file from the specified, existing directory.
     *
     * @param modelDirectory the existing directory location to search for a model file.
     * @return the model file or null, if it does not exist
     * @throws IllegalArgumentException if the directory is not a valid, existing, and readable directory
     * @throws IllegalStateException if the modelDirectory contains more than one YAML and/or JSON file
     */
    public static File getModelFile(File modelDirectory) {
        final String METHOD = "getModelFile";

        LOGGER.entering(CLASS, METHOD, modelDirectory);
        if (modelDirectory == null) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03005", METHOD, CLASS, "modelDirectory");
            IllegalArgumentException iae = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        } else if (!modelDirectory.exists()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03069", modelDirectory.getAbsolutePath());
            IllegalArgumentException iae = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        } else if (!modelDirectory.isDirectory()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03070", modelDirectory.getAbsolutePath());
            IllegalArgumentException iae = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        } else if (!modelDirectory.canRead()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03071", modelDirectory.getAbsolutePath());
            IllegalArgumentException iae = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }

        File[] dirEntries;
        try {
            dirEntries = modelDirectory.listFiles(new ModelFilenameFilter());
        } catch (SecurityException se) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03072", se,
                modelDirectory.getAbsolutePath(), se.getLocalizedMessage());
            IllegalArgumentException iae = new IllegalArgumentException(message, se);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }

        File modelFile = getModelFileFromArray(dirEntries, modelDirectory);
        LOGGER.exiting(CLASS, METHOD, modelFile);
        return modelFile;
    }

    /**
     * Find the model filename from the list.
     *
     * @param filenames the list of filenames
     * @param modelDirectoryName the directory name (for logging purposes only)
     * @return the model file name or null, if it was not found
     * @throws IllegalStateException if the modelDirectory contains more than one YAML and/or JSON file
     */
    public static String getModelFileName(List<String> filenames, String modelDirectoryName) {
        return getModelFileNameFromList(filenames, modelDirectoryName);
    }

    /**
     * Validate the file for the provided file name and return a File object handle. The file name
     * must not be a directory
     *
     * @param fileName of the file to validate
     * @return File handle for the file name
     * @throws IllegalArgumentException if the file name is empty or is a directory
     */
    public static File validateFileName(String fileName) {
        final String METHOD = "validateFileName";

        LOGGER.entering(CLASS, METHOD, fileName);
        if (StringUtils.isEmpty(fileName)) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03001");
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }

        File file = FileUtils.getCanonicalFile(new File(fileName));
        if (file.isDirectory()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03003", file.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, file);
        return file;
    }

    /**
     * Validate the directory for the provided directory name and return a File object handle.
     * The directory name must not be a directory.
     *
     * @param directoryName of the file to validate
     * @return File handle for the file name
     * @throws IllegalArgumentException if the directory name is empty or is not a directory
     */
    public static File validateDirectoryName(String directoryName) {
        final String METHOD = "validateDirectoryName";

        LOGGER.entering(CLASS, METHOD, directoryName);
        if (StringUtils.isEmpty(directoryName)) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03083");
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }

        File directory = FileUtils.getCanonicalFile(new File(directoryName));
        if (!directory.isDirectory()) {
            String message = ExceptionHelper.getMessage("WLSDPLY-03070", directory.getAbsolutePath());
            IllegalArgumentException iae  = new IllegalArgumentException(message);
            LOGGER.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        LOGGER.exiting(CLASS, METHOD, directory);
        return directory;
    }

    /**
     * Delete a directory and all of its contents, recursively.
     *
     * @param directory the directory to delete
     */
    public static void deleteDirectory(File directory) {
        LOGGER.entering(directory);
        if (directory != null) {
            LOGGER.finest("WLSDPLY-03108", directory.getAbsolutePath());
            File[] listing = directory.listFiles();
            if (listing != null) {
                LOGGER.finest("WLSDPLY-03109", directory.getAbsolutePath(), listing.length);
                for (File entry : listing) {
                    if (entry.isDirectory()) {
                        LOGGER.finest("WLSDPLY-03110", directory.getAbsolutePath(), entry.getAbsolutePath());
                        deleteDirectory(entry);
                    } else {
                        String dirPath = directory.getAbsolutePath();
                        String fileName = entry.getAbsolutePath();
                        LOGGER.finest("WLSDPLY-03111", dirPath, fileName);
                        if (!entry.delete()) {
                            LOGGER.finer("WLSDPLY-03112", fileName, dirPath);
                        }
                    }
                }
            }
            if (!directory.delete()) {
                LOGGER.finer("WLSDPLY-03113", directory);
            }
        }
        LOGGER.exiting(directory);
    }

    ///////////////////////////////////////////////////////////////////////////
    // Private helper methods                                                //
    ///////////////////////////////////////////////////////////////////////////

    private static File getModelFileFromArray(File[] files, File modelDirectory) {
        File modelFile = null;
        if (files != null && files.length > 0) {
            modelFile = getModelFileFromList(Arrays.asList(files), modelDirectory);
        }
        return modelFile;
    }

    private static String getModelFileNameFromList(List<String> filenames, String modelDirectoryName) {
        String result = null;
        if (filenames != null && !filenames.isEmpty()) {
            List<File> files = new ArrayList<>(filenames.size());
            for (String filename : filenames) {
                files.add(new File(filename));
            }
            File modelFile = getModelFileFromList(files, new File(modelDirectoryName));
            if (modelFile != null) {
                result = modelFile.getPath();
            }
        }
        return result;
    }

    private static File getModelFileFromList(List<File> files, File modelDirectory) {
        final String METHOD = "getModelFileFromList";

        File modelFile = null;
        if (files != null && !files.isEmpty()) {
            File yamlFile = null;
            File jsonFile = null;

            for (File file : files) {
                if (FileUtils.isYamlFile(file)) {
                    if (yamlFile == null) {
                        yamlFile = file;
                    } else {
                        String message = ExceptionHelper.getMessage("WLSDPLY-03073", modelDirectory.getAbsolutePath(),
                            "YAML", file.getName(), yamlFile.getName());
                        IllegalStateException ise = new IllegalStateException(message);
                        LOGGER.throwing(CLASS, METHOD, ise);
                        throw ise;
                    }
                } else if (isJsonFile(file)) {
                    if (jsonFile == null) {
                        jsonFile = file;
                    } else {
                        String message = ExceptionHelper.getMessage("WLSDPLY-03073", modelDirectory.getAbsolutePath(),
                            "JSON", file.getName(), jsonFile.getName());
                        IllegalStateException ise = new IllegalStateException(message);
                        LOGGER.throwing(CLASS, METHOD, ise);
                        throw ise;
                    }
                }
            }
            if (yamlFile != null) {
                modelFile = yamlFile;
            } else if (jsonFile != null) {
                modelFile = jsonFile;
            }
        }
        return modelFile;
    }

    private static class ModelFilenameFilter implements FilenameFilter {
        public boolean accept(File dir, String name) {
            boolean result = false;
            if (!StringUtils.isEmpty(name)) {
                File f = new File(dir, name);
                if (FileUtils.isYamlFile(f) || FileUtils.isJsonFile(f)) {
                    result = true;
                }
            }
            return result;
        }
    }
}