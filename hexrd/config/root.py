import os
import logging
import sys

from hexrd.utils.decorators import memoized

from .config import Config
from .instrument import InstrumentConfig
from .findorientations import FindOrientationsConfig
from .fitgrains import FitGrainsConfig
from .imageseries import ImageSeriesConfig
from .material import MaterialConfig
from .multiproc import MultiprocessingConfig
from .utils import null


logger = logging.getLogger('hexrd.config')



class RootConfig(Config):


    _dirty = False


    @property
    def analysis_name(self):
        return str(self.get('analysis_name', default='analysis'))
    @analysis_name.setter
    def analysis_name(self, val):
        self.set('analysis_name', val)


    @property
    def analysis_dir(self):
        return os.path.join(self.working_dir, self.analysis_name)


    @property
    def dirty(self):
        return self._dirty


    @property
    def find_orientations(self):
        return FindOrientationsConfig(self)


    @property
    def fit_grains(self):
        return FitGrainsConfig(self)


    @property
    def image_series(self):
        return ImageSeriesConfig(self)


    @property
    def instrument(self):
        return InstrumentConfig(self)


    @property
    def material(self):
        return MaterialConfig(self)


    @property
    def multiprocessing(self):
        return MultiprocessingConfig(self)

    @property
    def working_dir(self):
        try:
            temp = self.get('working_dir')
            if not os.path.exists(temp):
                raise IOError(
                    '"working_dir": "%s" does not exist', temp
                    )
            return temp
        except RuntimeError:
            temp = os.getcwd()
            was_dirty = self.dirty
            self.working_dir = temp
            if not was_dirty:
                self._dirty = False
            logger.info(
                '"working_dir" not specified, defaulting to "%s"' % temp
                )
            return temp
    @working_dir.setter
    def working_dir(self, val):
        val = os.path.abspath(val)
        if not os.path.isdir(val):
            raise IOError('"working_dir": "%s" does not exist' % val)
        self.set('working_dir', val)


    def dump(self, filename):
        import yaml

        with open(filename, 'w') as f:
            yaml.dump(self._cfg, f)
        self._dirty = False


    def get(self, key, default=null):
        args = key.split(':')
        args, item = args[:-1], args[-1]
        temp = self._cfg
        for arg in args:
            temp = temp.get(arg, {})
            # intermediate block may be None:
            temp = {} if temp is None else temp
        try:
            res = temp[item]
        except KeyError:
            if default is not null:
                logger.info(
                    '%s not specified, defaulting to %s', key, default
                    )
                res = temp.get(item, default)
            else:
                raise RuntimeError(
                    '%s must be specified in configuration file' % key
                    )
        return res


    def set(self, key, val):
        args = key.split(':')
        args, item = args[:-1], args[-1]
        temp = self._cfg
        for arg in args:
            temp = temp.get(arg, {})
            # intermediate block may be None:
            temp = {} if temp is None else temp
        if temp.get(item, null) != val:
            temp[item] = val
            self._dirty = True
