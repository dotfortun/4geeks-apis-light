# import importlib
# import sys
# import os
# import re

# for api_mod in os.listdir("./api"):
#     name = f"api.{api_mod}.models"
#     if name in sys.modules:
#         print(f"{name!r} already in sys.modules")
#     elif (spec := importlib.util.find_spec(name)) is not None:
#         module = importlib.util.module_from_spec(spec)
#         sys.modules[name] = module
#         spec.loader.exec_module(module)
#         print(f"{name!r} has been imported")
#     else:
#         print(f"can't find the {name!r} module")
