# django-gym
Package             Version
------------------- -------
asgiref             3.12.1
Django              6.0.7
django-filter       26.1
djangorestframework 3.17.1
Markdown            3.10.2
pip                 25.1.1
sqlparse            0.5.5


first commands:

python -m venv .venv
source .venv/bin/activate

pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support

django-admin startproject config .

for creating migrations
python manage.py makemigrations accounts