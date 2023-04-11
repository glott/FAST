# IMPORTS AND ZIP DOWNLOAD
import zipfile, os, shutil, urllib.request, subprocess, sys, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('requests')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'requests']);

import requests

if len(sys.argv) > 1:
    sys.stdout = open(os.devnull, 'w')

print('-------------------- FAST --------------------')
print('Downloading the latest version of FAST')

try:
    url = 'https://github.com/glott/FAST/releases/latest/download/FAST.zip'
    urllib.request.urlretrieve(url, 'FAST.zip');
    print('Downloaded FAST.zip')
except Exception:
    print('Unable to download FAST.zip')

# ZIP EXTRACTION AND DELETION
files = zipfile.ZipFile('FAST.zip', 'r')
files.extractall('FAST_update')
files.close()

print('Extracted temporary update files')

try:
    os.remove('FAST.zip')
    print('Deleted FAST.zip')
except Exception:
    print('Unable to delete FAST.zip')
    pass

# FILE MANIPULATION METHODS
cwd = os.getcwd()
out_dir = cwd

def merge_config(f_old, f_new):
    with open(f_old, 'r') as file:
        old_config = file.read().split('\n')
    with open(f_new, 'r') as file:
        new_config = file.read().split('\n')
    
    c = {}
    for line in old_config:
        if len(line) > 0 and '#' not in line[0] and '=' in line:
            c[line.split('=')[0]] = line.split('=')[1]
    
    out_config = list()
    for line in new_config:
        if len(line) > 0 and '#' not in line[0] and '=' in line:
            split = line.split('=')
            if split[0] in c:
                out_config.append(split[0] + '=' + c[split[0]])
            else:
                out_config.append(line)
        else:
            out_config.append(line)
    
    try:
        with open(f_old, 'w') as out_file:
            out_file.write('\n'.join(out_config))
            
        print('Merged FAST.txt')
    except Exception:
        print('Unable to merge FAST.txt')
        pass

def move_file(f, w='update'):
    file_name = os.path.basename(f)
    try:
        old_file = out_dir + '\\' + file_name
        if os.path.isfile(old_file):
            os.remove(old_file)
        else:
            w = 'create'
        shutil.move(f, out_dir)
        
        print(w.capitalize() + 'd ' + file_name)
    except Exception:
        print('Unable to ' + w + ' ' + file_name)
        pass

# UPDATE FILES AND MERGE CONFIG
for file in os.listdir(cwd + '\\FAST_update'):
    f = os.path.join(cwd + '\\FAST_update', file)
    if 'FAST.txt' not in file:
        move_file(f)
    else:
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        if 'FAST.txt' in files:
            merge_config(cwd + '\\FAST.txt', f)
        else:
            move_file(f, w='create')
    
try:
    shutil.rmtree(cwd + '\\FAST_update')
    print('Deleted temporary update files')
except Exception:
    print('Unable to delete temporary update files')
    pass

# ADD VERSION TO FAST.txt
try: 
    response = urllib.request.urlopen( \
        'https://github.com/glott/FAST/releases/latest')
    v = str(response.read()).split('FAST/tree/')[1].split(r'"')[0][1:]

    config_file = cwd + '\\FAST.txt'

    if os.path.isfile(config_file):
        with open(config_file, 'r') as file:
            config = file.read()
            space = '#                                           #'
            fill = '#############################################'
            double = space + '\n' + fill
            version = '#               Version ' + v + '               #\n'
            config = config.replace(double, version + double)

        with open(config_file, 'w') as out_file:
            out_file.write(config)

        print('Added version to FAST.txt')
except Exception:
    pass
    
print('\nAll FAST files updated successfully!')
if len(sys.argv) == 1:
    input('Press enter to close.');
else:
    sys.stdout = sys.__stdout__