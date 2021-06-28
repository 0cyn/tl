

# Code from https://github.com/DragonBuild/dragon
# Loads a Makefile and Subprojects, returns it as a big ass dict 

# This is going to spit out info in the dragon format, 
# however since that format is minimalistic in design
# it is useful anywhere.
import re as regex
import os, sys

make_match = regex.compile('(.*)=(.*)#?')
make_type = regex.compile(r'include.*\/(.*)\.mk')
nepmatch = regex.compile(r'(.*)\+=(.*)#?')  # nep used subproj += instead of w/e and everyone copies her.


def interpret_theos_makefile(file: object, root: object = True) -> dict:
    project = {}
    variables = {}
    stage = []
    stageactive = False
    module_type = ''
    arc = False
    hassubproj = False
    noprefix = False
    try:
        while 1:
            line = file.readline()
            if not line:
                break
            if not arc and '-fobjc-arc' in line:
                arc = True
            if not noprefix and '-DTHEOS_LEAN_AND_MEAN' in line:
                noprefix = True
            if line.startswith('internal-stage::'):
                stageactive = True
                continue
            if stageactive:
                if line.startswith((' ', '\t')):
                    x = line
                    x = x.replace('$(THEOS_STAGING_DIR)', '$proj_build_dir/_')
                    x = x.replace('$(ECHO_NOTHING)', '')
                    x = x.replace('$(ECHO_END)', '')
                    stage.append(x)
                else:
                    stageactive = False

            if not make_match.match(line):
                if not make_type.match(line):
                    continue
                if 'aggregate' in make_type.match(line).group(1):
                    hassubproj = True
                else:
                    module_type = make_type.match(line).group(1)
                continue

            if not nepmatch.match(line):
                name, value = make_match.match(line).group(1, 2)
            else:
                name, value = nepmatch.match(line).group(1, 2)
            if name.strip() in variables:
                variables[name.strip()] = variables[name.strip()] + ' ' + value.strip()
            variables[name.strip()] = value.strip()
    finally:
        file.close()

    if root:
        project['name'] = os.path.basename(os.getcwd())
        if 'INSTALL_TARGET_PROCESS' in variables:
            project['icmd'] = 'killall -9 ' + variables['INSTALL_TARGET_PROCESS']
        else:
            project['icmd'] = 'sbreload'

    modules = []
    mod_dicts = []
    # if module_type == 'aggregate':

    module_type_naming = module_type.upper()

    module_name = variables.get(f'{module_type_naming}_NAME')
    module_archs = variables.get(f'ARCHS')
    module_files = variables.get(module_name + '_FILES') or variables.get(f'$({module_type_naming}_NAME)_FILES') or ''
    module_cflags = variables.get(module_name + '_CFLAGS') or variables.get('$({module_type_naming}_NAME)_CFLAGS') or ''
    module_cxxflags = variables.get(module_name + '_CXXFLAGS') or variables.get('$({module_type_naming}_NAME)_CXXFLAGS') or ''
    module_cflags = variables.get(f'ADDITIONAL_CFLAGS') or ''
    module_ldflags = variables.get(module_name + '_LDFLAGS') or variables.get(
        f'$({module_type_naming}_NAME)_LDFLAGS') or ''
    module_codesign_flags = variables.get(module_name + '_CODESIGN_FLAGS') or variables.get(
        f'$({module_type_naming}_NAME)_CODESIGN_FLAGS') or ''
    module_ipath = variables.get(module_name + '_INSTALL_PATH') or variables.get(
        f'$({module_type_naming}_NAME)_INSTALL_PATH') or ''
    module_frameworks = variables.get(module_name + '_FRAMEWORKS') or variables.get(
        f'$({module_type_naming}_NAME)_FRAMEWORKS') or ''
    module_pframeworks = variables.get(module_name + '_PRIVATE_FRAMEWORKS') or variables.get(
        f'$({module_type_naming}_NAME)_PRIVATE_FRAMEWORKS') or ''
    module_eframeworks = variables.get(module_name + '_EXTRA_FRAMEWORKS') or variables.get(
        f'$({module_type_naming}_NAME)_EXTRA_FRAMEWORKS') or ''
    module_libraries = variables.get(module_name + '_LIBRARIES') or variables.get(
        f'$({module_type_naming}_NAME)_LIBRARIES') or ''

    files = []
    if module_files:
        tokens = module_files.split(' ')
        nextisawildcard = False
        for i in tokens:
            if '$(wildcard' in i:
                nextisawildcard = 1
                continue
            if nextisawildcard:
                # We dont want to stop with these till we hit a ')'
                # thanks cr4shed ._.
                nextisawildcard = 0 if ')' in i else 1
                grab = i.split(')')[0]
                files.append(grab.replace(')', ''))
                continue
            files.append(i)

    module = {
        'type': module_type,
        'files': files
    }
    if module_name != '':
        module['name'] = module_name
    module['frameworks'] = []
    if module_frameworks != '':
        module['frameworks'] += module_frameworks.split(' ')
    if module_pframeworks != '':
        module['frameworks'] += module_pframeworks.split(' ')
    if module_eframeworks != '':
        module['frameworks'] += module_eframeworks.split(' ')
    if module_libraries != '':
        module['libs'] = module_libraries
    if module_archs != '':
        module['archs'] = module_archs
    else:
        module['archs'] = ['arm64', 'arm64e']
    if module_cflags != '':
        module['cflags'] = module_cflags
    if module_cxxflags:
        module['cxxflags'] = module_cxxflags
    if module_ldflags:
        module['ldflags'] = module_ldflags
    if stage != []:
        module['stage'] = stage
    module['arc'] = arc
    if not root:
        return module
    else:
        mod_dicts.append(module)
        project['name'] = module['name']
        modules.append('.')

    if hassubproj and 'SUBPROJECTS' in variables:
        modules = modules + variables['SUBPROJECTS'].split(' ')

    rename_counter = 1
    for module in modules:
        if module != '.' and os.path.exists(module + '/Makefile'):
            new = interpret_theos_makefile(open(module + '/Makefile'), root=False)
            if new['name'].lower() == project['name'].lower():
                rename_counter += 1
                new['name_override'] = new['name']
                new['name'] = new['name'] + str(rename_counter)
            mod_dicts.append(new)

    i = 0
    for mod in mod_dicts:
        if mod:
            project[mod['name']] = mod
            project[mod['name']]['dir'] = modules[i]
            i += 1

    # the magic of theos

    if 'export ARCHS' in variables:
        project['all'] = {
            'archs': variables['export ARCHS'].split(' ')
        }
    return project