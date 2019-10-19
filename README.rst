ISalt: Interactive Salt Programming
===================================

ISalt is an IPython style console to facilitate the debugging or even
development of Salt code.

.. image:: https://github.com/mirceaulinic/isalt/blob/master/cover.png

Salt code typically makes use of a number of *dunder* (i.e., _d_ouble 
_under_score) variables such as ``__salt__``, ``__opts__``, ``__grains__``,
``__proxy__``, or ``__pillar__``, etc.,  which give you quick access to various 
resources and features. They also have a different meaning depending on the 
context - for example, ``__opts__`` on the Minion side is a different object 
than ``__opts__`` on the Master side; ``__salt__`` on the Minion side gives you
access to the list of Execution Modules, while ``__salt__`` on the Master side
provides the Runners, and so on.

The main difficulty when working with these variables is that they only make
sense when actually running Salt and having a Master and eventually one or more
Minions running. It often happens that you don't necessarily want to have these 
services running when writing a new function (that use these dunders), or just
want to quickly debug something without pushing code to production.

With ISalt, you can easily get access to these variables, by simply executing
``isalt``, e.g.,

.. code-block:: bash

    $ isalt
    >>> __salt__['test.ping']()
    True
    >>>
    >>> __grains__['osfinger']
    'Ubuntu-18.04'

In other words, ISalt is an enhanced IPython console which gives you access to
the Salt global variables typically used in Salt code.

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

One of the most important details to keep in mind is the difference between 
running the code on the Minion side, versus Master side (where we can further
distinguish between code to be executed as a Runner, vs. Execution Module for
an arbitrary Minion -- for the former you may need to provide the Minion ID
using the ``--minion-id`` CLI argument).

Typically, when you install ISalt where you have a Salt Minion running, it 
should be sufficient to execute just ``$ isalt``.

When you want to use ISalt on the Master side, but to test Execution Modules,
you can run ``$ isalt --on-master``.

When you're looking into evaluating Runner code, you can only do this one the
Master side, therefore, you'd need to start the console as ``$ isalt 
--master``.

You can check the complete list of CLI optional arguments by 

.. code-block:: bash

    $ isalt -h
    usage: isalt [-h] [--saltenv SALTENV] [--pillarenv PILLARENV] [-c CFG_FILE]
                 [-e CFG_FILE_ENV_VAR] [--minion-cfg MINION_CFG_FILE]
                 [--master-cfg MASTER_CFG_FILE] [--minion] [--master]
                 [--minion-id MINION_ID] [--on-minion] [--on-master]

    ISalt console

    optional arguments:
      -h, --help            show this help message and exit
      --saltenv SALTENV     Salt environment name.
      --pillarenv PILLARENV
                            The Salt environment name to compile the Pillar from.
      -c CFG_FILE, --cfg-file CFG_FILE
                            The absolute path to the ISalt config file.
      -e CFG_FILE_ENV_VAR, --env-var CFG_FILE_ENV_VAR
                            The name of the environment variable pointing to the
                            ISalt config file.
      --minion-cfg MINION_CFG_FILE
                            The absolute path to the Minion config file.
      --master-cfg MASTER_CFG_FILE
                            The absolute path to the Master config file.
      --minion              Prepare the Salt dunders for the Minion side.
      --master              Prepare the Salt dunders for the Master side.
      --minion-id MINION_ID
                            The Minion ID to compile the Salt dunders for. This
                            argument is optional, however it may fail when ISalt
                            is not able to determine the Minion ID, or take it
                            from the environment variable, etc.
      --on-minion           Whether should compile the dunders for the Minion
                            side, starting the ISalt console on the Minion
                            machine. The main difference is that the Pillar and
                            Grains are compiled locally, while when using --on-
                            master, it's using the local cached data.
      --on-master           Whether should compile the dunders for the Minion
                            side, starting the ISalt console on the Master
                            machine. This option is ignored when used in
                            conjunction with --master.
