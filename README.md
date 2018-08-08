pypy-um
---
A [Universal Machine](http://www.boundvariable.org/) in pypy.

*NOTE*: The `spoilers` branch ... contains spoilers.

Building
---
Note: pypy is optional, but *highly* recommended.
```
python pypy/rpython/bin/rpython --opt=jit interp.py
```

Usage
---
```
./interp-c <um application>
```

