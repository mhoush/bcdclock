# Python 3 BCD (binary-coded decimal) Clock

This is a [BCD clock](https://en.wikipedia.org/wiki/Binary_clock) using [Python](https://www.python.org/) 3 and the [Simple DirectMedia Layer (SDL)](https://www.libsdl.org/) [python bindings](https://pysdl2.readthedocs.io/en/rel_0_9_6/).

It wasn't created for any specific purpose, just an exercise in learning some SDL usage with Python 3.

![BCD Clock Image](http://jaeger.morpheus.net/images/bcdclock/bcdclock.png)

It will display the current time in either 24- or 12-hour mode and local time or GMT. Both BCD background panels and the decimal time are displayed. Any TTF or OTF fonts found in the 'fonts' folder will be used (some free examples from dafont.com are included). It supports the following key/button inputs:

Key | Result
--- | ------
Mouse Button | Prints decimal time to the console
Space | Changes panel color (random)
h | Toggles between 24- and 12-hour mode
l | Toggles between local timezone and GMT
t | Cycles through available fonts
