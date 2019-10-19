ISalt: Interactive Salt Programming
===================================

ISalt is an IPython style console to facilitate the debugging or even
development of Salt code.

.. code-block::
     __       _______.     ___       __      .___________.
    |  |     /       |    /   \     |  |     |           |
    |  |    |   (----`   /  ^  \    |  |     `---|  |----`
    |  |     \   \      /  /_\  \   |  |         |  |     
    |  | .----)   |    /  _____  \  |  `----.    |  |     
    |__| |_______/    /__/     \__\ |_______|    |__|     

Salt code typically makes use of a number of *dunder* (i.e., _d_ouble 
_under_score) variables such as ``__salt__``, ``__opts__``, ``__grains__``,
``__proxy__``, or ``__pillar__``, etc.,  which give you quick access to various 
resources and features. They also have a different meaning depending on the 
context - for example, ``__opts__`` on the Minion side is a different object 
than ``__opts__`` on the Master side; ``__salt__`` on the Minion side gives you
access to the list of Execution Modules, while ``__salt__`` on the Master side
provides the Runners, and so on.

With ISalt, you can easily get access to this, by simply executing ``isalt``, 
e.g.,

.. code-block:: bash

    $ isalt
    >>> __salt__['test.ping']()
    True
    >>>
    >>> __grains__['osfinger']
    'Ubuntu-18.04'

In other words, ISalt is an enhanced IPython console which gives you access to
the Salt global variables you usually make use in your code.

Install
-------

ISalt is distributed via PyPI, and you can install it by executing:

.. code-block:: bash

    $ pip install isalt

Dependencies:

- `salt <https://pypi.org/project/salt/>`__
- `IPython <https://pypi.org/project/IPython/>`__

No specific version for either of these packages, so it doesn't mess up with 
your environment. It should normally work well with any version.

Usage
-----


