"""
To prevent the pymysql error:  django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
https://stackoverflow.com/questions/55657752/django-installing-mysqlclient-error-mysqlclient-1-3-13-or-newer-is-required

But there is another error: AttributeError: 'str' object has no attribute 'decode'
The error is specified in: http://programmersought.com/article/19241784782/;jsessionid=ECBAF2C83EFD914CBEE2E811C1451AB4

To fix this error you will have to do some change in the operators.py file ubicated in the path:
your_project/lib/python3.x/site-packages/django/db/backends/mysql/operations.py

You have to change the line "query = query.decode(errors='replace')" from the last_executed_query function for the line
"query = query.encode(errors='replace')"

The reason is Python3 Str only has the encode method
"""
import pymysql
pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()

import django
django.setup()
from core.management.commands.initdb import initialize_database
initialize_database()