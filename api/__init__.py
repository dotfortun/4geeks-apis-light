import os
import re
import sys
import importlib

__all__ = []

for item in os.listdir(os.path.dirname(__file__)):
    if re.search(f"\.py", item):
        continue
    mod_name = f"api.{item}"
    if mod_name in sys.modules:
        pass
    elif (spec := importlib.util.find_spec(mod_name)) is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        __all__.append(module)
    else:
        print(f"can't find the {mod_name!r} module")


__all__ = tuple(__all__)
