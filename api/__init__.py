import os
import re
import sys
import importlib

__all__ = []

for file in os.listdir(os.path.dirname(__file__)):
    if re.search(f"\.py", file):
        continue
    mod_name = f"api.{file}"
    if mod_name in sys.modules:
        pass
    elif (spec := importlib.util.find_spec(mod_name)) is not None:
        # If you chose to perform the actual import ...
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        __all__.append(module)
    else:
        print(f"can't find the {mod_name!r} module")


__all__ = tuple(__all__)
