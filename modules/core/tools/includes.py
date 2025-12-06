"""
    Common JS/CSS includes

    Copyright: (c) 2010-2022 Sahana Software Foundation

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

import os

from gluon import current, HTTP, URL, XML


# =============================================================================
# Helper functions
# =============================================================================

def _theme_css_config_path(request, theme_config):
    """
    Get the absolute path to the theme CSS configuration file.

    Args:
        request: the current web2py request object
        theme_config: name of the active theme configuration

    Returns:
        Absolute filesystem path to ``css.cfg`` for the active theme.
    """
    return os.path.join(request.folder,
                        "modules", "templates",
                        theme_config, "css.cfg")


def _build_stylesheet_link(appname, stylesheet_name):
    """
    Build an HTML <link> element for a stylesheet in ``static/styles``.

    Args:
        appname: the current application name
        stylesheet_name: relative filename under ``static/styles``

    Returns:
        HTML string containing a <link> tag.
    """
    return (
        '<link href="/{app}/static/styles/{css}" '
        'rel="stylesheet" type="text/css" />'
    ).format(app=appname, css=stylesheet_name)


# =============================================================================
def include_debug_css():
    """
    Generate HTML to include all CSS listed in the active theme
    ``css.cfg`` file.

    The file is expected at:

        modules/templates/<theme>/css.cfg

    Each non-comment, non-empty line is interpreted as a stylesheet path
    relative to ``static/styles``.
    """

    request = current.request
    response = current.response

    location = response.s3.theme_config
    filename = _theme_css_config_path(request, location)

    if not os.path.isfile(filename):
        raise HTTP(
            500,
            "Theme configuration file missing: "
            "modules/templates/%s/css.cfg" % location,
        )

    appname = request.application
    links = []

    with open(filename, "r") as css_cfg:
        for line in css_cfg:
            line = line.strip()
            # Skip comments and blank lines
            if not line or line.startswith("#"):
                continue
            links.append(_build_stylesheet_link(appname, line))

    return XML("\n".join(links))


# -----------------------------------------------------------------------------
def include_debug_js():
    """
    Generate HTML to include the JS scripts listed in
    ``static/scripts/tools/sahana.js.cfg``.

    The configuration file is resolved relative to the ``scripts`` directory
    and processed by ``mergejsmf.getFiles`` to obtain the ordered list of
    script files to include.
    """

    request = current.request

    scripts_dir = os.path.join(request.folder, "static", "scripts")

    # The mergejsmf module is only needed here, so import locally
    import mergejsmf

    config_dict = {
        ".": scripts_dir,
        "ui": scripts_dir,
        "web2py": scripts_dir,
        "S3": scripts_dir,
    }
    config_filename = os.path.join(scripts_dir, "tools", "sahana.js.cfg")

    # getFiles returns (config, files) -> we only need the second element
    _, files = mergejsmf.getFiles(config_dict, config_filename)

    script_template = '<script src="/%s/static/scripts/%%s"></script>' % (
        request.application
    )

    scripts = "\n".join(script_template % scriptname for scriptname in files)
    return XML(scripts)


# -----------------------------------------------------------------------------
def include_datatable_js():
    """
    Add DataTables JS files into the page.

    Uses ``response.s3.datatable_opts`` to decide whether to include
    optional scripts for:
        - responsive tables (``jquery.dataTables.responsive``)
        - variable columns (``S3/s3.ui.columns``)

    Respects the ``s3.debug`` flag to switch between debug and minified
    builds.
    """

    s3 = current.response.s3

    scripts = s3.scripts
    options = s3.datatable_opts or {}

    appname = current.request.application

    def _append_script(script_name):
        """Append a script path under ``static/scripts`` to ``s3.scripts``."""
        scripts.append("/%s/static/scripts/%s" % (appname, script_name))

    if s3.debug:
        # Debug versions
        _append_script("jquery.dataTables.js")
        if options.get("responsive"):
            _append_script("jquery.dataTables.responsive.js")
        if options.get("variable_columns"):
            _append_script("S3/s3.ui.columns.js")
        _append_script("S3/s3.ui.datatable.js")
    else:
        # Minified versions
        _append_script("jquery.dataTables.min.js")
        if options.get("responsive"):
            _append_script("jquery.dataTables.responsive.min.js")
        if options.get("variable_columns"):
            _append_script("S3/s3.ui.columns.min.js")
        _append_script("S3/s3.ui.datatable.min.js")


# -----------------------------------------------------------------------------
def include_ext_js():
    """
    Add ExtJS CSS and JS into the page for a map.

    Notes:
        - This is normally invoked from ``MAP.xml()``, which is too late
          to insert stylesheets into ``s3.[external_]stylesheets``, so
          styles must be injected dynamically.
        - Avoids re-including ExtJS by checking ``s3.ext_included``.
    """

    s3 = current.response.s3
    if s3.ext_included:
        # Ext already included
        return

    request = current.request
    appname = request.application

    # XTheme configuration (optional)
    xtheme = current.deployment_settings.get_base_xtheme()
    if xtheme:
        # convert "...css" -> "...min.css"
        xtheme = "%smin.css" % xtheme[:-3]
        xtheme = (
            "<link href='/{app}/static/themes/{theme}' "
            "rel='stylesheet' type='text/css' />"
        ).format(app=appname, theme=xtheme)

    # Choose between CDN and local ExtJS
    if s3.cdn:
        # For sites on the public internet, CDN may provide better performance
        PATH = "//cdn.sencha.com/ext/gpl/3.4.1.1"
    else:
        PATH = "/%s/static/scripts/ext" % appname

    # Main adapter / JS / CSS assets (debug vs minified)
    if s3.debug:
        # Debug versions
        adapter = "%s/adapter/jquery/ext-jquery-adapter-debug.js" % PATH
        main_js = "%s/ext-all-debug.js" % PATH
        main_css = (
            "<link href='%s/resources/css/ext-all-notheme.css' "
            "rel='stylesheet' type='text/css' />" % PATH
        )
        if not xtheme:
            xtheme = (
                "<link href='%s/resources/css/xtheme-gray.css' "
                "rel='stylesheet' type='text/css' />" % PATH
            )
    else:
        # Minified versions
        adapter = "%s/adapter/jquery/ext-jquery-adapter.js" % PATH
        main_js = "%s/ext-all.js" % PATH
        if xtheme:
            main_css = (
                "<link href='/%s/static/scripts/ext/...-notheme.min.css' "
                "rel='stylesheet' type='text/css' />" % appname
            )
        else:
            main_css = (
                "<link href='/%s/static/scripts/ext/...ext-gray.min.css' "
                "rel='stylesheet' type='text/css' />" % appname
            )

    # Register scripts
    scripts = s3.scripts
    scripts_append = scripts.append
    scripts_append(adapter)
    scripts_append(main_js)

    # Localized language file, if available
    langfile = "ext-lang-%s.js" % s3.language
    locale_path = os.path.join(
        request.folder,
        "static", "scripts", "ext", "src", "locale", langfile,
    )
    if os.path.exists(locale_path):
        locale = "%s/src/locale/%s" % (PATH, langfile)
        scripts_append(locale)

    # Inject styles into the DOM at the correct position
    if xtheme:
        s3.jquery_ready.append(
            '''$('#ext-styles').after("%s").after("%s").remove()'''
            % (xtheme, main_css)
        )
    else:
        s3.jquery_ready.append(
            '''$('#ext-styles').after("%s").remove()''' % main_css
        )

    s3.ext_included = True


# -----------------------------------------------------------------------------
def include_underscore_js():
    """
    Add Underscore.js into the page.

    Used by:
        - Map templates
        - GroupedOptsWidget (comments)
    """

    s3 = current.response.s3
    debug = s3.debug
    scripts = s3.scripts

    # Prefer CDN when configured
    if s3.cdn:
        if debug:
            script = (
                "//cdnjs.cloudflare.com/ajax/libs/"
                "underscore.js/1.6.0/underscore.js"
            )
        else:
            script = (
                "//cdnjs.cloudflare.com/ajax/libs/"
                "underscore.js/1.6.0/underscore-min.js"
            )
    else:
        if debug:
            script = URL(c="static", f="scripts/underscore.js")
        else:
            script = URL(c="static", f="scripts/underscore-min.js")

    if script not in scripts:
        scripts.append(script)


# END ========================================================================