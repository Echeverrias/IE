# Web Scraping App

This is an app to do web scraping on the website 'IE', to get the data of the job offers and store it in a data base.<br><br><br>

You can register in it:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/signup.png" width="500"></div>
<br><p align="center"><i>Figure 1</i></p><br><br>

You can start a web scraping process (the extracted data will be stored in a data base)<br><br>
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
You need to have installed:

- [Python](https://www.python.org/downloads/)
- [VirtualEnv](https://virtualenv.pypa.io/en/latest/index.html)
- [MySQL](http://maven.apache.org/install.html)

You need to create an empty database.

Or if you want to run the proyect with [Docker](https://www.docker.com/get-started) you need to have it installed.

### Running the project
1. Download the base branch from the [IE project](https://github.com/Echeverrias/IE.git), you can [download](https://github.com/Echeverrias/IE/archive/base.zip) it as a zip or clone it with <b>git clone -b base https://github.com/Echeverrias/IE.git</b>
2. You have to set your database. Open the IE/src/ie_django/.env file and set the value of the environment variables.<br>
3. Open the terminal, go to the project root folder and install the virtual environment.<br>
4. Activate the virtual environment.<br>
5. Go to the 'src' folder and install all the requirements with <b>pip install -r requirements.txt</b><br>
6. Execute <b>python manage.py makemigrations</b> to create the migrations.<br>
7. Execute <b>python manage.py migrate</b> to create the tables in the database.<br>
8. Execute <b>python manage.py initdb</b> to initialize language table and locations tables.<br>
9. Execute <b>python manage.py createsuperuser</b> to create a default user with administrator permission.<br>
10. Execute <b>python manage.py collectstatic</b> to move all the static files to the staticfiles folder.<br>
11. The application will start in the url <a href="http://localhost:8000/">http://localhost:8000/</a><br>

### Running the project with Docker
1. Download the base branch from the [IE project](https://github.com/Echeverrias/IE.git), you can [download](https://github.com/Echeverrias/IE/archive/base.zip) it as a zip or clone it with <b>git clone -b base https://github.com/Echeverrias/IE.git</b>
2. Open the terminal, go to the project root folder and execute <b>docker-compose up</b><br>
3. The application will start in the url <a href="http://localhost:8000/">http://localhost:8000/</a><br><br>

The data will be stored in a MySQL database called 'ie' accesible at the 3307 port.<br>
There is an admin user created by default, its username is 'root' and its password is 'root'.


## Running the tests
 Open the terminal, go to the project src folder end execute <b>python manage.py test</b> to run all the tests.
 You also can run a specific test with <b>python manage.py test <<i>app_name</i>.tests><.<i>test_name</i>></b>
 
## Development
The app is developed in [Python](https://www.python.org) and uses the frameworks [Scrapy](https://scrapy.org/) for do the web scrapping of the website and [Django](https://www.djangoproject.com/) for build the web app.<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/sytem_arquitecture.png" width="450"></div>
<br><p align="center"><i>Figure 8</i></p><br><br>

The entity relationship diagram (ERD) defined to shows the relationships of entity sets stored in a database is the following:<br><br>
<div align="center"><img src="https://github.com/Echeverrias/IE/blob/base/screenshots/ER%20diagram.png" width="850"></div>
<br><p align="center"><i>Figure 9</p><br><br>

## Built with
* Python 3.7.5
* MySQL 8.0.2.0
* Django 3.0.5
* Scrapy 2.0.1

# Authors
* Juan Antonio Echeverrías Aranda

# License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/Echeverrias/IE/blob/base/LICENSE.md) file for details
