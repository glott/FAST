# IMPORTS AND COMMON FUNCTIONS
import csv, math, os, pathlib, random, random, re, subprocess
import sys, time, urllib.request, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import imp
    imp.find_module('requests')
    imp.find_module('selenium')
    imp.find_module('webdriver_manager')
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'requests']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'selenium']);
    subprocess.check_call([sys.executable, '-m', 'pip', 
                           'install', 'webdriver_manager']);

import requests
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
                    for i in range(5, 0, -1):
                        print('Restarting ' + os.path.basename(__file__) \
                            + ' in ' + str(i) + '.', end='\r')
                        time.sleep(1)
                    print(end='\n')
                    os.system('cls')
                    os.system('python ' + ' '.join(sys.argv))
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

# OPEN BROWSER
browser = read_config_value('BROWSER').capitalize()
print('Opening ' + browser + '.')

driver = None
if 'C' in browser:
    options = webdriver.chrome.options.Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path=ChromeDriverManager()
        .install(), options=options);
else:
    driver = webdriver.Firefox(executable_path=GeckoDriverManager() \
        .install(), service_log_path=os.devnull);
driver.minimize_window()

# LOGIN TO VATSIM AND vNAS
print('Opening vNAS login page.')
driver.get('https://data-admin.virtualnas.net/login')

click_button('Login with VATSIM')
wait()

try:
    print('Logging in to VATSIM.')
    driver.find_element('id', 'vatsim-id') \
        .send_keys(read_config_value('VATSIM_USER'))
    driver.find_element('id', 'password') \
        .send_keys(read_config_value('VATSIM_PASS'))
    click_button('Sign in')
    print('Successfully logged in to VATSIM.')
except Exception:
    print('Unsuccessfully logged in to VATSIM.')

wait(w=5)

try:
    ARTCC = read_config_value('ARTCC')
    print('Selecting ' + ARTCC + ' ARTCC.')
    
    driver.find_element('xpath', \
        '//div[@class=\'nav-item dropdown artcc-menu\']') \
        .find_element('class name', 'nav-link').click()
    wait()
    dropdown = driver.find_element('xpath', \
        '//div[@class=\'dropdown-menu dropdown-menu-right ' \
        + 'dropdown-menu-md show\']')
    for div in dropdown.find_element('xpath', './child::*') \
        .find_elements('xpath', './child::*'):
            if ARTCC in div.text:
                div.click()
    print('Successfully selected ' + ARTCC + ' ARTCC.')
except Exception:
    pass

wait()

# UPLOAD METHODS
def get_plane_id():
    return re.findall(r'aircraft\[[0-9]{1,4}\]', driver.page_source)[0] \
        .split('[')[1].split(']')[0]

def get_command_current_id(pos):
    return len(re.findall(r'aircraft\[' + pos + 
        r'\]\.presetCommands\[[0-9]{1,4}\]', driver.page_source)) - 1
    
def set_data(pos, element, value):
    elem = driver.find_element('name', 'aircraft[' + pos + '].' 
        + element)
    driver.execute_script('arguments[0].value=\'' + \
        str(value) + '\';', elem)
    elem.send_keys('0' + webdriver.common.keys.Keys.BACKSPACE)
    
def set_data_drop(pos, header, value):
    Select(driver.find_element('xpath', '//option[text()=\'' \
        + header + '\']').find_element('xpath', '..')) \
        .select_by_value(value)
    
def delete_existing(ident):
    if ident in existing_planes:
        elem = driver.find_element('xpath', '//input[@value=\'' \
            + ident + '\']')
        button = elem.find_element('xpath', '../../..') \
            .find_element('class name', 'btn-danger')
        driver.execute_script('arguments[0].scrollIntoView(true);', button)
        driver.execute_script('window.scrollBy(0, -' + 
            str(round(button.size['height'] * 2)) + ');')
        button.click()
        
def calc_M(v, alt):
    temp = (-6.49e-3 * float(alt) * .3048 + 14.9855) + 273.15
    a = (1.4 * 287.053 * temp) ** .5 * 1.944
    return round(float(v) / a, 3)

# UPLOAD DATA TO vNAS
print('Opening scenario ' + read_config_value('ARR_SCENARIO') + '.')
driver.get('https://data-admin.virtualnas.net/training/scenarios/' \
           + read_config_value('ARR_SCENARIO'))

wait()

try: 
    file_in = '\\scenarios\\' + read_config_value('ARR_CSV_FILE')
    if '.' not in file_in: file_in += '.csv'
    f = open(working_directory + file_in, 'r')
    reader = csv.DictReader(f, delimiter=',')
    wait()
except Exception:
    print('Unable to read ' + read_config_value('ARR_CSV_FILE') \
        + ' from \'scenarios\' subdirectory.\n')
    pass

transitions = {}
if ',' in read_config_value('RWY_TRANSITION'):
    for rt in read_config_value('RWY_TRANSITION').split(','):
        transitions[rt.split(':')[0]] = rt.split(':')[1]

current_planes = driver.find_elements('xpath', '//input[@disabled=\'\']')
existing_planes = list()
for plane in current_planes:
    existing_planes.append(plane.get_attribute('value'))

max_delay = int(read_config_value('ARR_MAX_DELAY'))
prev_spawn_delay = -1

for plane in reader:
    if(len(plane['dct']) == 0 or len(plane['proc']) == 0):
        print('Skipping ' + plane['ident'] + ', invalid procedure.')
        continue
    delete_existing(plane['ident'])
    click_button('Add Aircraft')
    wait(w=0)
    print('Uploading data for ' + plane['ident'] + '.')
    
    pos = get_plane_id()
    set_data(pos, 'aircraftId', plane['ident'])
    set_data(pos, 'aircraftType', plane['type'])
    set_data_drop(pos, 'Standby', 'C')
    true_spawn_delay = round(int(plane['spawn-delay']) \
        / float(read_config_value('ARR_TIME_COMPRESSION')) \
        - int(read_config_value('ARR_TIME_OFFSET')))
    if prev_spawn_delay == -1:
        true_spawn_delay = 0
    if true_spawn_delay < 0: 
        true_spawn_delay = 0
    if true_spawn_delay - prev_spawn_delay > max_delay:
        true_spawn_delay = prev_spawn_delay + max_delay \
            + random.randint(0, 15)
    prev_spawn_delay = true_spawn_delay
    set_data(pos, 'spawnDelay', true_spawn_delay)
    set_data(pos, 'airportId', plane['arr'][1:])
    set_data(pos, 'expectedApproach', '')
    oap = driver.find_element('xpath', 
        '//label[contains(text(), \'On Altitude Profile\')]')
    oap.find_element('xpath', '..//div//input[@type=\'checkbox\']').click()

    click_button('Create Flight Plan')
    
    if 'I' in plane['rules']: 
        set_data_drop(pos, 'DVFR', 'IFR')
    else: 
        set_data_drop(pos, 'DVFR', 'VFR')
    set_data(pos, 'flightplan.departure', plane['dep'])
    set_data(pos, 'flightplan.destination', plane['arr'])
    set_data(pos, 'flightplan.cruiseAltitude', plane['alt'])
    set_data(pos, 'flightplan.cruiseSpeed', plane['speed'])
    equip = '/' + plane['equip'] if len(plane['equip']) > 0 else ''
    set_data(pos, 'flightplan.aircraftType', plane['type'] + equip)
    set_data(pos, 'flightplan.route', plane['route'])
    set_data(pos, 'flightplan.remarks', '/v/ Gate ' + plane['gate'])
    
    set_data_drop(pos, 'Coordinates', 'Coordinates')
    set_data(pos, 'startingConditions.coordinates.lat', plane['lat'])
    set_data(pos, 'startingConditions.coordinates.lon', plane['lon'])
    set_data(pos, 'startingConditions.altitude', plane['ralt'])
    mach = calc_M(plane['rspeed'], plane['ralt'])
    if mach < .6:
        set_data(pos, 'startingConditions.speed', plane['rspeed'])
    else:
        set_data(pos, 'startingConditions.mach', mach)      
    set_data(pos, 'startingConditions.heading', plane['hdg'])
    
    proc_str = plane['proc'][0:-1]
    proc_add = ''
    if proc_str in transitions:
        proc_add = '.' + transitions[proc_str]
        
    dct_proc = plane['dct'] + ' ' + plane['proc']
    if plane['dct'] + ' ' in plane['proc']:
        dct_proc = plane['proc']
    set_data(pos, 'startingConditions.navigationPath', dct_proc + proc_add)
    
    click_button('Done')
    
click_button('Save')
f.close()

print('Data upload to vNAS complete!')