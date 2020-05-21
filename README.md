# Web Scrapping App

This is an app to do web scrapping on the site web 'IE', to get the data of the job offers and store it in a data base.<br><br><br>

You can register in it:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/signup.png" width="500"></div>
<br><p align="center"><i>Figure 1</i></p><br><br>

You can start a web scrapping process (the extracted data will be stored in a data base)<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/run_crawler.png" width="500"></div>
<br><p align="center"><i>Figure 2</i></p><br/><br/>

You can access to the stored data through Django admin panel:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/admin_panel1.png" width="500"></div>
<br><p align="center"><i>Figure 3</i></p><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/panel_admin2.png" width="500"></div>
<br><p align="center"><i>Figure 4</i></p><br>

You can make searches ,using filters, of the available offer jobs:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/offers_list.png" width="500"></div>
<br><p align="center"><i>Figure 5</i></p><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/offers_detail.png" width="500"></div>
<br><p align="center"><i>Figure 6</i></p><br><br>

## Getting Started
### Prerequisites
You need to install:

- [Python](https://www.python.org/downloads/)
- [VirtualEnv](https://virtualenv.pypa.io/en/latest/index.html)
- [MySQL](http://maven.apache.org/install.html)

You'll need to create an empty database.

### Run the project
1. Download the [IE](xxx) project. You can download it as a zip or clone it.
2. Yo have to set your database. Open de src/ie_django/settings.py file and configure the variable 'DATABASES'<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/db_settings.png" width="350"></div>
<br><p align="center"><i>Figure 7</i></p><br>
3. Open the terminal, go to the root folder project and install the virtual environmnet.<br>
4. Activate the virtual environment.<br>
5. Go to the 'src' folder and install all the requirements with <b>pip install -r requirements.txt</b><br>
6. Execute <b>python manage.py makemigrations</b> to create the migrations.<br>
7. Execute <b>python manage.py migrate</b> to create the tables in the database.<br>
8. Execute <b>python manage.py initdb</b> to initialize language table and locations tables.<br>
9. Execute <b>python manage.py createsuperuser</b> to create a default user with administrator permission.<br>
10. Execute <b>python manage.py runserver</b> to run the app.<br>
11. The application starts in the url <a href="http://localhost:8080/">http://localhost:8080/</a><br>


## Development
The app is developed in [Python](https://www.python.org) and uses the frameworks [Scrapy](https://scrapy.org/) for do the web scrapping of the site web and [Django](https://www.djangoproject.com/) for build the web app.<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/sytem_arquitecture.png" width="450"></div>
<br><p align="center"><i>Figure 8</i></p><br><br>

The entity relationship diagram (ERD) defined to shows the relationships of entity sets stored in a database is the following:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/ER%20diagram.png" width="850"></div>
<br><p align="center"><i>Figure 9*</p><br><br>

### Software versions
* Python 3.7.5
* MySQL 8.0.2.0
* Django 3.0.5
* Scrapy 2.0.1
