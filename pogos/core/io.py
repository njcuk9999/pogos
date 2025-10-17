#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-17 at 15:06

@author: cook
"""
import datetime
import glob
import os
from string import Template
from typing import Any, Dict

import numpy as np

from aperocore.base import base as aperobase
from aperocore.constants.constant_functions import ConstantsDict
from aperocore.constants.param_functions import ParamDict
from aperocore.constants.param_functions import SubParamDict
from aperocore.core import drs_log
from aperocore.core import drs_misc
from pogos.core import base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.core.io.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# get the Drs Exceptions
AperoCodedException = drs_log.AperoCodedException
AperoCodedWarning = drs_log.AperoCodedWarning
# get display func
display_func = drs_misc.display_func
# Get Logging function
WLOG = drs_log.wlog
# define html template file path
PACKAGE_PATH = os.path.dirname(os.path.dirname(__file__))
HTML_TEMPLATE_FILE = os.path.join(PACKAGE_PATH, 'resources',
                                  'html_template.html')


# =============================================================================
# Define variables
# =============================================================================
# TODO: This is a carbon-copy of the sossisse functionality --> move to aperocore

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def params_to_html(params: ParamDict, html: str = ''):
    """
    Convert a dictionary of parameters to an html list
    in the form of a bulleted list as follows

    - key: value

    :param params: dict, the dictionary of parameters
    :param html: str, the initial html string

    :return: str, the html string
    """
    # define the html string
    html += '<ul>'

    # sort keys alphabetically
    keys = np.sort(params.keys())
    # loop around all parameters
    for key in keys:
        # do not add these keys
        if key.startswith('DRS.'):
            continue
        if key.startswith('LOG.'):
            continue
        if key == 'RECIPE_SHORT':
            continue
        # get the raw value
        rawvalue = params[key]
        # ignore param dicts
        if isinstance(rawvalue, (ParamDict, SubParamDict, ConstantsDict)):
            continue
        # deal with lists
        if isinstance(rawvalue, (list, np.ndarray)):
            # quick check for valid sub-list data
            subvalues = []
            for val in rawvalue:
                if isinstance(val, (ParamDict, SubParamDict, ConstantsDict)):
                    continue
                else:
                    subvalues.append(val)
            # deal with no valid values
            if len(subvalues) == 0:
                continue
            # create a sub-list
            html += f'<li><b>{key}</b>:<ul>'
            for val in subvalues:
                html += f'<li> - {val}</li>'
            # end the list
            html += '</ul></li>'
        # deal with dictionaries
        elif isinstance(rawvalue, dict):
            # quick check for valid sub-dict data
            subvalues = dict()
            for subkey in rawvalue:
                val = rawvalue[subkey]
                if isinstance(val, (ParamDict, SubParamDict, ConstantsDict)):
                    continue
                else:
                    subvalues[subkey] = val
            # deal with no valid values
            if len(subvalues) == 0:
                continue
            # create a sub-list
            html += f'<li><b>{key}</b>:<ul>'
            for subkey in subvalues:
                html += f'<li> - {subkey}: {rawvalue[subkey]}</li>'
            # end the list
            html += '</ul></li>'
        # else convert to string
        else:
            value = str(rawvalue)
            # create a list item
            html += '<li><b>{0}</b>: {1}</li>'.format(key, value)
    # end the list
    html += '</ul>'
    # return the html string
    return html


def plots_to_html(params: ParamDict, plot_path: str):
    """
    Grab the png files from the PLOT_PATH and push them into html

    :param params:
    :return:
    """
    # get plot file
    plotfile = os.path.join(params[plot_path], 'plots.yaml')
    # read yaml file
    plotdict = aperobase.load_yaml(plotfile)
    # define the html string
    html = '<br>'
    # counter for figures
    figcounter = 1
    # order the plotdict by time subkey
    plotdict = dict(sorted(plotdict.items(),
                           key=lambda item: item[1].get('time', 0)))
    # loop around all png files
    for png_file in plotdict:
        # get the filename
        abspath = os.path.join(params[plot_path], f'{png_file}.png')
        # skip files that don't exist
        if not os.path.exists(abspath):
            continue
        # get basename
        basename = os.path.basename(abspath)
        # get title and description
        title = plotdict[png_file]['title']
        description = plotdict[png_file]['description']
        # create the html string
        html_image = f'<h3>Figure {figcounter}: {title}</h3>\n'
        if description is not None:
            html_image += f'<br>{description}<br>\n'
        html_image += (f'<img src="{basename}" alt="{png_file}" '
                       f'style="width:"600"">\n')
        html_image += '<br><br><br>\n'
        html += html_image
        # increment figure counter
        figcounter += 1
    # return the html string
    return html


def files_to_html(params: ParamDict, sid_name: str):
    """
    Grab the csv files from the PLOT_PATH and push them into html

    :param params:
    :return:
    """
    # get all files in SID path
    csv_files = glob.glob(os.path.join(params['PATHS.OTHER_PATH'], '*.csv'))
    # define the html string
    html = '<br><ul>'
    # loop around all csv files
    for csv_file in csv_files:
        # get the filename
        filename = os.path.basename(csv_file)
        # create the html string
        html_list = '<li><a href="{0}">{0}</a></li>'
        html += html_list.format(filename)
    # end the list
    html += '</ul>'
    # return the html string
    return html


def info_html(params: ParamDict, sid_name: str):

    # get time now
    timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # get version
    version = base.__version__
    vdate = base.__date__
    # push into html
    html = '<ul>'
    html += f'<li><b>Reduction date</b>: {timenow}</li>'
    html += f'<li><b>Version</b>: {version}</li>'
    html += f'<li><b>date</b>: {vdate}</li>'
    html += f'<li><b>SID</b>: {params[sid_name]}</li>'
    html += '</ul>'
    return html


def summary_html(params: ParamDict, module: str, plot_path: str,
                 sid_name: str, title: str, imode: str = None):
    """
    Create a summary html file

    :param params: ParamDict, the parameter dictionary of constants
    :param module: str, the module name
    :param plot_path: str, the path to the plots
    :param sid_name: str, the SID name
    :param objname: str, the object name
    :param imode: str, the instrument mode name

    :return:
    """
    # read the html template
    with open(HTML_TEMPLATE_FILE, 'r') as template_file:
        template = Template(template_file.read())
    # define the data to insert into the template
    data = dict()
    # add the data to the dictionary for the html sections
    targs = [module, title]
    # add title
    data['title'] = '{0} Summary: <br> {1}'.format(*targs)
    if imode is not None:
        data['title'] += f' [{imode}]'
    # add info section
    data['info'] = info_html(params, sid_name)
    # add plot section
    data['plots'] = plots_to_html(params, plot_path)
    # add file section
    data['filelist'] = files_to_html(params, sid_name)
    # add param section
    data['paramlist'] = params_to_html(params.get(module))
    # Substitute variables in the template
    rendered_html = template.safe_substitute(data)
    # construct filename for html file
    html_file = os.path.join(params[plot_path], 'index.html')
    # write the html file
    with open(html_file, 'w') as html_file:
        html_file.write(rendered_html)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
