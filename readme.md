# Friend inviter skill qualification app

### Setup

* Requirements
    * Manually install Flask>=0.11, SQLAlchemy, Flask-Login, Flask-Principal
    * run `python setup.py develop` to autoinstall dependencies
* place a config file (sample config is `config_sample.ini`) as a file named `core.ini` into `~/.config/qfi` directory
* or define `QFI_CONFIG_PATH` environment variable pointing to the directory where config file exists
* optionally define `QFI_CORE_INI` variable to specify another config filename (default is `core.ini`)
* make your desirable configuration changes in that .ini file


### Run
* for console run in debug mode just exec `python friend_inviter.py` from top level directory
* default `admin` password is `derpasswort`


### Autotests
Just run `python setup.py test`

