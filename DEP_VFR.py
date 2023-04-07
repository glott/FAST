# IMPORTS AND COMMON FUNCTIONS
import csv, os, pathlib, random, random, re, requests
import subprocess, sys, time, urllib.request, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('selenium')
    imp.find_module('webdriver_manager')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'selenium']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'webdriver_manager']);
    
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

working_directory = ''
if os.path.isfile(os.getcwd() + '\\FAST.txt'):
    working_directory = os.getcwd()
elif os.path.isfile(str(pathlib.Path.home() / 'Downloads\\FAST.txt')):
    working_directory = str(pathlib.Path.home() / 'Downloads')
else:
    print('FAST.txt file not found!\nPlace valid FAST.txt file in this ' \
          + 'folder or in your Downloads folder.\nDefault file:' \
          + ' https://raw.githubusercontent.com/glott/FAST/main/FAST.txt')
    
def check_for_updates():
    try: 
        response = urllib.request.urlopen( \
            'https://github.com/glott/FAST/releases/latest')
        ver = str(response.read()).split('FAST/tree/')[1].split(r'"')[0][1:]
        
        config_file = os.getcwd() + '\\FAST.txt'
        readme_file = os.getcwd() + '\\README.md'
        if os.path.isfile(config_file) and not os.path.isfile(readme_file):
            with open(config_file, 'r') as file:
                config = file.read()
            if 'Version ' in config:
                config_version = config.split('Version ')[1].split(' ')[0]
                if config_version not in ver:
                    os.system('python FAST_UPDATE.py 0')
                    print('Updated FAST files to v' + ver + '.')
    except Exception:
        pass

print('-------------------- FAST --------------------')
check_for_updates()

def read_config_value(key):
    config = open(working_directory + '\\FAST.txt', 'r').read()
    if key + '=' in config:
        return config.split(key + '=')[1].split('\n')[0]
    return 'NULL'

def between(text, start, end):
    try: 
        return text.split(start)[1].split(end)[0]
    except Exception:
        return ''
    
def click_button(text):
    try: 
        button = driver.find_element('xpath', 
           '//button[contains(text(), \'' + text + '\')]')
        driver.execute_script('arguments[0].scrollIntoView(true);', button)
        driver.execute_script('window.scrollBy(0, -' + 
            str(round(button.size['height'] * 2)) + ');')
        button.click()
    except Exception:
        print('Unable to click button \'' + text + '\'.')

sleep_factor = float(read_config_value('SLOW_INTERNET_FACTOR'))
def wait(w=1, t=5):
    try:
        webdriver.support.ui.WebDriverWait(driver, t).until(webdriver \
        .support.expected_conditions.url_changes(driver.current_url))
    except Exception:
        pass
    time.sleep(w * sleep_factor)

# READ CONFIG FILE AND GENERATE RANDOM VALUES
print('Generating random VFR aircraft.')
def n_reg(n):
    a = list('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ')
    regs = ['N346G']
    for i in range(0, n - 1):
        reg = 'N' + a[random.randint(1, 9)] + a[random.randint(0, 9)] \
            + a[random.randint(0, 9)] + a[random.randint(0, 33)]
        if random.randint(0, 2) < 2: 
            if reg[4].isdigit(): 
                reg += a[random.randint(0, 9)]
            else:
                reg += a[random.randint(10, 33)]
        regs.append(reg)
    return regs

def process_types(vfr_types, n):
    aircraft = list()
    weights = list()
    for a in vfr_types.split(','):
        try: 
            aircraft.append(a.split(':')[0])
            weights.append(int(a.split(':')[1]))
        except Exception:
            print('Unable to process VFR_TYPES, check config!')
            pass
    
    return random.choices(aircraft, weights=weights, k=n)

def process_delays(spawn_delay_range, n):
    delays = [0]
    for i in range(1, n):
        rand_delay = random.randint(int(spawn_delay_range.split('-')[0]), \
            int(spawn_delay_range.split('-')[1]))
        delays.append(rand_delay + delays[i - 1])
    return delays
    
num_vfr = int(read_config_value('NUM_VFR'))
ga_parking = list(set(read_config_value('GA_PARKING').split(',')) \
    - set(read_config_value('GA_PARKING_RESERVED').split(',')))
random.shuffle(ga_parking)
if num_vfr > len(ga_parking): num_vfr = len(ga_parking)

print('Generating aircraft registrations.')
regs = n_reg(20)
print('Generating aircraft types.')
types = process_types(read_config_value('VFR_TYPES'), num_vfr)
print('Generating spawn delays.')
delays = process_delays(read_config_value('SPAWN_DELAY_RANGE'), num_vfr)

# CREATE AIRCRAFT DATA FILE
s = 'ident,type,dep,arr,alt,speed,route,rules,equip,spawn-delay,' \
    + 'gate,push-taxiway,taxi-route'

airport = read_config_value('AIRPORT')

for i in range(0, num_vfr):
    s += '\n' + ','.join([regs[i], types[i], airport, '', '0', '0', '', \
        'V', '', str(delays[i]), ga_parking[i], '', ''])

out_file = s.split('\n')[1].split(',')[2][1:] + '_DEP_VFR_' \
    + time.strftime('%y%m%d-%H%M', time.gmtime()) + '.csv'
print('Writing aircraft data to ' + str(out_file) + '.')
with open(working_directory + '\\' + out_file, 'w') as f: 
    f.write(s)

print('VFR departure generation complete!')