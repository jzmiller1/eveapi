EVE Online Python API v.2.0
===========================
Python interface for EVE Online API.

Features
--------
* Python3 support (YAY)
* Saner API
* Good documentation
* Good test coverage

Installation
------------

    pip install eveapi


Example
-------

```python
import eveapi2

connection = eveapi2.Connect()
auth = connection.auth(key_id=API_KEY_ID, ver_code=API_VER_CODE)

for character in auth.account.Characters():
    print character.name
```


For more examples see tests/api.py.


Testing
-------

    make test
