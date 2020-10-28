# CS235Flix-SQL Web Application

## Description

A Web application that demonstrates use of Python's Flask framework. The application makes use of libraries such as the Jinja templating library and WTForms. Architectural design patterns and principles including Repository, Dependency Inversion and Single Responsibility have been used to design the application. The application uses Flask Blueprints to maintain a separation of concerns between application functions. Testing includes unit and end-to-end testing using the pytest tool. 

## Cloning the Repository

Do the following instructions using Git Bash shell:
* Go to your desired location/folder on your computer, for example:
```shell script
$ cd Documents/CompsciPart2/Compsci235/A3
```
* Clone the GitHub repository:
```shell script
$ git init
$ git clone https://github.com/NeoXB/CS235Flix-SQL.git
```
**For the next set of instructions, please switch to and use the Command Prompt window!**

## Installation

**Installation via requirements.txt**

Go to the location/folder that you chose before, which now contains the *CS235Flix-SQL* directory (i.e. the directory that has the movie_app\ and tests\ directories plus other files), and access the *CS235Flix-SQL* directory. For example:
```shell
C:\Users\neoxb> cd Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL
```

Then, perform the following:
```shell
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> py -3 -m venv venv
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> venv\Scripts\activate
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> pip install -r requirements.txt
```
When using PyCharm, set the virtual environment using 'File'->'Settings' and select 'Project:CS235Flix-SQL' from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add'. Click the 'Existing environment' radio button to select the virtual environment.

## Execution

**Running the application**

From the *CS235Flix-SQL* directory, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> flask run
```` 

## Configuration

The *CS235Flix-SQL/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.
* `SQLALCHEMY_DATABASE_URI`: Database URI, can be memory- or file-based.
* `REPOSITORY`: Repository type, can be 'memory' or 'database'.

## Testing

Testing requires that file *CS235Flix-SQL/tests/conftest.py* be edited to set the value of `TEST_DATA_PATH`. You should set this to the absolute path of the *CS235Flix-SQL/tests/data* directory. 

E.g. 

`TEST_DATA_PATH = os.path.join('C:', os.sep, 'Users', 'neoxb', 'Documents', 'CompsciPart2', 'Compsci235', 'A3', 'CS235Flix-SQL', 'tests', 'data')`

assigns TEST_DATA_PATH with the following value (the use of os.path.join and os.sep ensures use of the correct platform path separator):

`C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL\tests\data`

You can then run tests from within PyCharm.

**Running the tests via the Command Prompt window**

From the *CS235Flix-SQL* directory, and within the activated virtual environment (see *venv\Scripts\activate* in the **Installation** guide):
```shell
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> python -m pytest
```

## Note
If when you encounter any *Module Not Found* errors, you may need to set PYTHONPATH before running or testing. If required, PYTHONPATH should be set to the full path of the directory that contains \movie_app and \tests (i.e. CS235Flix-SQL), for example:
```shell
C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL> set PYTHONPATH=C:\Users\neoxb\Documents\CompsciPart2\Compsci235\A3\CS235Flix-SQL
```
