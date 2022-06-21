# GPS Tracking APP

## Installation

**Instruction for Linux/Unix systems.**

##### 1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

##### 2. Configure the application environment

Copying the file `env` to `.env` and giving proper values to the variables.

##### 3. Run the application:

```bash
FLASK_APP="gps_backend" flask run
```

Now the API should be reachable under `localhost:5000`.
