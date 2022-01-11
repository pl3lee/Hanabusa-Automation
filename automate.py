from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import requests
import os, sys
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from random import randint
from fake_useragent import UserAgent
import shutil
from pathlib import Path

# Lists of states, cities, and areas available for uploading. Used for checking.
states = ["Chiba", "Kanagawa", "Saitama", "Tokyo"]
cities = ["23 wards", "Akiruno", "Akishima", "Asaka", "Chiba", "Chofu", "Fuchu", "Fujimi", "Fujimino", "Funabashi", "Fussa", "Hachioji", "Hamura", "Higashikurume", "Higashimurayama", "Higashiyamato", "Hino", "Ichikawa", "Inagi", "Kamagaya", "Kashiwa", "Kawagoe", "Kawaguchi", "Kawasaki", "Kiyose", "Kodaira", "Koganei", "Kokubunji", "Komae", "Koshigaya", "Kunitachi", "Machida", "Matsudo", "Misato", "Mitaka", "Miyoshi", "Musashimurayama", "Musashino", "Nagareyama", "Narashino", "Nishitokyo", "Niza", "Noda", "Ome", "Sagamihara", "Saitama", "Sakura", "Sayama", "Shiki", "Soka", "Tachikawa", "Tama", "Toda", "Tokorozawa", "Urayasu", "Wako", "Warabi", "Yachiyo", "Yashio", "Yokohama", "Yoshikawa", "Yotsukaido"]
areas = ["Adachi", "Aoba", "Arakawa", "Asahi", "Asao", "Bunkyo", "Chiyoda", "Chuo", "Edogawa", "Hanamigawa", "Hodogaya", "Inage", "Isogo", "Itabashi", "Izumi", "Kanagawa", "Kanazawa", "Katsushika", "Kawasaki", "Kita", "Kohoku", "Konan", "Koto", "Meguro", "Midori", "Mihama", "Minami", "Minato", "Minuma", "Miyamae", "Naka", "Nakahara", "Nakano", "Nerima", "Nishi", "Omiya", "Ota", "Saiwai", "Sakae", "Sakura", "Setagaya", "Seya", "Shibuya", "Shinagawa", "Shinjuku", "Suginami", "Sumida", "Taito", "Takatsu", "Tama", "Toshima", "Totsuka", "Tsuzuki", "Tsurumi", "Urawa", "Wakaba"]
username = "random"
password = "random"

class Property:
    def __init__(self, url, state, city, area, dlist):
        self.url = url
        self.state = state
        self.city = city
        self.area = area
        self.dlist = dlist
    def print_dlist(self):
        print(f"Images: {self.dllist}")
    def print_url(self):
        print(self.url)
    def print_prop(self):
        print(f"Address: {self.english_address}")
        print(f"Price: ¥{self.price}")
        print(f"Layout: {self.layout}")


# Automatically scrapes property details from website. Returns a Property.
# prop: class Property
# scrapecounter: integer
def scrape(prop, scrapecounter):
    ua = UserAgent()
    headers = {"User-Agent" : ua.random}

    
    source = requests.get(prop.url, headers = headers).text
    soup = BeautifulSoup(source, 'lxml')
    mainbody = soup.find('body')

    
    


    # First section
    propertyspecs = mainbody.find('div', class_='bukkenSpec')
    pricediv = propertyspecs.find('div', class_='line')
    # Gets the price of property
    price = pricediv.dd.text
    pricelist = []
    # Puts price in pricelist
    for char in price:
        if char.isdigit() or char == ".":
            pricelist.append(char)
    # Makes price a float
    price = float("".join(pricelist))
    # Adds 4 zeros to the back
    price *= 10000
    price = int(price)
    prop.price = price

    # Gets traffic info of property
    alltraffic = propertyspecs.find('dd', id='chk-bkc-fulltraffic')
    traffics = []
    # Gets traffic info and puts it in traffics
    for i in alltraffic.find_all('p', class_='traffic'):
        traffics.append(i.text)
    # Determines the shortest time
    for item in range(len(traffics)):
        if "バス" not in traffics[item]:
            fastest_traffic = traffics[item]
            break
    trafficlist = list(fastest_traffic)
    trafficnumber = []
    # Extracts the number of minutes
    for char in trafficlist:
        if char.isdigit():
            trafficnumber.append(str(char))
    # Turns it into an integer
    trafficnumber = int("".join(trafficnumber))
    prop.trafficnumber = trafficnumber

    # Gets the address
    address = propertyspecs.find('dd', id='chk-bkc-fulladdress').text.strip()
    prop.address = address

    # Gets the year built
    year = propertyspecs.find('dd', id='chk-bkc-kenchikudate').text.strip()
    # Gets the first 4 charaters, they are digits of the year
    year = year[0:4]
    prop.year = year

    # Gets the house area/size
    housearea = propertyspecs.find('dd', id='chk-bkc-housearea').text.strip()
    harea = ""
    # Extracts the numbers in area
    for char in housearea:
        if char == "m":
            break
        elif char != "m":
            harea += char
    prop.harea = harea

    # Gets the land area
    landarea = propertyspecs.find('dd', id='chk-bkc-landarea').text.strip()
    larea = ""
    # Extracts the number in area
    for char in landarea:
        if char == "m":
            break
        elif char != "m":
            larea += char
    prop.larea = larea

    # Gets the layout
    layout = propertyspecs.find('dd', id='chk-bkc-marodi').text.strip()[0:5].strip()
    prop.layout = layout

    # Second section
    detailedspecs = mainbody.find('div', class_='mod-bukkenSpecDetail')

    # Gets road width
    road = None
    if detailedspecs.find('td', id='chk-bkd-setsudodetail') is None:
        road = None
    else:
        road = detailedspecs.find('td', id='chk-bkd-setsudodetail').p.text.strip()
        roads = []
        ctr = 0
        while ctr < len(road):
            if road[ctr].isdigit():
                j = ctr + 1
                while road[j] != "m":
                    j += 1
                roads.append(float(road[ctr:j]))
                ctr = j
            ctr += 1
        roads = [road for road in roads if road <= 15.0]
        if len(roads) == 0:
            road = None
        else:
            road = max(roads)
            if road >= 10:
                road = round(road)
    prop.road = road
    # Gets parking spaces
    parking = None
    parkinglist = []
    if detailedspecs.find('td', id='chk-bkd-parking') is None:
        pass
    else:
        parkingspaces = detailedspecs.find('td', id='chk-bkd-parking').text.strip()
        if "台" in parkingspaces:
            for k in parkingspaces:
                if k == "台":
                    break
                elif k.isdigit():
                    parkinglist.append(k)
        if (len(parkinglist) == 0) or ("台" not in parkingspaces) or ((len(parkinglist) == 1) and (parkinglist[0] == "0")):
            parking = 0
        else:
            parking = int("".join(parkinglist))
    prop.parking = parking
    prop.parkinglist = parkinglist
    prop.english_address = "Failed"
    for t in range(2):
        try:
            gallery = soup.find('ul', class_='galleryItems prg-galleryItems')
            foldername = None
            if prop.area == "None":
                foldername = prop.city
            else:
                foldername = prop.area
            downloads_path = str(Path.home() / "Downloads")
            folderpath = os.path.join(downloads_path, f"{foldername}{scrapecounter}")
            try:
                shutil.rmtree(folderpath)
            except:
                pass
            os.mkdir(folderpath)
            images = gallery.findAll('img')
            list1 = []
            for image in images:
                list1.append(image['src'])
            ctr = 1
            for num in prop.dlist:
                fullfilename = os.path.join(folderpath, f"image{ctr}.jpg")
                urlretrieve(list1[int(num) - 1], fullfilename)
                ctr += 1
            break
        except:
            if t == 1:
                print("Error downloading pictures. Please try again.")
            else:
                pass
    return prop

# Inputs the data of prop into Hanabusa website. Returns True or False depending on whether it is successful or not.
# prop: class Property
# username: string
# password: string
def input_data(prop, username, password):
    # Inputting the data into Hanabusa website
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('log-level=3')
    browser = webdriver.Chrome(options = options)
    browser.maximize_window()
    browser.get('https://hanabusa-realty.com/wp-login.php?redirect_to=https%3A%2F%2Fhanabusa-realty.com%2Fwp-admin%2Fpost-new.php%3Fpost_type%3Dproperty&reauth=1')
    
    try_loop = 80

    # Login
    for t in range(try_loop):
        try:
            username_text = browser.find_element(By.XPATH, '//*[@id="user_login"]')
            username_text.send_keys(username)
            password_text = browser.find_element(By.XPATH, '//*[@id="user_pass"]')
            password_text.send_keys(password)
            login_button = browser.find_element(By.XPATH, '//*[@id="wp-submit"]')
            login_button.click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error logging in.")
                print(e)
                return False
    # Gets rid of intro
    for t in range(try_loop):
        try:
            ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error quitting intro.")
                print(e)
                return False

    # Opens type, status, and labels dropdown on the right
    for t in range(try_loop):
        try:
            # Type dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[4]/h2/button').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding type dropdown.")
                print(e)
                return False

    for t in range(try_loop):
        try:
            # Status dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[5]/h2/button').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding status dropdown.")
                print(e)
                return False

    for t in range(try_loop):
        try:
            # Labels dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[7]/h2/button').click()  
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding labels dropdown.")
                print(e)
                return False

    # Chooses contact info
    contact_textbox = browser.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[6]/a')
    contact_textbox.click()
    for t in range(try_loop):
        try:
            agency_info_button = browser.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/div/div[6]/div[1]/div/div/div[2]/ul/li[3]/label/input')
            agency_info_button.click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding agency info.")
                print(e)
                return False
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//*[@id="fave_property_agency"]/option[2]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding agency options.")
                print(e)
                return False

    # Inputs price, house size, land area, and year built
    browser.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[1]/a').click()
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//*[@id="fave_property_price"]').send_keys(prop.price)
            browser.find_element(By.XPATH, '//*[@id="fave_property_size"]').send_keys(prop.harea)
            browser.find_element(By.XPATH, '//*[@id="fave_property_land"]').send_keys(prop.larea)
            browser.find_element(By.XPATH, '//*[@id="fave_property_year"]').send_keys(prop.year)
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error inputting price, house size, land area, and year built.")
                print(e)
                return False

    # Chooses layout
    layoutselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_layout"]'))
    layoutselect.select_by_visible_text(prop.layout)

    # Chooses land title
    landtitleselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_land-title"]'))
    landtitleselect.select_by_value("Ownership")

    # Chooses traffic
    trafficselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_walk-to-station"]'))
    trafficselect.select_by_value(str(prop.trafficnumber) + " min")

    # Chooses road width (if applicable)
    if prop.road is not None:
        roadselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_width-of-road"]'))
        roadselect.select_by_visible_text(str(prop.road) + " m")
    
    # Chooses parking spaces (if applicable)
    if prop.parking is not None:
        if len(prop.parkinglist) == 0 or prop.parking == 0:
            parkingselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_of-parking-space"]'))
            parkingselect.select_by_value("Avail")
        else:
            parkingselect = Select(browser.find_element(By.XPATH, '//*[@id="fave_of-parking-space"]'))
            if prop.parking == 1:
                parkingselect.select_by_value(str(prop.parking) + " car")
            else:
                parkingselect.select_by_value(str(prop.parking) + " cars")

    # Checks single family home
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//label[normalize-space()="Single Family Home"]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding single family home.")
                print(e)
                return False
    
    # Checks for sale
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//label[normalize-space()="For Sale"]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding for sale.")
                print(e)
                return False

    # Checks newly built
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//label[normalize-space()="NEWLY BUILT"]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding newly built.")
                print(e)
                return False
    for t in range(try_loop):
        try:
            # State dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[8]/h2/button').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding state dropdown.")
                print(e)
                return False
    for t in range(try_loop):
        try:
            # City dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[9]/h2/button').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding city dropdown.")
                print(e)
                return False

    if propertyarea != "None":
        for t in range(try_loop):
            try:
                # Area dropdown
                browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[10]/h2/button').click()
                break
            except Exception as e:
                time.sleep(0.1)
                if t == (try_loop - 1):
                    print("Error finding area dropdown.")
                    print(e)
                    return False
    for t in range(try_loop):
        try:
            # Featured image dropdown
            browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[11]/h2/button').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding featured image dropdown.")
                print(e)
                return False


    # Checks state
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, f'//label[text()="{prop.state}"]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding state.")
                print(e)
                return False

    # Checks city
    for t in range(try_loop):
        try:
            browser.find_element(By.XPATH, '//*[@id="editor-post-taxonomies__hierarchical-terms-filter-4"]').send_keys(prop.city)
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding city.")
                print(e)
                return False
    for t in range(try_loop):
        try:
            # City checkbox container
            city_tab = browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[9]/div')
            city_tab.find_element(By.XPATH, f'.//label[normalize-space()="{prop.city}"]').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding city.")
                print(e)
                return False
    
    
    # Checks area
    if prop.area != "None":
        for t in range(try_loop):
            try:
                browser.find_element(By.XPATH, '//*[@id="editor-post-taxonomies__hierarchical-terms-filter-5"]').send_keys(prop.area)
                break
            except Exception as e:
                time.sleep(0.1)
                if t == (try_loop - 1):
                    print("Error finding area.")
                    print(e)
                    return False
        for t in range(try_loop):
            try:
                # Area checkbox container
                area_tab = browser.find_element(By.XPATH, '//*[@id="editor"]/div[1]/div[1]/div[2]/div[3]/div/div[3]/div[10]/div')
                area_tab.find_element(By.XPATH, f'.//label[normalize-space()="{prop.area}"]').click()
                break
            except Exception as e:
                time.sleep(0.1)
                if t == (try_loop - 1):
                    print("Error finding area.")
                    print(e)
                    return False
    
    # Checks property expiration, changes month and year (if necessary)
    browser.find_element(By.XPATH, '//label[normalize-space()="Enable Property Expiration"]').click()
    jpmonth = datetime.datetime.utcnow().month
    newmonth = 0
    if jpmonth + 3 > 12:
        newmonth = str(jpmonth + 3 - 12)
        newyear = str(datetime.datetime.utcnow().year + 1)
        yearselect = Select(browser.find_element(By.XPATH, '//*[@id="expirationdate_year"]'))
        yearselect.select_by_visible_text(newyear)
    else:
        newmonth = str(jpmonth + 3)
    datetime_object = datetime.datetime.strptime(newmonth, "%m")
    new_month_name = datetime_object.strftime("%B")
    monthselect = Select(browser.find_element(By.XPATH, '//*[@id="expirationdate_month"]'))
    monthselect.select_by_visible_text(new_month_name)

    # Selects map tab
    map_tab = browser.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[2]/a')
    map_tab.click()
    map_textbox = browser.find_element(By.XPATH, '//*[@id="fave_property_map_address"]')
    # Enters address
    map_textbox.send_keys(prop.address)
    
    # Finds address autocomplete item
    autocompletetext = "random"
    for t in range(try_loop):
        try:
            autocomplete = browser.find_element(By.CLASS_NAME, 'ui-menu-item')
            autocompletetext = autocomplete.find_element(By.CLASS_NAME, 'ui-menu-item-wrapper').text
            autocomplete.find_element(By.CLASS_NAME, 'ui-menu-item-wrapper').click()
            break
        except Exception as e:
            time.sleep(0.1)
            if t == (try_loop - 1):
                print("Error finding autocomplete.")
                print(e)
                return False

    # Enters autocomplete address to title
    browser.find_element(By.XPATH, '//*[@id="post-title-0"]').send_keys(autocompletetext)

    # Selects media tab
    autocomplete.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[4]/a').click()
    browser.find_element(By.XPATH, '//*[@id="houzez-property-meta-box"]/div[2]/div/div/div/div[4]/div[1]/div/div/div[2]/div/div[2]/a').click()
    browser.find_element(By.XPATH, '//*[@id="menu-item-upload"]').click()
    time.sleep(2)

    # This can be used to find the upload box in media tab, but I cannot figure out how to upload multiple images at the same time without it replacing one another.
    # uploadbox = browser.find_element(By.CLASS_NAME, 'media-modal-content')
    # uploadbox.find_element(By.TAG_NAME, 'input').send_keys("C:\\Users\\billy\\Downloads\\image (2).jpg") 
    # uploadbox.find_element(By.TAG_NAME, 'input').send_keys("C:\\Users\\billy\\Downloads\\image (1).jpg") 

    prop.english_address = autocompletetext
    return True

# Runs the scrape and input_data functions on plist. Does not return any value.
# plist: list of class Property
# username: string
# password: string
def scrape_weblist(plist, username, password):
    status = [False for i in range(len(plist))]
    print("==================================================")
    print("Uploading the following properties:")
    for website in range(len(plist)):
        print(f"{website + 1}. {plist[website].url}")
        print(f"Downloading images {plist[website].dlist}")
    print("==================================================")
    for website in range(len(plist)):
        try:
            output = scrape(plist[website], website + 1)
            result = False
            for t in range(2):
                try:
                    result = input_data(output, username, password)
                    break
                except:
                    if t == 1:
                        result = False
                    else:
                        print(f"Something went wrong with {plist[website].url}, retrying.")
            if result is True:
                print("==================================================")
                print(f"Uploading of {plist[website].url} with pictures {plist[website].dlist} successful!")
                print("==================================================")
                status[website] = True
            else:
                print("==================================================")
                print(f"Something went wrong with {plist[website].url} with pictures {plist[website].dlist}!")
                print("==================================================")
                status[website] = f"{plist[website].url} failed, please retry."
        except Exception as e:
            print("==================================================")
            print(f"Something went wrong with {plist[website].url} with pictures {plist[website].dlist}!")
            print("==================================================")
            status[website] = f"{plist[website].url} failed: {e}"
    status = [i for i in status if i is not True]
    
    if len(status) == 0:
        print("==================================================")
        print("All properties successfully uploaded!")
        print("==================================================")
    else:
        print("==================================================")
        print("Error(s) on some properties! Please retry!")
        for error_msg in range(len(status)):
            print(f"{error_msg + 1}. {status[error_msg]}")
        print("==================================================")
    sorted_plist_address = []
    sorted_plist = []
    try:
        sorted_plist_address = sorted(plist, key = lambda x: x.english_address)
    except:
        pass
    try:
        sorted_plist = sorted(sorted_plist_address, key = lambda x: x.price)
    except:
        pass
    print("==================================================")
    print("Here is a list of the chosen addresses and their corresponding layout and price in the order that you inputted, please check if they are correct and if there are any potential duplicates: ")
    for p in range(len(plist)):
        print(f"{p + 1}.")
        Property.print_prop(plist[p])
    print("==================================================")
    print("==================================================")
    print("Here is the same list, but sorted by price:")
    for p in range(len(sorted_plist)):
        print(f"{p + 1}.")
        Property.print_prop(sorted_plist[p])
    print("==================================================")

# Splits a given range. Returns a list of integers. Example: 1-5 -> [1, 2, 3, 4, 5].
# num_range: string
def split_range(num_range):
    if "-" in num_range:
        lowercounter = 0
        for char in num_range:
            if char == "-":
                break
            elif 0 <= int(char) and int(char) <= 30:
                lowercounter += 1
            else:
                return False
        lowerlimit = int(num_range[:lowercounter])
        upperlimit = int(num_range[lowercounter + 1:])
        numlist = [i for i in range(lowerlimit, upperlimit + 1)]
        return numlist 
    else:
        dummylist = []
        dummylist.append(int(num_range))
        return dummylist

# Prompts the user to select a person. Returns two strings, username and password.
def select_person():
    while True:
        print("Are you Billy or Jamie? Enter b or j.")
        person = input()
        if person.lower() == "b":
            username = 'billylee'
            password = ')RWNAHSs1iCmRvzYGpXFK83b'
            return username, password
        elif person.lower() == "j":
            username = 'mjamie'
            password = 'Jam2002^'
            return username, password
        elif person.lower() == "q":
            quit()
        else:
            print("Unknown person! Try again.")

# Checks whether answer is a predetermined command, and modifies list. For example, if answer is "r", the function empties list. Returns True if answer is "d", and returns False otherwise.
# answer: string
# list: list
def check_input_command(answer, list):
    if answer.lower() == "d":
        return True
    elif answer.lower() == "u":
        list.pop()
        return False
    elif answer.lower() == "q":
        quit()
        return False
    elif answer.lower() == "r":
        list.clear()
        return False
    elif answer.lower() == "p":
        print("==================================================")
        print("This is the current list of properties/pictures download:")
        for entry in range(len(list)):
            print(f"{entry + 1}: {list[entry]}")
        print("==================================================")
        return False
    elif answer.lower() == "e":
        print("==================================================")
        print("This is the current list of properties/pictures download:")
        for entry in range(len(list)):
            print(f"{entry + 1}: {list[entry]}")
        print("Which one do you want to delete? (Enter a number)")
        print("==================================================")
        ans = None
        while True:
            ans = input()
            if ans.isdigit() == False:
                print("Invalid selection, please try again.")
            elif int(ans) > len(list):
                print("Invalid selection, please try again.")
            elif int(ans) <= 0:
                print("Invalid selection, please try again.")
            else:
                break
        deleted = list.pop(int(ans) - 1)
        print(f"Deleted {deleted} from list!")
        return False
    else:
        list.append(answer)
        return False

# Prompts the user to input state, city, and area. Returns three strings, propertystate, propertycity, and propertyarea.
def input_area():
    while True:
        print("Please enter the state: (chiba/kanagawa/saitama/tokyo)")
        propertystate = input()
        propertystate = propertystate.capitalize()
        if propertystate == "Q":
            quit()
        elif propertystate not in states:
            print(f"Cannot find {propertystate}! Please try again.")
        else:
            break
    while True:
        print("Please enter the city: (23 wards/chiba/inagi...)")
        propertycity = input()
        propertycity = propertycity.capitalize()
        if propertycity == "Q":
            quit()
        if propertycity not in cities:
            print(f"Cannot find {propertycity}! Please try again.")
        else:
            break
    while True:
        print("Please enter the area: (naka/nishi/midori...)(If no area then enter none)")
        propertyarea = input()
        propertyarea = propertyarea.capitalize()
        if propertyarea == "Q":
            quit()
        if propertyarea not in areas:
            if propertyarea != "None":
                print(f"Cannot find {propertyarea}! Please try again.")
            else:
                break
        else:
            break
    return propertystate, propertycity, propertyarea

# Prompts the user to input a series of URLs for web scraping and modifies urllist accordingly. Does not return a value.
# urllist: list of strings
def input_weblist(urllist):
    print("Please enter website URLs, one at a time, d when done.")
    print("Here is a list of commands that you can perform:")
    print("d: done")
    print("q: quit")
    print("r: reset list")
    print("u: delete previous entry")
    print("p: print list")
    print("e: edit list")
    while True:
        answer = input()
        input_result = check_input_command(answer, urllist)
        if input_result is True:
            break

# Prompts the user to input a series of strings corresponding to the indices of images that the user would like to download and modifies dlist accordingly. Does not return a value.
def input_dlist(dlist):
    print("Please enter the numbers of the pictures that you would like to download, separated with a comma and a space. For example, if you would like to download pictures 1, 2, 3, 7, 9, 10, 11, 12, 13, please input '1-3, 7, 9-13' then press enter. Repeat this process for each property. Enter d when done.")
    print("Here is a list of commands that you can perform:")
    print("d: done")
    print("q: quit")
    print("r: reset list")
    print("u: delete previous entry")
    print("p: print list")
    print("e: edit list")
    while True:
        usrinput = input()
        result = check_input_command(usrinput, dlist)
        if result is True:
            break
    for i in range(len(dlist)):
        dlist[i] = dlist[i].split(", ")
        split_list = []
        for k in range(len(dlist[i])):
            split_list = split_list + split_range(dlist[i][k])
        dlist[i] = split_list

# Prompts the user to input a series of URLs and strings, creates and returns a list of Property accordingly.
# state: string
# city: string
# area: string
def create_property_list(state, city, area):
    plist = []
    urllist = []
    dlist = []
    input_weblist(urllist)
    input_dlist(dlist)
    while len(urllist) != len(dlist):
        print("Number of URLs does not correspond to the number of entries of selected images!")
        print(f"You have input {len(urllist)} URLs:")
        for url in range(len(urllist)):
            print(f"{url + 1}. {urllist[url]}")
        print(f"You have input {len(dlist)} entries of selected images:")
        for dl in range(len(dlist)):
            print(f"{dl + 1}. {dlist[dl]}")
        print("Which of the above do you want to reinput? (1/2)")
        while True:
            answer = input()
            if answer == "q":
                quit()
            elif answer == "1":
                urllist = []
                input_weblist(urllist)
                break
            elif answer == "2":
                dlist = []
                input_dlist(dlist)
                break
            else:
                print("Invalid choice! Please enter 1 or 2")
    for i in range(len(urllist)):
        tempproperty = Property(urllist[i], state, city, area, dlist[i])
        plist.append(tempproperty)
    return plist

# Deletes input.txt if it is present.
try:
    os.remove("input.txt")
except:
    pass

up_state = False
location_state = False

print("Welcome! You can enter q at any step to quit.")
# Keeps the program running after it is done
while True:
    if up_state == False:
        username, password = select_person()
        up_state = True
    if location_state == False:
        propertystate, propertycity, propertyarea = input_area()
        location_state = True
    plist = create_property_list(propertystate, propertycity, propertyarea)
    scrape_weblist(plist, username, password)
    print("Done! Would you like to quit? (y/n)")
    answer = input()
    if answer.lower() == "y":
        quit()
    print("Would you like to continue with the same area? (y/n)")
    answer = input()
    if answer.lower() == "y":
        location_state = True
    else:
        location_state = False
    print("Would you like to login to another account? (y/n)")
    answer = input()
    if answer.lower() == "y":
        up_state = False
    else:
        up_state = True
        
    









