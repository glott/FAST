# IMPORTS AND COMMON FUNCTIONS
import os, subprocess, sys, time, random, pathlib, csv, re, warnings, random
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
print('-------------------- FAST --------------------')
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

# UPLOAD DATA TO vNAS
def get_plane_id():
    return re.findall(r'aircraft\[[0-9]{1,4}\]', driver.page_source)[0] \
        .split('[')[1].split(']')[0]

def get_command_current_id(pos):
    return len(re.findall(r'aircraft\[' + pos + 
        r'\]\.presetCommands\[[0-9]{1,4}\]', driver.page_source)) - 1
    
def set_data(pos, element, value):
    driver.find_element('name', 'aircraft[' + pos + '].' 
        + element).clear()
    driver.find_element('name', 'aircraft[' + pos + '].' 
        + element).send_keys(value)
    
def set_data_drop(pos, header, value):
    Select(driver.find_element('xpath', '//option[text()=\'' \
        + header + '\']').find_element('xpath', '..')) \
        .select_by_value(value)

print('Opening scenario ' + read_config_value('SCENARIO') + '.')
driver.get('https://data-admin.virtualnas.net/training/scenarios/' \
           + read_config_value('SCENARIO'))

wait()

file_in = read_config_value('CSV_FILE')
if '.' not in file_in: file_in += '.csv'
f = open(working_directory + '\\' + file_in, 'r')
reader = csv.DictReader(f, delimiter=',')
wait()

for plane in reader:
    click_button('Add Aircraft')
    wait(w=0)
    print('Uploading data for ' + plane['ident'] + '.')
    
    pos = get_plane_id()
    set_data(pos, 'aircraftId', plane['ident'])
    set_data(pos, 'aircraftType', plane['type'])
    set_data_drop(pos, 'Standby', 'Standby')
    true_spawn_delay = round(int(plane['spawn-delay']) \
        / float(read_config_value('TIME_COMPRESSION')) \
        - int(read_config_value('TIME_OFFSET')))
    if true_spawn_delay < 0: true_spawn_delay = 0
    set_data(pos, 'spawnDelay', true_spawn_delay)
    set_data(pos, 'airportId', plane['dep'][1:])

    try:
        click_button('Create Flight Plan')
    except Exception:
        pass
    
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
    set_data(pos, 'flightplan.remarks', '/v/')
    set_data_drop(pos, 'Coordinates', 'Parking')
    set_data(pos, 'startingConditions.parking', plane['gate'])
    
    if(len(plane['push-taxiway']) != 0):
        click_button('Add Command')
        driver.find_element('name', 'aircraft[' + pos + '].presetCommands[' 
        + str(get_command_current_id(pos)) + ']') \
        .send_keys('PUSH ' + plane['push-taxiway'])
    
    if(len(plane['taxi-route']) != 0):
        click_button('Add Command')
        driver.find_element('name', 'aircraft[' + pos + '].presetCommands[' 
        + str(get_command_current_id(pos)) + ']') \
        .send_keys('TAXI ' + plane['taxi-route'])
    click_button('Done')
    
click_button('Save')
f.close()

print('Data upload to vNAS complete!')