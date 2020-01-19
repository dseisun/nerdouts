# Getting started

1. Install the dependencies with `apt install libdbus-1-dev libdbus-glib-1-dev`
2. First set up your virtualenv (ideally under the conventional "vendor" directory) with `virtualenv vendor`
3. Activate the virtualenvironment and install the pip requirements with `pip install -r requirements.txt`
4. Create a `secrets.yaml` file in the format of the secrets.yaml.template in the top level directory. This should hold the connection string to whatever backend you choose to use
5. To create your database tables, run `init_db.py`
6. If you're using a new backend, you can bootstrap some exercises into it by running the `bootstrap_exercises.py`.
7. Look at config.json and tweak as desired to setup your workout