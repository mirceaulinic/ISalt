# -*- coding: utf-8 -*-
# Copyright 2019 Mircea Ulinic. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
'''
The ISalt script functions.
'''
import os
import sys
import argparse

import salt
import salt.config
import salt.loader
import salt.version
import salt.utils.master
import salt.modules.pillar

import IPython
import traitlets.config.loader

BANNER = '''\
 __       _______.     ___       __      .___________.
|  |     /       |    /   \     |  |     |           |
|  |    |   (----`   /  ^  \    |  |     `---|  |----`
|  |     \   \      /  /_\  \   |  |         |  |     
|  | .----)   |    /  _____  \  |  `----.    |  |     
|__| |_______/    /__/     \__\ |_______|    |__|     


'''


class ISaltError(Exception):
    pass


def main():
    '''
    The entry point to the ISalt console.

    cfg_file
        Absolute path to the ISalt config file to read.

    cfg_file_env_var: ``ISALT_CFG_FILE``
        The environment variable containing the path to the ISalt config file.

    saltenv: ``base``
        The name of the Salt environment.

    pillarenv: ``base``
        The environment name to render the Pillar from.
    '''
    parser = argparse.ArgumentParser(description='ISalt console')
    parser.add_argument(
        '--saltenv',
        default='base',
        help='Salt environment name.'
    )
    parser.add_argument(
        '--pillarenv',
        default='base',
        help='The Salt environment name to compile the Pillar from.'
    )
    parser.add_argument(
        '-c', '--cfg-file',
        default='/etc/salt/isalt',
        dest='cfg_file',
        help='The absolute path to the ISalt config file.'
    )
    parser.add_argument(
        '-e', '--env-var',
        default='ISALT_CFG_FILE',
        dest='cfg_file_env_var',
        help='The name of the environment variable pointing to the ISalt config file.'
    )
    parser.add_argument(
        '--minion-cfg',
        default='/etc/salt/minion',
        dest='minion_cfg_file',
        help='The absolute path to the Minion config file.'
    )
    parser.add_argument(
        '--master-cfg',
        default='/etc/salt/master',
        dest='master_cfg_file',
        help='The absolute path to the Master config file.'
    )
    parser.add_argument(
        '--minion',
        action='store_true',
        help='Prepare the Salt dunders for the Minion side.'
    )
    parser.add_argument(
        '--master',
        action='store_true',
        help='Prepare the Salt dunders for the Master side.'
    )
    parser.add_argument(
        '--minion-id',
        dest='minion_id',
        help=(
            'The Minion ID to compile the Salt dunders for.\n'
            'This argument is optional, however it may fail when ISalt is not '
            'able to determine the Minion ID, or take it from the environment '
            'variable, etc.'
        )
    )
    parser.add_argument(
        '--on-minion',
        action='store_true',
        help=(
            'Whether should compile the dunders for the Minion side, starting '
            'the ISalt console on the Minion machine.\n'
            'The main difference is that the Pillar and Grains are compiled '
            'locally, while when using --on-master, it\'s using the local '
            'cached data.'
        )
    )
    parser.add_argument(
        '--on-master',
        action='store_true',
        help=(
            'Whether should compile the dunders for the Minion side, starting '
            'the ISalt console on the Master machine.\n'
            'This option is ignored when used in conjunction with --master.'
        )
    )
    args = parser.parse_args()

    isalt_cfg = salt.config.load_config(args.cfg_file, args.cfg_file_env_var)
    role = os.environ.get('ISALT_ROLE', isalt_cfg.get('role', 'minion'))
    if args.minion:
        role = 'minion'
    elif args.master:
        role = 'master'
    on_minion = args.on_minion or bool(os.environ.get(
        'ISALT_ON_MINION',
        isalt_cfg.get('on_minion', 'True')
    ))
    minion_id = None
    if role == 'minion':
        cfg_file = args.minion_cfg_file or os.environ.get(
            'ISALT_MINION_CONFIG',
            isalt_cfg.get(
                'minion_config',
                salt.config.DEFAULT_MINION_OPTS['conf_file'],
            )
        )
        __opts__ = salt.config.minion_config(cfg_file)
        minion_id = args.minion_id or __opts__.get('id',
            os.environ.get('ISALT_MINION_ID', isalt_cfg.get('minion_id'))
        )
        if not minion_id:
            raise ISaltError('Unable to determine a Minion ID')
        __opts__['id'] = minion_id
    elif role == 'master':
        cfg_file = args.master_cfg_file or os.environ.get(
            'ISALT_MASTER_CONFIG',
            isalt_cfg.get(
                'master_config',
                salt.config.DEFAULT_MASTER_OPTS['conf_file'],
            )
        )
        __opts__ = salt.config.master_config(cfg_file)
    __opts__['saltenv'] = args.saltenv
    __opts__['pillarenv'] = args.pillarenv

    __proxy__ = None
    __grains__ = None
    __pillar__ = None
    __utils__ = salt.loader.utils(__opts__)
    if role == 'minion':
        __proxy__ = salt.loader.proxy(__opts__, utils=__utils__)
        __salt__ = salt.loader.minion_mods(
            __opts__,
            utils=__utils__,
            proxy=__proxy__,
        )
        if args.on_master:
            use_cached_pillar = bool(
                os.environ.get(
                    'ISALT_USE_CACHED_PILLAR',
                    isalt_cfg.get('use_cached_pillar', True)
                )
            )
            pillar_util = salt.utils.master.MasterPillarUtil(
                minion_id,
                'glob',
                use_cached_grains=True,
                grains_fallback=False,
                use_cached_pillar=use_cached_pillar,
                pillar_fallback=True,
                opts=__opts__,
            )
            __grains__ = pillar_util.get_minion_grains()
            __pillar__ = pillar_util.get_minion_pillar()
        else:
            __grains__ = salt.loader.grains(__opts__, proxy=__proxy__)
            __pillar__ = __salt__['pillar.items']()
    elif role == 'master':
        __salt__ = salt.loader.runner(__opts__, utils=__utils__)

    dunders = {
        'salt': salt,
        '__opts__': __opts__,
        '__salt__': __salt__,
        '__proxy__': __proxy__,
        '__grains__': __grains__,
        '__pillar__': __pillar__,
    }
    sys.argv = sys.argv[:1]

    ipy_cfg = traitlets.config.loader.Config()
    if int(IPython.__version__[0]) >= 6:
        ipy_cfg.TerminalInteractiveShell.term_title_format = 'ISalt'
    else:
        ipy_cfg.TerminalInteractiveShell.term_title = False
    ipy_cfg.InteractiveShell.banner1 = BANNER + '''\n
        Salt version: {salt_ver}
       IPython version: {ipython_ver}\n'''.format(
        salt_ver=salt.version.__version__,
        ipython_ver=IPython.__version__
    )
    IPython.start_ipython(config=ipy_cfg, user_ns=dunders)


if __name__ == '__main__':
    main()
