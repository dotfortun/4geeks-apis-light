import os

from fastapi_babel import (
    Babel, BabelConfigs, _
)

configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="lang",
)
babel = Babel(configs=configs)

if __name__ == "__main__":
    babel.run_cli()
