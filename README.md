# Getting started

0. Install the dependencies with `apt install libdbus-1-dev libdbus-glib-1-dev`
1. First set up your virtualenv (ideally under the conventional "vendor" directory) with `virtualenv vendor`
2. Activate the virtualenvironment and install the pip requirements with `pip install -r requirements.txt`
3. Create a secrets.yaml in the format of the secrets.yaml.template. This should hold the connection string to whatever backend you choose to use
4. To create your database tables, run `init_db.py`
5. If you're using a new backend, you can bootstrap some exercises into it by running the `bootstrap_exercises.py`.
