# Web Scrapping App

This is an app to do web scrapping on the site web 'IE', to get the data of the job offers and store it in a data base.<br><br><br>

You can register in it:<br><br>
<img align="center" src="https://github.com/Echeverrias/IE/blob/base/screenshots/signup.png" width="500">
<br><p align="center">*Figure 1*</p><br><br>

You can start a web scrapping process (the extracted data will be stored in a data base)<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/run_crawler.png" width="500"></div>
<br><p align="center">*Figure 2*</p>  <br/><br/>

You can access to the stored data through Django admin panel:<br><br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/admin_panel1.png" width="500">
<br>*Figure 3*  <br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/panel_admin2.png" width="500">
<br>*Figure 4*  <br>

You can make searches ,using filters, of the available offer jobs:<br><br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/offers_list.png" width="500">
<br>*Figure 5*  <br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/offers_detail.png" width="500">
<br>*Figure 6*  <br><br>

## Getting Started
### Prerequisites
You need to install:

- [Python](https://www.python.org/downloads/):
- [VirtualEnv](https://virtualenv.pypa.io/en/latest/index.html)
- [MySQL](http://maven.apache.org/install.html): You'll need to create an empty database.

### Run the project
1. Download the [IE](xxx) project. You can download it as a zip or clone it.
2. Yo have to set your database. Open de src/ie_django/settings.py file and configure the variable 'DATABASES'<br><br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/db_settings.png" width="500"><br>
<br>*Figure 7*  <br><br>
3. Open the terminal, go to the root folder project and install the virtual environmnet.
4. Activate the virtual environment.
5. Go to the 'src' folder and install all the requirements with **`pip install -r requirements.txt`**
6. Execute **`python manage.py makemigrations`** to create the migrations.
7. Execute **`python manage.py migrate`** to create the tables in the database.
8. Execute **`python manage.py initdb`** to initialize language table and locations tables.
9. Execute **`python manage.py createsuperuser`** to create a default user with administrator permission.
10. Execute **`python manage.py runserver`** to run the app.
11. The application starts in the url [http://localhost:8080/](http://localhost:8080/)


## Development
The app is developed in [Python](https://www.python.org) and uses the frameworks [Scrapy](https://scrapy.org/) for do the web scrapping of the site web and [Django](https://www.djangoproject.com/) for build the web app.<br><br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/sytem_arquitecture.png" width="500"><br>
<br>*Figure 8* <br><br>

The entity relationship diagram (ERD) defined to shows the relationships of entity sets stored in a database is the following:<br><br>
<img src="https://github.com/Echeverrias/IE/blob/base/screenshots/ER%20diagram.png" width="500"><br>
<br>*Figure 9*<br><br>

### Software versions
Python 3.7.5
MySQL 8.0.2.0
Django 3.0.5
Scrapy 2.0.1
