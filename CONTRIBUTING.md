# Contributing

Welcome contributors! 

Thank you for taking the time to contribute to this project. Your help is highly appreciated.

The rules are pretty simple:
1. Use Discussions for major changes. 
2. This repo uses `black` & `flake8` for style and formatting via `pre-commit` hooks. Kindly make sure you run it before submitting a PR. Refer [Pull Request Process](#pull-request-process)

## Pull Request Process

1. Fork and clone the repo. 
2. Install [pre-commit](https://pre-commit.com/) and setup hooks via the following steps. 

   ```
   $ pip install pre-commit
   $ pre-commit install
   ```
   Now pre-commit will run on every git commit. Alternatively, you could just run `pre-commit run --all-files` after you're done. Please ensure you've run the pre-commit before submitting the PR.
3. Submit PR to `dev` branch.
