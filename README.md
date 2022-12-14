# 20221215-pyATS-Testscripts
Demo code for creating a pyATS Testscript TTTT - December 2022

## Usage

### Installation

Create a Python 3 virtual environment and activate it.
_All testing was done using Python 3.8, but Python 3.7+ should work._

```
python3 -m venv pyats-venv
source pyats-venv/bin/activate
```

With the virtual environment activated, install all the dependencies from requirements.txt

```
pip install -r requirements.txt
```

Lastly, you will need to create a `.env` file in the project root directory with two environment variables for the device login credentials (username and password). For testing purposes, I used the variable names `CML_SSH_USER` and `CML_SSH_PASS` since I used CML to virtually simulate my test network.

```
CML_SSH_USER=<your username>
CML_SSH_PASS=<your password>
```

If you would like to use different variable names, please make sure to update the appropriate script files. More specifically, the pyATS testbed YAML file (`cml_testbed.yaml`). You'll need to make sure the testbed looks for the new environment variable names.

## Contribution

As most of this repository contains introductory demo code, there are definitely ways to improve the code (i.e. error handling, improving modularity, etc.). Please feel free to make a pull request with whatever changes you think would help improve the code!

## Feedback

If you have any questions or would like to provide further feedback, please feel free to message me or open an issue. Thanks!