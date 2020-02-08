NOTE: 
Always specify gate time, ex `b.gate('X', ['1'], time = 10)`, where the `b` is a builder instance, and the time is the middle temporal of the gate's execution.
Plus, always correct the builder class timing at the end:
```
b.times = {'1': 20}
```

Installation
------------


Overview and usage
==================

Installation
------------
This package needs to be installed alongside quantumsim, which can be found at https://github.com/brianzi/quantumsim.

The following set of commands will install both packages on linux (beginning in your favourite directory to store git repos):

```
git clone https://github.com/quantumsim/quantumsim
git clone https://github.com/quantumsim/qsoverlay
cd quantumsim
pip install -e .
cd ../qsoverlay
pip install -e .
```


License
-------

This work is distributed under the GNU GPLv3. See LICENSE.txt.
(c) 2017 Tom O'Brien
