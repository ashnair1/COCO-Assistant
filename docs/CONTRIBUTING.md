<h1> Contributing </h1>

Welcome contributors! 

Thank you for taking the time to contribute to this project. Your help is highly appreciated.

The rules are pretty simple:

-   Use [Discussions](https://github.com/ashnair1/COCO-Assistant/discussions) for proposing major changes. 
-   This repo uses `black` & `flake8` for style and formatting via `pre-commit` hooks. Kindly make sure you run it before submitting a PR. Refer [Pull Request Process](#pull-request-process) below.

## Pull Request Process

1.  Fork and clone the repo. 
2.  Install poetry as specified [here](https://python-poetry.org/docs/#installation). and setup the dev environment as follows:

        poetry install -E dev -E doc -E test

    Running `poetry shell` will now put you in the dev environment. 
    
3. Setup [pre-commit](https://pre-commit.com/) hooks by running `pre-commit install` in the dev environment. Now pre-commit will run on every git commit. Alternatively, you could just run `pre-commit run --all-files` after you're done. 

3.  Confirm tests are passing by running `tox`.
4.  Submit PR.
