# AUA Smart Course Planner

# Application setup

```bash
# Clone the repository
git clone git@github.com:iamdianaaa/AUA-Course-Planner.git
```

## Installing requirements locally

It is suggested to create a virtual environment firstly:

```bash
python -m venv venv
.\venv\Scripts\activate # on Windows
source venv/bin/activate # on Ubuntu
```

Then install the requirements specified in requirements.txt file:

```bash
pip install -r requirements.txt
```

## Running the application locally

```bash
# on Windows
set FLASK_APP=main.py 
set FLASK_ENV=development
flask run

# on Ubuntu
export FLASK_APP=main.py 
export FLASK_ENV=development
flask run
```