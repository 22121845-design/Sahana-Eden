"""
Common JS/CSS includes for Sahana Eden.

Provides helper functions to inject CSS and JS resources during
page rendering. All logic is kept compatible with the original
Sahana framework; no functional behaviour is changed.

Refactored for:
    - Improved readability
    - Reduced code duplication
    - Clearer helper abstractions
    - Consistent naming and comments
"""

import os

from gluon import current, HTTP, URL, XML


# =============================================================================
# Helper Functions
# =============================================================================

def _abs_theme_config_path(request, theme):
    """
    Compute absolute path to the active theme's css.cfg file.

    Args:
        request: web2py request object
        theme: name of the active theme folder

    Returns:
        Absolute path to modules/templates/<theme>/css.cfg
    """
    return os.path.join(
        request.folder, "modules", "templates", theme, "css.cfg"
    )


def _stylesheet_link_tag(appname, css_file):
    """
    Build an HTML <link> tag pointing to static/styles/<css_file>.

    Args:
        appname: current web2py app name
        css_file: relative path under static/styles

    Returns:
        HTML <link> tag as a string
    """
    return (
        f'<link href="/{appname}/static/styles/{css_file}" '
        f'rel="stylesheet" type="text/css" />'
    )


def _append_script(scripts, appname, script_path):
    """
    Append a script from static/scripts into s3.scripts.

    Args:
        scripts: s3.scripts list
        appname: current app name
        script_path: relative path under static/scripts
    """
    scripts.append(f"/{appname}/static/scripts/{script_path}")


# =============================================================================
# CSS Includes
# =============================================================================

def include_debug_css():
    """
    Include all CSS listed in the active theme's css.cfg file.

    css.cfg lives under:
        modules/templates/<theme>/css.cfg

    Non-comment lines represent paths under static/styles/.
    """

    request = current.request
    response = current.response

    theme = response.s3.theme_config
    cfg_path = _abs_theme_config_path(request, theme)

    if not os.path.isfile(cfg_path):
        raise HTTP(
            500,
            f"Missing theme CSS config: modules/templates/{theme}/css.cfg",
        )

    app = request.application
    links = []

    with open(cfg_path, "r") as cfg:
        for line in cfg:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            links.append(_stylesheet_link_tag(app, line))

    return XML("\n".join(links))


# =============================================================================
# JavaScript Includes (Debug Mode)
# =============================================================================

def include_debug_js():
    """
    Include JS scripts listed in static/scripts/tools/sahana.js.cfg.

    mergejsmf.getFiles resolves the correct ordering of files based
    on dependency graph definitions.
    """

    request = current.request
    scripts_dir = os.path.join(request.folder, "static", "scripts")

    # Local import to avoid unnecessary overhead
    import mergejsmf

    config_map = {
        ".": scripts_dir,
        "ui": scripts_dir,
        "web2py": scripts_dir,
        "S3": scripts_dir,
    }

    cfg_file = os.path.join(scripts_dir, "tools", "sahana.js.cfg")

    # Outputs: (config_dict, file_list)
    _, file_list = mergejsmf.getFiles(config_map, cfg_file)

    app = request.application
    template = f'<script src="/{app}/static/scripts/%s"></script>'

    scripts = "\n".join(template % path for path in file_list)
    return XML(scripts)


# =============================================================================
# DataTables Includes
# =============================================================================

def include_datatable_js():
    """
    Include required DataTables JS files based on:
        - s3.debug (debug or minified)
        - s3.datatable_opts (responsive, variable_columns)
    """

    s3 = current.response.s3
    scripts = s3.scripts
    options = s3.datatable_opts or {}
    debug = s3.debug

    app = current.request.application

    def add(script):
        """Append JS script using static/scripts."""
        _append_script(scripts, app, script)

    # Core datatable
    add("jquery.dataTables.js" if debug else "jquery.dataTables.min.js")

    # Extensions
    if options.get("responsive"):
        add("jquery.dataTables.responsive.js" if debug
            else "jquery.dataTables.responsive.min.js")

    if options.get("variable_columns"):
        add("S3/s3.ui.columns.js" if debug
            else "S3/s3.ui.columns.min.js")

    # Eden datatable wrapper
    add("S3/s3.ui.datatable.js" if debug else "S3/s3.ui.datatable.min.js")


# =============================================================================
# ExtJS Includes
# =============================================================================

def _extjs_xtheme_tag(appname, xtheme, path):
    """
    Construct the CSS <link> tag for ExtJS xtheme.

    Args:
        appname: current application name
        xtheme: the filename of the theme CSS
        path: base CDN or local path

    Returns:
        <link> tag HTML
    """
    if xtheme:
        return (
            f"<link href='/{appname}/static/themes/{xtheme}' "
            f"rel='stylesheet' type='text/css' />"
        )
    return None


def include_ext_js():
    """
    Include ExtJS resources for map components.

    Handles:
        - CDN vs local script selection
        - Debug vs minified builds
        - XTheme injection
        - Avoids duplicate inclusion via s3.ext_included
    """

    s3 = current.response.s3
    if s3.ext_included:
        return

    request = current.request
    app = request.application

    # Handle theme
    xtheme = current.deployment_settings.get_base_xtheme()
    if xtheme:
        xtheme = f"{xtheme[:-3]}min.css"  # convert "...css" -> "...min.css"

    # Select CDN or local base path
    base = (
        "//cdn.sencha.com/ext/gpl/3.4.1.1"
        if s3.cdn else f"/{app}/static/scripts/ext"
    )

    # JS files (debug/minified)
    if s3.debug:
        adapter = f"{base}/adapter/jquery/ext-jquery-adapter-debug.js"
        main_js = f"{base}/ext-all-debug.js"
        main_css = (
            f"<link href='{base}/resources/css/ext-all-notheme.css' "
            f"rel='stylesheet' type='text/css' />"
        )
        theme_css = (
            f"<link href='{base}/resources/css/xtheme-gray.css' "
            f"rel='stylesheet' type='text/css' />"
        ) if not xtheme else None
    else:
        adapter = f"{base}/adapter/jquery/ext-jquery-adapter.js"
        main_js = f"{base}/ext-all.js"
        main_css = (
            f"<link href='/{app}/static/scripts/ext/...-notheme.min.css' "
            f"rel='stylesheet' type='text/css' />"
        )
        theme_css = None

    # Register JS scripts
    scripts = s3.scripts
    scripts.append(adapter)
    scripts.append(main_js)

    # Add language file if available
    langfile = f"ext-lang-{s3.language}.js"
    lang_path = os.path.join(
        request.folder, "static", "scripts", "ext",
        "src", "locale", langfile
    )

    if os.path.exists(lang_path):
        scripts.append(f"{base}/src/locale/{langfile}")

    # Inject CSS into DOM via jQuery ready
    inject = s3.jquery_ready.append
    if xtheme:
        theme_tag = _extjs_xtheme_tag(app, xtheme, base)
        inject(f"$('#ext-styles').after(\"{theme_tag}\").after(\"{main_css}\").remove()")
    else:
        css_tag = theme_css or main_css
        inject(f"$('#ext-styles').after(\"{css_tag}\").remove()")

    s3.ext_included = True


# =============================================================================
# Underscore.js Includes
# =============================================================================

def include_underscore_js():
    """
    Include Underscore.js, using CDN when configured.

    Used by:
        - Map templates
        - GroupedOptsWidget
    """

    s3 = current.response.s3
    debug = s3.debug
    scripts = s3.scripts

    if s3.cdn:
        base = "//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.6.0/"
        script = base + ("underscore.js" if debug else "underscore-min.js")
    else:
        script = URL(
            c="static",
            f=f"scripts/underscore{'-min' if not debug else ''}.js"
        )

    if script not in scripts:
        scripts.append(script)


# END =========================================================================
