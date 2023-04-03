# IMPORTS AND COMMON FUNCTIONS
import imp, os, subprocess, sys, time, random, pathlib, csv, re
try:
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

downloads_folder = str(pathlib.Path.home() / 'Downloads')

def read_config_value(key):
    config = open(downloads_folder + '\\FAST.txt', 'r').read()
    if key + '=' in config:
        return config.split(key + '=')[1].split('\n')[0]
    return 'NULL'

def between(text, start, end):
    try: 
        return text.split(start)[1].split(end)[0]
    except Exception:
        return ''
    
def click_button(text):
    driver.find_element('xpath', 
        '//button[contains(text(), \'' + text + '\')]').click()

# WEB DRIVER OPEN
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install());
driver.minimize_window()
os.system('cls');

# GENERATE AIRCRAFT URLs
url = 'https://flightaware.com/live/airport/' \
    + read_config_value('AIRPORT') + '/scheduled'

driver.get(url)

driver.find_element('name', 'flightaware_username') \
    .send_keys(read_config_value('FLIGHTAWARE_USER'))
driver.find_element('name', 'flightaware_password') \
    .send_keys(read_config_value('FLIGHTAWARE_PASS'))
driver.find_element('id', 'loginButton').click()
time.sleep(5)

plane_urls = driver.find_elements('xpath', '//a[@href]')
filtered_urls = list()
for plane_url in plane_urls:
    href = plane_url.get_attribute('href')
    if 'live/flight/id/' in href:
        filtered_urls.append(href)

# CREATE AIRCRAFT DATA FILE
s = 'ident,type,dep,arr,alt,speed,route,spawn-delay,gate,' \
    + 'push-taxiway,taxi-route'
init_spawn_delay = 0

def get_plane_info(source):
    temp_text = source[source.rindex(r'"route"') - 3000:
                       source.rindex(r'"route"') + 1500]
    global init_spawn_delay

    ident = between(temp_text, r'"displayIdent":"', r'"')
    flight_plan = between(temp_text, r'"flightPlan":', r'"fuelBurn"')
    alt = between(flight_plan, r'"altitude":', r',') + '00'
    speed = between(flight_plan, r'"speed":', r',')
    route = between(flight_plan, r'"route":"', r'",').replace(',', '')
    delay = int(between(flight_plan, r'departure":', r',"ete"'))
    spawn_delay = 0 if init_spawn_delay == 0 else delay - init_spawn_delay
    dep = between(source, r'name="origin" content="', r'"')
    arr = between(source, r'name="destination" content="', r'"')
    acft = between(source, r'name="aircrafttype" content="', r'"')
    gate = 'UNKN' if not r'","gate":"' in source \
        else between(source, dep + r'","gate":"', r'"')
    
    if init_spawn_delay == 0: init_spawn_delay = delay

    return ','.join([ident, acft, dep, arr, alt, speed, route, \
                     str(spawn_delay), gate, '', ''])

for filtered_url in filtered_urls:
    driver.get(filtered_url)
    plane = get_plane_info(driver.page_source)
    s += '\n' + plane
    print(plane.split(',')[0] + '\t' + plane.split(',')[2] + '-' \
          + plane.split(',')[3])
    time.sleep(random.uniform(1, 5))
    
with open(downloads_folder + '\\' + s.split('\n')[1].split(',')[2][1:] \
          + '_DEP_' + time.strftime('%y%m%d-%H%M', time.gmtime()) \
          + '.csv', 'w') as f:
    f.write(s)
    
time.sleep(10)
driver.quit()