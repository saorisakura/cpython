#ifndef Py_PYCORECONFIG_H
#define Py_PYCORECONFIG_H
#ifndef Py_LIMITED_API
#ifdef __cplusplus
extern "C" {
#endif

/* --- PyStatus ----------------------------------------------- */

typedef struct {
    enum {
        _PyStatus_TYPE_OK=0,
        _PyStatus_TYPE_ERROR=1,
        _PyStatus_TYPE_EXIT=2
    } _type;
    const char *func;
    const char *err_msg;
    int exitcode;
} PyStatus;

PyAPI_FUNC(PyStatus) PyStatus_Ok(void);
PyAPI_FUNC(PyStatus) PyStatus_Error(const char *err_msg);
PyAPI_FUNC(PyStatus) PyStatus_NoMemory(void);
PyAPI_FUNC(PyStatus) PyStatus_Exit(int exitcode);
PyAPI_FUNC(int) PyStatus_IsError(PyStatus err);
PyAPI_FUNC(int) PyStatus_IsExit(PyStatus err);
PyAPI_FUNC(int) PyStatus_Exception(PyStatus err);

/* --- PyWideStringList ------------------------------------------------ */

typedef struct {
    /* If length is greater than zero, items must be non-NULL
       and all items strings must be non-NULL */
    Py_ssize_t length;
    wchar_t **items;
} PyWideStringList;

PyAPI_FUNC(PyStatus) PyWideStringList_Append(PyWideStringList *list,
    const wchar_t *item);
PyAPI_FUNC(PyStatus) PyWideStringList_Insert(PyWideStringList *list,
    Py_ssize_t index,
    const wchar_t *item);


/* --- PyPreConfig ----------------------------------------------- */

typedef struct PyPreConfig {
    int _config_init;     /* _PyConfigInitEnum value */

    /* Parse Py_PreInitializeFromBytesArgs() arguments?
       See PyConfig.parse_argv */
    int parse_argv;

    /* If greater than 0, enable isolated mode: sys.path contains
       neither the script's directory nor the user's site-packages directory.

       Set to 1 by the -I command line option. If set to -1 (default), inherit
       Py_IsolatedFlag value. */
    /*
        ### Python Isolated 模式概述

        Python 的 `-I` 或 `--isolated` 命令行选项用于以隔离模式启动 Python 解释器。这种模式下，解释器会忽略用户级别的配置，如环境变量和用户 site-packages，使运行环境更加干净、可重现。

        ### 主要特点和使用场景

        1. **环境隔离**：忽略 `PYTHONPATH`、`PYTHONHOME` 等环境变量，避免外部配置干扰。
        2. **测试环境**：确保测试在标准环境中运行，提高结果可靠性。
        3. **打包工具**：在构建和分发 Python 包时，确保不依赖本地环境。
        4. **脚本沙盒**：运行不受信任的脚本时减少潜在风险。
        5. **可重现性**：保证代码在不同环境中行为一致。

        ### 使用示例

        下面是一个展示 isolated 模式效果的示例：


            
            


        ### 运行对比

        1. **标准模式**：
        ```bash
        python check_env.py
        ```
        输出会包含 `PYTHONPATH` 环境变量和用户 site-packages 目录。

        2. **隔离模式**：
        ```bash
        python -I check_env.py
        ```
        输出会显示：
        - `sys.path` 不包含 `PYTHONPATH` 的内容
        - `PYTHONPATH` 被忽略（显示未设置）
        - 用户 site-packages 目录被排除

        ### 实际应用场景

        #### 1. 测试脚本
        ```bash
        python -I -m unittest mypackage.tests
        ```
        确保测试不依赖本地环境中的包。

        #### 2. 运行不受信任的代码
        ```bash
        python -I untrusted_script.py
        ```
        减少脚本访问本地系统资源的风险。

        #### 3. 构建打包工具
        ```bash
        python -I -m build --sdist --wheel .
        ```
        确保打包过程不依赖开发环境中的特定包。

        通过这些示例可以看到，isolated 模式提供了一个干净的 Python 运行环境，非常适合需要环境隔离和可重现性的场景。
    */
    int isolated;

    /* If greater than 0: use environment variables.
       Set to 0 by -E command line option. If set to -1 (default), it is
       set to !Py_IgnoreEnvironmentFlag. */
    int use_environment;

    /* Set the LC_CTYPE locale to the user preferred locale? If equals to 0,
       set coerce_c_locale and coerce_c_locale_warn to 0. */
    int configure_locale;

    /* Coerce the LC_CTYPE locale if it's equal to "C"? (PEP 538)

       Set to 0 by PYTHONCOERCECLOCALE=0. Set to 1 by PYTHONCOERCECLOCALE=1.
       Set to 2 if the user preferred LC_CTYPE locale is "C".

       If it is equal to 1, LC_CTYPE locale is read to decide if it should be
       coerced or not (ex: PYTHONCOERCECLOCALE=1). Internally, it is set to 2
       if the LC_CTYPE locale must be coerced.

       Disable by default (set to 0). Set it to -1 to let Python decide if it
       should be enabled or not. */
    int coerce_c_locale;

    /* Emit a warning if the LC_CTYPE locale is coerced?

       Set to 1 by PYTHONCOERCECLOCALE=warn.

       Disable by default (set to 0). Set it to -1 to let Python decide if it
       should be enabled or not. */
    int coerce_c_locale_warn;

#ifdef MS_WINDOWS
    /* If greater than 1, use the "mbcs" encoding instead of the UTF-8
       encoding for the filesystem encoding.

       Set to 1 if the PYTHONLEGACYWINDOWSFSENCODING environment variable is
       set to a non-empty string. If set to -1 (default), inherit
       Py_LegacyWindowsFSEncodingFlag value.

       See PEP 529 for more details. */
    int legacy_windows_fs_encoding;
#endif

    /* Enable UTF-8 mode? (PEP 540)

       Disabled by default (equals to 0).

       Set to 1 by "-X utf8" and "-X utf8=1" command line options.
       Set to 1 by PYTHONUTF8=1 environment variable.

       Set to 0 by "-X utf8=0" and PYTHONUTF8=0.

       If equals to -1, it is set to 1 if the LC_CTYPE locale is "C" or
       "POSIX", otherwise it is set to 0. Inherit Py_UTF8Mode value value. */
    int utf8_mode;

    /* If non-zero, enable the Python Development Mode.

       Set to 1 by the -X dev command line option. Set by the PYTHONDEVMODE
       environment variable. */
    int dev_mode;

    /* Memory allocator: PYTHONMALLOC env var.
       See PyMemAllocatorName for valid values. */
    int allocator;
} PyPreConfig;

PyAPI_FUNC(void) PyPreConfig_InitPythonConfig(PyPreConfig *config);
PyAPI_FUNC(void) PyPreConfig_InitIsolatedConfig(PyPreConfig *config);


/* --- PyConfig ---------------------------------------------- */

/* This structure is best documented in the Doc/c-api/init_config.rst file. */
typedef struct PyConfig {
    int _config_init;     /* _PyConfigInitEnum value */

    int isolated;
    int use_environment;
    int dev_mode;
    int install_signal_handlers;
    int use_hash_seed;
    unsigned long hash_seed;
    int faulthandler;
    int tracemalloc;
    int perf_profiling;
    int remote_debug;
    int import_time;
    int code_debug_ranges;
    int show_ref_count;
    int dump_refs;
    wchar_t *dump_refs_file;
    int malloc_stats;
    wchar_t *filesystem_encoding;
    wchar_t *filesystem_errors;
    wchar_t *pycache_prefix;
    int parse_argv;
    PyWideStringList orig_argv;
    PyWideStringList argv;
    PyWideStringList xoptions;
    PyWideStringList warnoptions;
    int site_import;
    int bytes_warning;
    int warn_default_encoding;
    int inspect;
    int interactive;
    int optimization_level;
    int parser_debug;
    int write_bytecode;
    int verbose;
    int quiet;
    int user_site_directory;
    int configure_c_stdio;
    int buffered_stdio;
    wchar_t *stdio_encoding;
    wchar_t *stdio_errors;
#ifdef MS_WINDOWS
    int legacy_windows_stdio;
#endif
    wchar_t *check_hash_pycs_mode;
    int use_frozen_modules;
    int safe_path;
    int int_max_str_digits;
    int thread_inherit_context;
    int context_aware_warnings;
#ifdef __APPLE__
    int use_system_logger;
#endif

    int cpu_count;
#ifdef Py_GIL_DISABLED
    int enable_gil;
    int tlbc_enabled;
#endif

    /* --- Path configuration inputs ------------ */
    int pathconfig_warnings;
    wchar_t *program_name;
    wchar_t *pythonpath_env;
    wchar_t *home;
    wchar_t *platlibdir;

    /* --- Path configuration outputs ----------- */
    int module_search_paths_set;
    PyWideStringList module_search_paths;
    wchar_t *stdlib_dir;
    wchar_t *executable;
    wchar_t *base_executable;
    wchar_t *prefix;
    wchar_t *base_prefix;
    wchar_t *exec_prefix;
    wchar_t *base_exec_prefix;

    /* --- Parameter only used by Py_Main() ---------- */
    int skip_source_first_line;
    wchar_t *run_command;
    wchar_t *run_module;
    wchar_t *run_filename;

    /* --- Set by Py_Main() -------------------------- */
    wchar_t *sys_path_0;

    /* --- Private fields ---------------------------- */

    // Install importlib? If equals to 0, importlib is not initialized at all.
    // Needed by freeze_importlib.
    int _install_importlib;

    // If equal to 0, stop Python initialization before the "main" phase.
    int _init_main;

    // If non-zero, we believe we're running from a source tree.
    int _is_python_build;

#ifdef Py_STATS
    // If non-zero, turns on statistics gathering.
    int _pystats;
#endif

#ifdef Py_DEBUG
    // If not empty, import a non-__main__ module before site.py is executed.
    // PYTHON_PRESITE=package.module or -X presite=package.module
    wchar_t *run_presite;
#endif
} PyConfig;

PyAPI_FUNC(void) PyConfig_InitPythonConfig(PyConfig *config);
PyAPI_FUNC(void) PyConfig_InitIsolatedConfig(PyConfig *config);
PyAPI_FUNC(void) PyConfig_Clear(PyConfig *);
PyAPI_FUNC(PyStatus) PyConfig_SetString(
    PyConfig *config,
    wchar_t **config_str,
    const wchar_t *str);
PyAPI_FUNC(PyStatus) PyConfig_SetBytesString(
    PyConfig *config,
    wchar_t **config_str,
    const char *str);
PyAPI_FUNC(PyStatus) PyConfig_Read(PyConfig *config);
PyAPI_FUNC(PyStatus) PyConfig_SetBytesArgv(
    PyConfig *config,
    Py_ssize_t argc,
    char * const *argv);
PyAPI_FUNC(PyStatus) PyConfig_SetArgv(PyConfig *config,
    Py_ssize_t argc,
    wchar_t * const *argv);
PyAPI_FUNC(PyStatus) PyConfig_SetWideStringList(PyConfig *config,
    PyWideStringList *list,
    Py_ssize_t length, wchar_t **items);


/* --- PyConfig_Get() ----------------------------------------- */

PyAPI_FUNC(PyObject*) PyConfig_Get(const char *name);
PyAPI_FUNC(int) PyConfig_GetInt(const char *name, int *value);
PyAPI_FUNC(PyObject*) PyConfig_Names(void);
PyAPI_FUNC(int) PyConfig_Set(const char *name, PyObject *value);


/* --- Helper functions --------------------------------------- */

/* Get the original command line arguments, before Python modified them.

   See also PyConfig.orig_argv. */
PyAPI_FUNC(void) Py_GetArgcArgv(int *argc, wchar_t ***argv);


// --- PyInitConfig ---------------------------------------------------------

typedef struct PyInitConfig PyInitConfig;

PyAPI_FUNC(PyInitConfig*) PyInitConfig_Create(void);
PyAPI_FUNC(void) PyInitConfig_Free(PyInitConfig *config);

PyAPI_FUNC(int) PyInitConfig_GetError(PyInitConfig* config,
    const char **err_msg);
PyAPI_FUNC(int) PyInitConfig_GetExitCode(PyInitConfig* config,
    int *exitcode);

PyAPI_FUNC(int) PyInitConfig_HasOption(PyInitConfig *config,
    const char *name);
PyAPI_FUNC(int) PyInitConfig_GetInt(PyInitConfig *config,
    const char *name,
    int64_t *value);
PyAPI_FUNC(int) PyInitConfig_GetStr(PyInitConfig *config,
    const char *name,
    char **value);
PyAPI_FUNC(int) PyInitConfig_GetStrList(PyInitConfig *config,
    const char *name,
    size_t *length,
    char ***items);
PyAPI_FUNC(void) PyInitConfig_FreeStrList(size_t length, char **items);

PyAPI_FUNC(int) PyInitConfig_SetInt(PyInitConfig *config,
    const char *name,
    int64_t value);
PyAPI_FUNC(int) PyInitConfig_SetStr(PyInitConfig *config,
    const char *name,
    const char *value);
PyAPI_FUNC(int) PyInitConfig_SetStrList(PyInitConfig *config,
    const char *name,
    size_t length,
    char * const *items);

PyAPI_FUNC(int) PyInitConfig_AddModule(PyInitConfig *config,
    const char *name,
    PyObject* (*initfunc)(void));

PyAPI_FUNC(int) Py_InitializeFromInitConfig(PyInitConfig *config);


#ifdef __cplusplus
}
#endif
#endif /* !Py_LIMITED_API */
#endif /* !Py_PYCORECONFIG_H */
