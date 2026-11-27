#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skeleton structure for all demo classes

These apply to all demo classes do not edit for a specific demo
- edit the individual demo class files (e.g. soss_demo.py)

Created on 2025-03-25 at 09:57

@author: cook
"""


from typing import Any, Dict, List, Optional, Union

from aperocore.constants import custom_const_classes

from pogos.constants import constants as pconst
from pogos.core import file_download
# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'demos.py'


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
    # id - identifies the demo and selected reduction stages
    id: str
    # url - the POGOS data server directory for this demo
    #   (used by files with source: pogos, see pogos_files)
    url: str
    # legacy download dictionary (no longer used - file constants now carry
    #   their own source, see mast_files / pogos_files)
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

    def mast_files(self, filelist: Union[str, List[str], None], pid: int,
                   obsnumber: int, product: str,
                   **extras: Any) -> Dict[str, Any]:
        """
        File constant value for files downloaded from MAST

        :param filelist: str, list of str or None, the file(s) to use (None
                         uses every matching MAST product)
        :param pid: int, the JWST program ID
        :param obsnumber: int, the observation number in the program
        :param product: str, the MAST product suffix e.g. uncal, rateints
        :param extras: optional keys e.g. match=['nrs1'], min_size_mb=1

        :return: dict, the mapping form of the file constant
        """
        value = dict(filelist=filelist, source='mast', pid=pid,
                     obsnumber=obsnumber, product=product)
        value.update(extras)
        return value

    def pogos_files(self, filelist: Union[str, List[str]],
                    product: Optional[str] = None,
                    **extras: Any) -> Dict[str, Any]:
        """
        File constant value for files downloaded from the POGOS data server

        :param filelist: str or list of str, the file(s) on the server
                         (in self.url)
        :param product: str or None, the kind of file (None: the constant
                        default) e.g. product='fits' for a custom WAVE_FILE
        :param extras: any constant specific extra keys

        :return: dict, the mapping form of the file constant
        """
        value = dict(filelist=filelist, source='pogos', url=self.url)
        if product is not None:
            value['product'] = product
        value.update(extras)
        return value

    def data_sources(self) -> List[str]:
        """
        Describe where the demo input files come from (for the demo list)

        Uses a fresh copy of the demo (so this demo is not modified) with
        the selected reduction steps (all steps if none selected yet).

        :return: list of str, one line per source e.g.
                 'MAST (pid=1366, obsnumber=3): uncal, rateints'
        """
        # the selected reduction steps (all if none selected yet)
        steps = [step for step in self.redsteps if step in self.flavours]
        if len(steps) == 0:
            steps = list(self.redsteps)
        # cache (get_info is called many times while listing demos)
        cache_key = tuple(steps)
        cache = self.__dict__.setdefault('_data_cache', dict())
        if cache_key in cache:
            return cache[cache_key]
        # fill a fresh copy of this demo with the selected steps
        demo = type(self)()
        for step in steps:
            for method in demo.redsteps[step]:
                method()
        # main inputs produced by an earlier selected step are not
        #   downloaded (e.g. TSOVORE -> SOSSISSE)
        values = {key: const.value
                  for key, const in demo.cdict.storage.items()}
        chained = set(file_download.chained_keys(values))
        # group the file constants by source
        groups = dict()
        for key, const in demo.cdict.storage.items():
            if not isinstance(const, custom_const_classes.FileObjectConst):
                continue
            if key in chained:
                continue
            if const.value is None:
                continue
            fileobj = const.parse(const.value)
            if fileobj is None:
                continue
            if fileobj.source == 'mast':
                group = (f'MAST (pid={fileobj.pid}, '
                         f'obsnumber={fileobj.obsnumber})')
                item = fileobj.product
            elif fileobj.source == 'pogos':
                group = f'POGOS server ({fileobj.url})'
                item = key.split('.')[-1]
            else:
                group = 'local'
                item = key.split('.')[-1]
            items = groups.setdefault(group, [])
            if item not in items:
                items.append(item)
        # one line per source
        lines = [f'{group}: {", ".join(items)}'
                 for group, items in groups.items()]
        cache[cache_key] = lines
        return lines

    def get_info(self) -> Dict[str, Any]:
        """
        Get the information about the demo as a dictionary.
        :return:
        """
        info = dict()
        for prop in ['title', 'instrument', 'description', 'date', 'author',
                     'url', 'object', 'keywords']:
            info[prop] = self.get_prop(prop)
        # where the input data come from (MAST / POGOS server / local)
        info['data'] = self.data_sources()
        return info

