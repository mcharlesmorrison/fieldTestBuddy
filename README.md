# Field Test Buddy :heart:

## Install

```console
pip3 install -r requirements.txt
pip3 install -e .
```

## Development

ALWAYS be in a virtual env during development for the sake of Zappa. I do `python3 -m venv venv` to make `./venv`, then `source ./venv/bin/activate.sh` to enter the virtual environment, plus `. ~/secret_keys.sh` to add secret keys to your environment. Doing `source ~/.bashrc` after entering the virtual environment will pollute your environment with all the installed packages on your system, so don't do that.

## General code cleanliness

I like [black](https://github.com/psf/black) for automatic code formatting (`pip3 install black` to install and `black ftb` will autoformat `ftb` for you). `ruff` is also very good for linting (`pip3 install ruff` and `ruff ftb --fix`), and `mypy` for type checking (`pip3 install mypy` and `mypy ftb`). This triplet finds SO many bugs, it's rediculous. Makes you realize how much you lose from dynamically typed languages.
