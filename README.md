# README #

This README would normally document whatever steps are necessary to get your 
application up and running.

Report and presentation:
* Report.pdf
* Presentation.pptx

## Dependencies ##

Located in the packages folder. Extract the folders from the zip, except 'Crypto' because that doesn't seem to work unless you install it.

### Run ###

```bash
cd /path/to/project
export PYTHONPATH=./:./packages
python2 ./app/Server.py
```

If you're on Windows, just run the .bat file.

Visit ```localhost:10101``` afterwards and the web page should be up. This may take a while to load depending on your connection to CDNJS.

### Test ###

Server must be up for this to work.

```bash
cd /path/to/project
export PYTHONPATH=./:./packages

# IF YOU HAVE PYTEST
pytest test

# IF NOT
python2 ./packages/pytest/pytest.py test
```




## Contacts ##

Jerry Fan - jfan082@aucklanduni.ac.nz
