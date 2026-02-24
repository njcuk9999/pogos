#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skeleton structure for all demo classes

These apply to all demo classes do not edit for a specific demo
- edit the individual demo class files (e.g. soss_demo.py)

Created on 2025-03-25 at 09:57

@author: cook
"""


from typing import Any, Dict, List

from pogos.constants import constants as pconst
# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'soss_demo.py'


# =============================================================================
# Define demo classes
# =============================================================================
class PogoDemo():
    """
    A class to store all the information about a demo, including the title, the
    instrument, the description, the date, the author, the url, the download links,
    the redsteps, the yaml file, the object, the keywords, and the constants.
    """
    classname = 'PogoDemo'
    title: str
    # define the flavours selected by the user
    flavours: List[str] = []
    # define the string flavours (shortened versions of flavours for
    #  title and id)
    tflavours: List[str] = []
    # Object name (a filter - required)
    object: str
    # List of keywords (to be used as filters)
    keywords: List[str]
    # Instrument name
    instrument: str
    # Description (for YAML)
    description: str
    # Date of observation
    date: str
    # Author of the demo
    author: str
    # id - used for setting sub-directory
    id: str
    # url - used for downloading the data
    url: str
    # download dictionary of key (the file constant string) and
    # value (the directory constant string) - code looks up the url and
    # tries to find these "files" from file constnat string and copy them to
    # the directory constant string directory
    download: Dict[str, str] = dict()
    # list of all possible reduction steps - values are calls to methods
    # in the class (i.e. tsovore, miriam, sossisse) that modify cdict
    redsteps: Dict[str, List[Any]] = dict()
    # Where we store the constants - a ConstDict class
    # it will be filled generically and then via "redsteps" functions
    cdict: pconst.ConstDict

    def __str__(self):
        # get id without tmodes
        class_id = str(self.id)
        if '.{tmodes}' in class_id:
            class_id = class_id.replace('.{tmodes}', '')
        return f'{self.classname}[{class_id}]'

    def __repr__(self):
        return self.__str__()

    def startup(self):
        NotImplemented()

    def tsovore(self):
        NotImplemented()

    def miriam(self):
        NotImplemented()

    def sossisse(self):
        NotImplemented()

    def sorbet(self):
        NotImplemented()

    def sorbet_wlca(self):
        NotImplemented()

    def sorbet_slca(self):
        NotImplemented()

    # =========================================================================
    # Worker methods
    # ========================================================================
    def get_prop(self, prop):
        """
        Update the title and id based on the tmodes set.
        :return:
        """
        # deal with wrong properties
        if not hasattr(self, prop):
            raise AttributeError(f"Property {prop} not found in demo "
                                 f"{self.title}")
        # get property
        prop_inst = getattr(self, prop)
        # deal with non-strings just return the property
        if not isinstance(prop_inst, str):
            return prop_inst
        # deal with string (inserting tmode if needed)
        else:
            # get the tmodes and push into a string
            tflavour = '_'.join(self.tflavours)
            # replace ":" with ""
            tflavour = tflavour.replace(':', '')
            # if the property has {tmodes} in it, replace it with the
            # tmode string
            if '{tflavours}' in prop_inst:
                return str(prop_inst).format(tflavours=tflavour)
            # otherwise just return the property
            else:
                return prop_inst

    def get_info(self) -> Dict[str, Any]:
        """
        Get the information about the demo as a dictionary.
        :return:
        """
        info = dict()
        for prop in ['title', 'instrument', 'description', 'date', 'author',
                     'url', 'object', 'keywords']:
            info[prop] = self.get_prop(prop)
        return info
