# Biota brick

This software brick is the core library to manage Gecovery knowledge databases. <br />

The purpose of Biota is to collect biological data from official open biological databases to create a reference database for GWS bricks. <br />

This module has been developed in python 3.8.2.  

### Dependencies:

```peewee``` version 3.13.3 <br />
```starlette``` version 0.13.4 <br />
```uvicorn``` version 0.11.5 <br />
```aiofiles``` version 0.5.0 <br />
```jinja2``` version 2.11.2 <br />
```requests``` version 2.24.0 <br />
```itsdangerous``` version 1.1.0 <br />
```awesome-slugify``` version 1.6.5 <br />
```pronto``` version 2.1.0 <br />
```sphinx``` version 3.1.2 <br />
```sphinx-rtd-theme``` version 0.5.0 <br />
```numpy``` <br />
```ujson``` <br />

### Installation:

#### Mac and Linux
Create a virtual environment in biota-py root and load required package:
```bash env.sh```

#### Windows 

Create a virtual environment in biota-py root: 
```python -m virtualenv .venv```

Activate the virtual environment:
```source .\.venv\bin\activate```

Install required packages:
```pip -m install -r requirements.txt```

### Tests 

Before to launch the loading of the complete database make sure that all tests of biota are OK with:

```python manage.py --test <module name>```

### Biota database loading 
Launch complete database loading 

```bash createdb.sh``` on mac and linux

```createdb.sh``` on windows

### Prequesities
Before launching anything with Biota, ensure that you have downloaded all the necessary data

### Documentation:
You can find documentation about prism and helper package of biota on the following brick in the ./docs/ folder

# License

This software is the exclusive property of Gencovery SAS. 
The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.