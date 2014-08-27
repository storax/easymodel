#!/usr/bin/env python
""" Generate config files for travis, tox

Source - https://github.com/ionelmc/cookiecutter-pylibrary/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/bootstrap.py

Put the templates in the conf folder.
Use setup.cfg to configer your test matrix.
Run bootstrap for each update.
"""
import os
import sys

import jinja2
import matrix

if not os.path.exists('.tox/configure'):
    import virtualenv
    import subprocess
    print("Bootstrapping ...")
    virtualenv.create_environment('.tox/configure')
    print("Installing `jinja2` and `matrix` into bootstrap environment ...")
    if sys.platform == 'win32':
        subprocess.check_call(['.tox/configure/Scripts/pip', 'install', 'jinja2', 'matrix'])
    else:
        subprocess.check_call(['.tox/configure/bin/pip', 'install', 'jinja2', 'matrix'])

if sys.platform == 'win32':
    execfile('.tox/configure/Scripts/activate_this.py', dict(__file__='.tox/configure/Scripts/activate_this.py'))
else:
    execfile('.tox/configure/bin/activate_this.py', dict(__file__='.tox/configure/bin/activate_this.py'))


jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader('conf'),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True
)
tox_environments = {}
for alias, conf in matrix.from_file('setup.cfg').items():
    python = conf['python_versions']
    deps = conf['dependencies']
    cover = {'false': False, 'true': True}[conf['coverage_flags'].lower()]
    env_vars = conf['environment_variables']

    tox_environments[alias] = {
        'python': 'python' + python if 'py' not in python else python,
        'deps': deps.split(),
        'cover': cover,
        'env_vars': env_vars.split(),
    }

for name in os.listdir('conf'):
    with open(name, 'w') as fh:
        fh.write(jinja.get_template(name).render(tox_environments=tox_environments))
    print("Wrote %s" % name)

print("DONE.")