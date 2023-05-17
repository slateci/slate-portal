
# Static Code Analysis

The GitHub workflows will automatically run the `black` and `isort` static analysis tools against any pull request as defined in `./.github/workflows/pr-python.yml`.

## Setting up your Python interpreter

It is possible to run these analyses on your own machine by first creating a Python interpreter using one of the two methods described below.
* The local development `./resources/docker/environment.yml` Conda file:

  ```shell
  $ conda env create --file ./resources/docker/environment.yml
  $ conda activate slate-portal
  (slate-portal) $
  ```

* The production `./resources/docker/requirements.txt` Pip file:
  
  ```shell
  $ python -m venv /path/to/new/virtual/environment
  $ source /path/to/new/virtual/environment/bin/activate
  (environment) $ pip install black isort
  (environment) $
   ```

## Running `black`

From the [black documentation](https://black.readthedocs.io/en/stable/), run a check:

```shell
black --check --verbose ./portal
```

or enact changes against the source files:

```shell
black --verbose ./portal
```

## Running `isort`

From the [isort documentation](https://pycqa.github.io/isort/), report on a directory:

```shell
isort --check-only --diff ./portal
```

or enact changes against the source files:

```shell
isort ./portal
```
