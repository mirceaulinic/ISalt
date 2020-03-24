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

You can configure various bits of data or conditionals using one or more of the 
following options, with precedence in this order: ISalt configuration file, 
environment variables, and CLI arguments.

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
                 [--proxy-cfg PROXY_CFG_FILE] [--master-cfg MASTER_CFG_FILE]
                 [--minion] [--proxytype PROXYTYPE] [--proxy] [--sproxy]
                 [--master] [--local] [--minion-id MINION_ID] [--on-master]

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
      --proxy-cfg PROXY_CFG_FILE
                            The absolute path to the Proxy Minion config file.
      --master-cfg MASTER_CFG_FILE
                            The absolute path to the Master config file.
      --minion              Prepare the Salt dunders for the Minion.
      --proxy               Prepare the Salt dunders for the Proxy Minion.
      --sproxy              Prepare the Salt dunders for the salt-sproxy (Master
                            side).
      --master              Prepare the Salt dunders for the Master.
      --local               Override the Minion config and use the local client.
                            This option loads the file roots config from the
                            Master file.
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

Usage Examples
^^^^^^^^^^^^^^

Using ISalt on the Master
+++++++++++++++++++++++++

Start with ``isalt --master``. Remember that the ``__salt__`` dunder currently 
maps to the Runner functions, and not to the execution modules.

.. code-block:: bash

  $ isalt --master

  In [1]: # execute the ``test.sleep`` Runner:

  In [2]: # https://docs.saltstack.com/en/latest/ref/runners/all/salt.runners.test.html#module-salt.runners.test

  In [3]: __salt__['test.sleep'](1)
  1
  Out[3]: True


Using ISalt on the Master, loading the (Proxy) Minion dunders
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this mode, you need to specify the Minion ID to use and collect and compile
data for (otherwise it'll use local machine's hostname):

.. code-block:: bash

    $ isalt --on-master --minion-id jerry

.. note::

    You can equally specify the Minion ID in the proxy/minion configuration 
    file, from ``--minion-cfg`` or ``--proxy-cfg`` options.

For Proxy Minions, you have to pass the ``--proxy`` CLI argument, e.g.,

.. code-block:: bash

    $ isalt --on-master --minion-id edge-router --proxy

For Proxy Minions, in order to load the ``__salt__`` modules correctly, you may
have to provide the ``proxytype`` as well into the Proxy configuration file (by 
default at ``/etc/salt/proxy``, or a different path set using the 
``--proxy-cfg`` arg) - or using the ``--proxytype`` CLI argument, e.g.,

``/etc/salt/proxy``

.. code-block:: yaml

    proxy:
      proxytype: napalm

And execute as ``isalt --on-master --proxy --minion-id jerry``.

Or directly as ``isalt --on-master --proxytype napalm --minion-id jerry``.

Using ISalt on the (Proxy) Minion
+++++++++++++++++++++++++++++++++

This is the default ISalt mode, and you no longer have to provide the Minion 
ID, as it's collected from local machine, unless you want to use a specific 
one. As always, you can have the Minion ID in the Proxy / Minion configuration 
file, the ``ISALT_MINION_ID`` environment variable, or the ISalt configuration
file (as the ``minion_id`` option).

Example:

.. code-block:: bash

    $ echo $ISALT_MINION_ID
    jerry
    $ isalt

    In [1]: __opts__['id']
    Out[1]: 'jerry'

.. note::

    The local Proxy / Minion key must be accepted by the Master. To avoid 
    connecting to the Master, you can use the ``--local`` argument to start the
    Minion in `Masterless 
    <https://docs.saltstack.com/en/latest/topics/tutorials/quickstart.html>`__
    mode - you will however need to make sure that you point to the file (and
    pillar) roots you need as those won't be pulled from the Master.

    One good way to deal with this is pointing the ``file_roots`` option to the
    cache directory of the production Minion. For example, you have a Minion
    that is pulling the production files from the Master, and caching them 
    under ``/var/cache/salt/minion/files/base`` (whatever would be your 
    filesystem backend). Now, to use these files when starting ISalt in local 
    mode, you can reference that dir as:

    ``/etc/salt/minion`` (excerpt)

    .. code-block:: yaml

        file_roots:
            base:
              - /var/cache/salt/minion/files/base

    Now, starting with ``isalt --local``, you still load your modules, states,
    and other files without connecting to the Master.

Using ISalt in conjunction with Salt Super Proxy (Master side)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. note::

    This option requires salt-sproxy to be installed in the same environment as
    ISalt: ``pip install salt-sproxy``. For simplicity, you can, for example,
    install as: ``pip install isalt[sproxy]``.

Usage example:

.. code-block:: bash

    $ isalt --sproxy

In this interactive console, you have access to the usual Salt Master dunders, 
as well as the salt-sproxy features. As a shortcut, you have access to the 
salt-sproxy core function, through the ``sproxy`` global variable:

.. code-block:: bash

    >>> sproxy
    <function execute at 0x7fd394075510>
    >>> sproxy('*', preview_target=True)
    ['router1',
     'router2']

In a similar way, this facilitates the execution of any Salt function through
salt-sproxy, e.g.,

.. code-block:: bash

    >>> sproxy('router1', function='test.ping', static=True)
    {'router1': True}
    >>>

.. tip::

    For best results using salt-sproxy, it is recommended to pass the 
    ``static=True`` argument.

You can also get into the *sproxy* mode by default, by setting the value 
``role: sproxy`` into the ISalt configuration file (see also the next 
paragraph).

.. important::

    Check also the `salt-sproxy documentation 
    <https://salt-sproxy.readthedocs.io/en/latest/>`__ for more usage 
    instructions and examples.

ISalt configuration file
^^^^^^^^^^^^^^^^^^^^^^^^

Every of the options presented above are available through the ISalt 
configuration file, by default ``/etc/salt/isalt``. To read the file from 
a specific path, use the ``-c`` / ``--cfg-file`` args, e.g.,

.. code-block:: bash

    $ isalt -c /path/to/isalt/config/file

Or, alternative, using the ``ISALT_CFG_FILE`` environment variable, e.g.,

.. code-block:: bash

    $ echo $ISALT_CFG_FILE
    /path/to/isalt/config/file
    $ isalt

Even more, if you want to read the path to the config file from a different
environment variable, use the ``-e`` / ``--env-var`` arg:

.. code-block:: bash

    $ echo $ALTERNATIVE_ISALT_CFG_FILE
    /path/to/another/isalt/config/file
    $ isalt -e ALTERNATIVE_ISALT_CFG_FILE

ISalt configuration file example
++++++++++++++++++++++++++++++++

.. code-block:: yaml

    on_master: true
    proxytype: dummy
    proxy_cfg: /path/to/proxy/config
    minion_cfg: /path/to/minion/config
    master_cfg: /path/to/master/config

With the configuration file above, you can simplify the CLI usage, e.g., from 
``isalt --on-master --proxy-cfg /path/to/proxy/config --proxytype dummy 
--minion-id jerry`` to just ``isalt --minion-id jerry``, etc.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

``ISALT_CFG_FILE``
    Absolute path to the ISalt configuration file.

``ISALT_ROLE``
    The Salt system role. Choose between: ``master``, ``minion``, or ``proxy``.

``ISALT_ON_MASTER``
    If you're running ISalt on the Master.

``ISALT_MINION_ID``
    The Minion ID to use.

``ISALT_PROXYTYPE``
    The Proxy Minion module name to use.

``ISALT_MASTER_CONFIG``
    Absolute path to the Master configuration file.

``ISALT_MINION_CONFIG``
    Absolute path to the Minion configuration file.

``ISALT_PROXY_MINION_CONFIG``
    Absolute path to the Proxy Minion configuration file.

``ISALT_USE_CACHED_PILLAR``
    When starting in Proxy / Minion mode, on the Master: whether to use the
    cached Pillars that may be already available for the specified Minion,
    or compile fresh data.
