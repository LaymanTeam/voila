#############################################################################
# Copyright (c) 2018, Voilà Contributors                                    #
# Copyright (c) 2018, QuantStack                                            #
#                                                                           #
# Distributed under the terms of the BSD 3-Clause License.                  #
#                                                                           #
# The full license is in the file LICENSE, distributed with this software.  #
#############################################################################

import json
import os
from jupyter_core.paths import jupyter_path

# Define our own ROOT and STATIC_ROOT
ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(ROOT, "static")

# Define DEV_MODE based on local project structure (this can be adjusted as needed)
DEV_MODE = os.path.exists(os.path.join(ROOT, "..", "setup.py")) and os.path.exists(
    os.path.join(ROOT, "..", "share", "jupyter")
)


def collect_template_paths(
    app_names, template_name="default", prune=False, root_dirs=None
):
    return collect_paths(
        app_names,
        template_name,
        include_root_paths=True,
        prune=prune,
        root_dirs=root_dirs,
    )


def collect_static_paths(
    app_names, template_name="default", prune=False, root_dirs=None
):
    return collect_paths(
        app_names,
        template_name,
        include_root_paths=False,
        prune=prune,
        root_dirs=root_dirs,
        subdir="static",
    )


def collect_paths(
    app_names,
    template_name="default",
    subdir=None,
    include_root_paths=True,
    prune=False,
    root_dirs=None,
):
    """
    Collect template or resource paths for the specified template name by searching
    in standard Jupyter data directories.
    """
    found_at_least_one = False
    paths = []
    full_paths = []  # only used for error reporting

    root_dirs = root_dirs or _default_root_dirs()

    # Find the template hierarchy
    template_names = _find_template_hierarchy(app_names, template_name, root_dirs)

    for tmpl_name in template_names:
        for root_dir in root_dirs:
            for app_name in app_names:
                app_dir = os.path.join(root_dir, app_name, "templates")
                path = os.path.join(app_dir, tmpl_name)
                if subdir:
                    path = os.path.join(path, subdir)
                if not prune or os.path.exists(path):
                    paths.append(path)
                    found_at_least_one = True
        # For error reporting, you might want to collect full paths here if needed.
        # (Optional: Uncomment if needed)
        # for root_dir in root_dirs:
        #     for app_name in app_names:
        #         full_paths.append(os.path.join(root_dir, app_name, "templates"))
    
    if include_root_paths:
        for root_dir in root_dirs:
            paths.append(root_dir)
            for app_name in app_names:
                paths.append(os.path.join(root_dir, app_name, "templates"))
    
    if not found_at_least_one:
        full_paths_str = "\n\t".join(full_paths)
        raise ValueError(
            "No template sub-directory with name {!r} found in the following paths:\n\t{}".format(
                template_name, full_paths_str
            )
        )
    return paths


def _default_root_dirs():
    # Use our own logic instead of relying on nbconvert.
    root_dirs = []
    if DEV_MODE:
        root_dirs.append(os.path.abspath(os.path.join(ROOT, "..", "share", "jupyter")))
    root_dirs.extend(jupyter_path())
    return root_dirs


def _find_template_hierarchy(app_names, template_name, root_dirs):
    template_names = []
    while template_name is not None:
        template_names.append(template_name)
        conf = {}
        for root_dir in root_dirs:
            for app_name in app_names:
                conf_file = os.path.join(
                    root_dir, app_name, "templates", template_name, "conf.json"
                )
                if os.path.exists(conf_file):
                    with open(conf_file) as f:
                        new_conf = json.load(f)
                        new_conf.update(conf)
                        conf = new_conf
        if "base_template" in conf:
            template_name = conf["base_template"]
        else:
            if template_name == "base":
                template_name = None
            else:
                template_name = "base"
    return template_names
