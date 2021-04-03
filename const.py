class _const(object):
    def __setattr__(self, name, value):
        self.__dict__[name]=value

    def __delattr__(self, name):
        return

import sys
sys.modules[__name__]=_const()
