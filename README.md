EVE Online Python API
=====================
Python interface for EVE Online API.

Installation
------------

    pip install eveapi


Example
-------

```python
import eveapi

api = eveapi.EVEAPIConnection()
auth = api.auth(keyID=API_KEY_ID, vCode=API_VER_CODE)

for character in auth.account.Characters():
    print character.name
```


For more examples see tests/api.py.


Testing
-------

    make test  (hits EVE api servers)
