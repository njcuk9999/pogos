from typing import Any, Dict, List

from pogos.constants import constants as pconst


class PogoDemo():
    """
    A class to store all the information about a demo, including the title, the
    instrument, the description, the date, the author, the url, the download links,
    the redsteps, the yaml file, the object, the keywords, and the constants.
    """
    classname = 'PogoDemo'
    title: str
    tmodes: List[str] = []
    object: str
    keywords: List[str]
    instrument: str
    description: str
    date: str
    author: str
    id: str
    url: str
    download: Dict[str, str] = dict()
    redsteps: Dict[str, List[Any]] = dict()
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
            tmode = '_'.join(self.tmodes)
            # replace ":" with ""
            tmode = tmode.replace(':', '')
            # if the property has {tmodes} in it, replace it with the
            # tmode string
            if '{tmodes}' in prop_inst:
                return str(prop_inst).format(tmodes=tmode)
            # otherwise just return the property
            else:
                return prop_inst
