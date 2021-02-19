# -*- coding: utf-8 -*-
# Copyright 2019-2020 Mircea Ulinic. All rights reserved.
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
import salt.utils.napalm
import salt.utils.master
import salt.modules.pillar
import salt.utils.platform

try:
    import salt_sproxy

    HAS_SPROXY = True
except ImportError:
    HAS_SPROXY = False

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
    """
    The entry point to the ISalt console.

    cfg_file
        Absolute path to the ISalt config file to read.

    cfg_file_env_var: ``ISALT_CFG_FILE``
        The environment variable containing the path to the ISalt config file.

    saltenv: ``base``
        The name of the Salt environment.

    pillarenv: ``base``
        The environment name to render the Pillar from.
    """
    parser = argparse.ArgumentParser(description='ISalt console')
    parser.add_argument('--saltenv', default='base', help='Salt environment name.')
    parser.add_argument(
        '--pillarenv',
        default='base',
        help='The Salt environment name to compile the Pillar from.',
    )
    parser.add_argument(
        '-c',
        '--cfg-file',
        default='/etc/salt/isalt',
        dest='cfg_file',
        help='The absolute path to the ISalt config file.',
    )
    parser.add_argument(
        '-e',
        '--env-var',
        default='ISALT_CFG_FILE',
        dest='cfg_file_env_var',
        help='The name of the environment variable pointing to the ISalt config file.',
    )
    parser.add_argument(
        '--minion-cfg',
        default='/etc/salt/minion',
        dest='minion_cfg_file',
        help='The absolute path to the Minion config file.',
    )
    parser.add_argument(
        '--proxy-cfg',
        default='/etc/salt/proxy',
        dest='proxy_cfg_file',
        help='The absolute path to the Proxy Minion config file.',
    )
    parser.add_argument(
        '--master-cfg',
        default='/etc/salt/master',
        dest='master_cfg_file',
        help='The absolute path to the Master config file.',
    )
    parser.add_argument(
        '--minion', action='store_true', help='Prepare the Salt dunders for the Minion.'
    )
    parser.add_argument('--proxytype', help='The Salt Proxy module name to use.')
    parser.add_argument(
        '--proxy',
        action='store_true',
        help='Prepare the Salt dunders for the Proxy Minion.',
    )
    parser.add_argument(
        '--sproxy',
        action='store_true',
        help='Prepare the Salt dunders for the salt-sproxy (Master side).',
    )
    parser.add_argument(
        '--master', action='store_true', help='Prepare the Salt dunders for the Master.'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help=(
            'Override the Minion config and use the local client.\n'
            'This option loads the file roots config from the Master file.'
        ),
    )
    parser.add_argument(
        '--minion-id',
        dest='minion_id',
        help=(
            'The Minion ID to compile the Salt dunders for.\n'
            'This argument is optional, however it may fail when ISalt is not '
            'able to determine the Minion ID, or take it from the environment '
            'variable, etc.'
        ),
    )
    parser.add_argument(
        '--on-master',
        action='store_true',
        help=(
            'Whether should compile the dunders for the Minion side, starting '
            'the ISalt console on the Master machine.\n'
            'This option is ignored when used in conjunction with --master.'
        ),
    )
    args = parser.parse_args()
    isalt_cfg = salt.config.load_config(args.cfg_file, args.cfg_file_env_var)

    on_master = args.on_master or os.environ.get(
        'ISALT_ON_MASTER', isalt_cfg.get('on_master', False)
    )
    minion_id = args.minion_id or os.environ.get(
        'ISALT_MINION_ID', isalt_cfg.get('minion_id')
    )
    proxytype = args.proxytype or os.environ.get(
        'ISALT_PROXYTYPE', isalt_cfg.get('proxytype')
    )
    role = os.environ.get('ISALT_ROLE', isalt_cfg.get('role', 'minion'))
    if args.sproxy:
        role = 'sproxy'
    if args.minion or minion_id:
        role = 'minion'
    if args.proxy or proxytype:
        role = 'proxy'
    if args.master:
        role = 'master'
    if role == 'sproxy':
        if not HAS_SPROXY:
            raise ISaltError('salt-sproxy doesn\'t seem to be installed')
    master_cfg_file = args.master_cfg_file or os.environ.get(
        'ISALT_MASTER_CONFIG',
        isalt_cfg.get(
            'master_config',
            salt.config.DEFAULT_MASTER_OPTS['conf_file'],
        ),
    )
    master_opts = salt.config.master_config(master_cfg_file)
    if role in ('minion', 'proxy'):
        if role == 'minion':
            cfg_file = args.minion_cfg_file or os.environ.get(
                'ISALT_MINION_CONFIG',
                isalt_cfg.get(
                    'minion_config',
                    salt.config.DEFAULT_MINION_OPTS['conf_file'],
                ),
            )
            __opts__ = salt.config.minion_config(cfg_file)
        else:
            cfg_file = args.proxy_cfg_file or os.environ.get(
                'ISALT_PROXY_MINION_CONFIG',
                isalt_cfg.get(
                    'proxy_minion_config',
                    salt.config.DEFAULT_PROXY_MINION_OPTS['conf_file'],
                ),
            )
            __opts__ = salt.config.proxy_config(cfg_file, minion_id=minion_id)
            proxytype = proxytype or __opts__.get('proxy', {}).get('proxytype')
            if 'proxy' not in __opts__:
                __opts__['proxy'] = {'proxytype': proxytype}
            else:
                __opts__['proxy']['proxytype'] = proxytype
        minion_id = minion_id or __opts__['id']
        local = args.local or isalt_cfg.get('local', False)
        if local and __opts__.get('file_client') != 'local':
            __opts__['file_client'] = 'local'
            for opt, value in master_opts.items():
                if opt.startswith(
                    (
                        'gitfs_',
                        'git_',
                        'azurefs_',
                        'hgfs_',
                        'minionfs_',
                        's3fs_',
                        'svnfs_',
                        'pillar_roots',
                        'file_roots',
                    )
                ):
                    __opts__[opt] = value
        if not minion_id:
            raise ISaltError('Unable to determine a Minion ID')
        __opts__['id'] = minion_id
    elif role in ('master', 'sproxy'):
        __opts__ = salt.config.master_config(master_cfg_file)
    __opts__['saltenv'] = args.saltenv
    __opts__['pillarenv'] = args.pillarenv

    __utils__ = None
    __proxy__ = None
    __grains__ = None
    __pillar__ = None

    if role == 'proxy':

        def _is_proxy():
            return True

        def _napalm_is_proxy(opts):
            return opts.get('proxy', {}).get('proxytype') == 'napalm'

        salt.utils.platform.is_proxy = _is_proxy
        salt.utils.napalm.is_proxy = _napalm_is_proxy

    if role in ('minion', 'proxy'):
        if on_master:
            use_cached_pillar = bool(
                os.environ.get(
                    'ISALT_USE_CACHED_PILLAR', isalt_cfg.get('use_cached_pillar', True)
                )
            )
            pillar_util = salt.utils.master.MasterPillarUtil(
                minion_id,
                'glob',
                use_cached_grains=True,
                grains_fallback=False,
                use_cached_pillar=use_cached_pillar,
                pillar_fallback=True,
                opts=master_opts,
            )

            grains = pillar_util.get_minion_grains()
            __grains__ = grains[minion_id] if grains and minion_id in grains else {}
            pillar = pillar_util.get_minion_pillar()
            __pillar__ = pillar[minion_id] if pillar and minion_id in pillar else {}
            if __pillar__ and 'proxy' in __pillar__:
                __opts__['proxy'] = __pillar__['proxy']

            __utils__ = salt.loader.utils(__opts__)
            __proxy__ = salt.loader.proxy(__opts__, utils=__utils__)
            __salt__ = salt.loader.minion_mods(
                __opts__,
                utils=__utils__,
                proxy=__proxy__,
            )
        else:
            if not os.path.exists(__opts__['cachedir']):
                try:
                    os.mkdir(__opts__['cachedir'])
                except OSError as ose:
                    print(
                        'Unable to create the cache directory',
                        __opts__['cachedir'],
                        'please make sure you are running ISalt with the correct permissions',
                    )
                    raise ose
            if role == 'minion':
                sminion = salt.minion.SMinion(__opts__)
            else:
                use_cached_pillar = bool(
                    os.environ.get(
                        'ISALT_USE_CACHED_PILLAR',
                        isalt_cfg.get('use_cached_pillar', True),
                    )
                )
                pillar_util = salt.utils.master.MasterPillarUtil(
                    minion_id,
                    'glob',
                    use_cached_grains=True,
                    grains_fallback=False,
                    use_cached_pillar=use_cached_pillar,
                    pillar_fallback=True,
                    opts=master_opts,
                )
                grains = pillar_util.get_minion_grains()
                __grains__ = grains[minion_id] if grains and minion_id in grains else {}
                pillar = pillar_util.get_minion_pillar()
                __pillar__ = pillar[minion_id] if pillar and minion_id in pillar else {}

                if __pillar__ and 'proxy' in __pillar__:
                    __opts__['proxy'] = __pillar__['proxy']

                if salt.version.__version_info__ >= (2019, 2, 0):
                    sminion = salt.minion.SProxyMinion(__opts__)
                else:
                    sminion = salt.minion.ProxyMinion(__opts__)
            __proxy__ = sminion.proxy
            __utils__ = sminion.utils
            __salt__ = sminion.functions
            __grains__ = __opts__['grains']
            __pillar__ = __salt__['pillar.items']()
    elif role in ('master', 'sproxy'):
        if role == 'sproxy':
            saltenv = __opts__['saltenv']
            if saltenv not in __opts__.get('file_roots', {}):
                __opts__['file_roots'] = {saltenv: []}
            file_roots = __opts__['file_roots'][saltenv]
            sproxy_path = list(salt_sproxy.__path__)[0]
            if sproxy_path not in file_roots:
                file_roots.append(sproxy_path)
                __opts__['file_roots'][saltenv] = file_roots
            sproxy_dirs = [
                (sproxy_dir[:-1] if sproxy_dir[-1] == 's' else sproxy_dir)
                for sproxy_dir in os.listdir(sproxy_path)
                if sproxy_dir.startswith('_')
                and not sproxy_dir.startswith('__')
                and os.path.isdir(os.path.join(sproxy_path, sproxy_dir))
            ]
            for sproxy_dir in sproxy_dirs:
                sproxy_dirs_opts = '{}_dirs'.format(sproxy_dir.replace('_', '', 1))
                if sproxy_dirs_opts not in __opts__:
                    __opts__[sproxy_dirs_opts] = []
                sproxy_dir_path = os.path.join(sproxy_path, sproxy_dir)
                if sproxy_dir_path not in __opts__[sproxy_dirs_opts]:
                    __opts__[sproxy_dirs_opts].append(sproxy_dir_path)
        __utils__ = salt.loader.utils(__opts__)
        __salt__ = salt.loader.runner(__opts__, utils=__utils__)

    dunders = {
        'salt': salt,
        '__utils__': __utils__,
        '__opts__': __opts__,
        '__salt__': __salt__,
        '__proxy__': __proxy__,
        '__grains__': __grains__,
        '__pillar__': __pillar__,
    }
    if role == 'sproxy':
        dunders['sproxy'] = __salt__['proxy.execute']
    sys.argv = sys.argv[:1]

    ipy_cfg = traitlets.config.loader.Config()
    if int(IPython.__version__[0]) >= 6:
        ipy_cfg.TerminalInteractiveShell.term_title_format = 'ISalt'
    else:
        ipy_cfg.TerminalInteractiveShell.term_title = False
    ipy_cfg.InteractiveShell.banner1 = BANNER + '''\n
           Role: {role}
        Salt version: {salt_ver}
       IPython version: {ipython_ver}\n'''.format(
        role=role.title(),
        salt_ver=salt.version.__version__,
        ipython_ver=IPython.__version__,
    )
    IPython.start_ipython(config=ipy_cfg, user_ns=dunders)


if __name__ == '__main__':
    main()
