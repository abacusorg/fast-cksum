project(
    'fast_cksum',
    'cpp',
    version: '0.1.0',
    meson_version: '>= 1.1',
    default_options: [
        'cpp_std=gnu++17',
        'c_std=gnu17',
        'debug=true',
        'optimization=3',
        'b_lto=true',
    ],
)

if get_option('optimization') == '3'
    add_project_arguments(['-Ofast'], language: 'cpp')
endif

if not meson.is_cross_build()
    add_project_arguments(['-march=native'], language: 'cpp')
endif

include = include_directories('src', 'include')

if get_option('py')
    # TODO: figure out if we want binaries installed via Python,
    # and what to do about helper bin scripts.
    py = import('python').find_installation(pure: false)

    py.install_sources(
        'py/fast_cksum/context_timer.py',
        'py/fast_cksum/cksum_io.py',
        'py/fast_cksum/cksum_ffi.py',
        'py/fast_cksum/cksum_merge.py',
        'py/fast_cksum/__init__.py',
        subdir: 'fast_cksum',
    )

    # the venv/bin dir
    # scripts_dir = py.get_variable('scripts')

    fast_cksum_lib = shared_library(
        'fast_cksum',
        'src/fast_cksum.cpp',
        include_directories: include,
        install: true,
        # We are only using the shared library from Python for now.
        install_dir: py.get_install_dir() / 'fast_cksum',
    )
endif

if get_option('cli')
    fast_cksum = executable(
        'fast_cksum',
        'src/cli/fast_cksum_cli.cpp',
        include_directories: include,
        install: true,
    )

    fast_cksum_store = executable(
        'fast_cksum_store',
        'src/cli/fast_cksum_store.cpp',
        include_directories: include,
        install: true,
    )

    fast_cksum_cat = executable(
        'fast_cksum_cat',
        'src/cli/fast_cksum_cat.cpp',
        include_directories: include,
        install: true,
    )
endif

fast_cksum_source_dep = declare_dependency(
    include_directories: include,
    sources: 'src/fast_cksum.cpp',
)
