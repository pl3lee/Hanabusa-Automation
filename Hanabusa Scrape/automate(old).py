from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import datetime
from selenium.webdriver.chrome.options import Options

# lists of states, cities, and areas
states = ["Chiba", "Kanagawa", "Saitama", "Tokyo"]
cities = ["23 wards", "Akiruno", "Akishima", "Asaka", "Chiba", "Chofu", "Fuchu", "Fujimi", "Fujimino", "Funabashi", "Fussa", "Hachioji", "Hamura", "Higashikurume", "Higashimurayama", "Higashiyamato", "Hino", "Ichikawa", "Inagi", "Kamagaya", "Kashiwa", "Kawagoe", "Kawaguchi", "Kawasaki", "Kiyose", "Kodaira", "Koganei", "Kokubunji", "Komae", "Koshigaya", "Kunitachi", "Machida", "Matsudo", "Misato", "Mitaka", "Miyoshi", "Musashimurayama", "Musashino", "Nagareyama", "Narashino", "Nishitokyo", "Niza", "Noda", "Ome", "Sagamihara", "Saitama", "Sakura", "Sayama", "Shiki", "Soka", "Tachikawa", "Tama", "Toda", "Tokorozawa", "Urayasu", "Wako", "Warabi", "Yachiyo", "Yashio", "Yokohama", "Yoshikawa", "Yotsukaido"]
areas = ["Adachi", "Aoba", "Arakawa", "Asahi", "Asao", "Bunkyo", "Chiyoda", "Chuo", "Edogawa", "Hanamigawa", "Hodogaya", "Inage", "Isogo", "Itabashi", "Izumi", "Kanagawa", "Kanazawa", "Katsushika", "Kawasaki", "Kita", "Kohoku", "Konan", "Koto", "Meguro", "Midori", "Mihama", "Minami", "Minato", "Minuma", "Miyamae", "Naka", "Nakahara", "Nakano", "Nerima", "Nishi", "Omiya", "Ota", "Saiwai", "Sakae", "Sakura", "Setagaya", "Seya", "Shibuya", "Shinagawa", "Shinjuku", "Suginami", "Sumida", "Taito", "Takatsu", "Tama", "Toshima", "Totsuka", "Tsuduki", "Tsurumi", "Urawa", "Wakaba"]

# Automatically scrapes property details from website, and inputs the details into Hanabusa website
def scrape(website, username, password, propertystate, propertycity, propertyarea):
    # opens a new input.txt file
    source = requests.get(website).text
    file = open("input.txt", "w")
    soup = BeautifulSoup(source, 'lxml')
    mainbody = soup.find('body')

    # first section
    propertyspecs = mainbody.find('div', class_='bukkenSpec')
    pricediv = propertyspecs.find('div', class_='line')

    # gets the price of property
    price = pricediv.dd.text
    pricelist = []
    # puts price in pricelist
    for char in price:
        if char.isdigit() or char == ".":
            pricelist.append(char)
    # makes price a float
    price = float("".join(pricelist))
    # adds 4 zeros to the back
    price *= 10000
    price = int(price)
    file.write(f"{price}\n")

    # gets traffic info of property
    alltraffic = propertyspecs.find('dd', id='chk-bkc-fulltraffic')
    traffics = []
    # gets traffic info and puts it in traffics
    for i in alltraffic.find_all('p', class_='traffic'):
        traffics.append(i.text)
    # determines the shortest time
    for item in range(len(traffics)):
        if "バス" not in traffics[item]:
            fastest_traffic = traffics[item]
            break
    trafficlist = list(fastest_traffic)
    trafficnumber = []
    # extracts the number of minutes
    for char in trafficlist:
        if char.isdigit():
            trafficnumber.append(str(char))
    # turns it into an integer
    trafficnumber = int("".join(trafficnumber))
    file.write(f"{trafficnumber}\n")
    file.close()

    # gets the address
    file = open('input.txt', 'a',encoding='utf8')
    address = propertyspecs.find('dd', id='chk-bkc-fulladdress').text.strip()
    file.write(f"{address}\n")
    file.close()

    # gets the year built
    file = open('input.txt', 'a')
    year = propertyspecs.find('dd', id='chk-bkc-kenchikudate').text.strip()
    # gets the first 4 charaters, they are digits of the year
    year = year[0:4]
    file.write(f"{year}\n")

    # gets the house area/size
    housearea = propertyspecs.find('dd', id='chk-bkc-housearea').text.strip()
    harea = ""
    # extracts the numbers in area
    for char in housearea:
        if char == "m":
            break
        elif char != "m":
            harea += char
    file.write(f"{harea}\n")

    #gets the land area
    landarea = propertyspecs.find('dd', id='chk-bkc-landarea').text.strip()
    larea = ""
    # extracts the number in area
    for char in landarea:
        if char == "m":
            break
        elif char != "m":
            larea += char
    file.write(f"{larea}\n")

    # gets the layout
    layout = propertyspecs.find('dd', id='chk-bkc-marodi').text.strip()[0:5].strip()
    file.write(f"{layout}\n")

    # second section
    detailedspecs = mainbody.find('div', class_='mod-bukkenSpecDetail')

    # gets road width
    road = None
    if detailedspecs.find('td', id='chk-bkd-setsudodetail') is None:
        file.write("No Road\n")
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
        roads = [road for road in roads if road <= 8.0 or road == 15.0]
        if len(roads) == 0:
            file.write("No Road\n")
        else:
            road = max(roads)
        file.write(f"{road}\n")
            
    # gets parking spaces
    parking = None
    parkinglist = []
    if detailedspecs.find('td', id='chk-bkd-parking') is None:
        file.write("No Parking")
    else:
        parkingspaces = detailedspecs.find('td', id='chk-bkd-parking').text.strip()
        for k in parkingspaces:
            if k.isdigit():
                parkinglist.append(k)
        if len(parkinglist) == 0:
            file.write("Parking Available\n")
            parking = 0
        else:
            parking = int("".join(parkinglist))
            file.write(f"{parking}\n")
    file.close()

    # Inputting the data into Hanabusa website
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(chrome_options = options)
    browser.get('https://hanabusa-realty.com/wp-login.php?redirect_to=https%3A%2F%2Fhanabusa-realty.com%2Fwp-admin%2Fpost-new.php%3Fpost_type%3Dproperty&reauth=1')
    time.sleep(2)

    # login
    username_text = browser.find_element_by_xpath('//*[@id="user_login"]')
    username_text.send_keys(username)
    password_text = browser.find_element_by_xpath('//*[@id="user_pass"]')
    password_text.send_keys(password)
    login_button = browser.find_element_by_xpath('//*[@id="wp-submit"]')
    login_button.click()
    time.sleep(2)

    # gets rid of intro
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()

    # enters address
    map_tab = browser.find_element_by_xpath('//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[2]/a')
    map_tab.click()
    map_textbox = browser.find_element_by_xpath('//*[@id="fave_property_map_address"]')
    map_textbox.send_keys(address)

    # chooses contact info
    contact_textbox = browser.find_element_by_xpath('//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[6]/a')
    contact_textbox.click()
    agency_info_button = browser.find_element_by_xpath('//*[@id="houzez-property-meta-box"]/div[2]/div/div/div/div[6]/div[1]/div/div/div[2]/ul/li[3]/label/input')
    agency_info_button.click()
    browser.find_element_by_xpath('//*[@id="fave_property_agency"]/option[2]').click()

    # inputs price, house size, land area, and year built
    browser.find_element_by_xpath('//*[@id="houzez-property-meta-box"]/div[2]/div/div/ul/li[1]/a').click()
    browser.find_element_by_xpath('//*[@id="fave_property_price"]').send_keys(price)
    browser.find_element_by_xpath('//*[@id="fave_property_size"]').send_keys(harea)
    browser.find_element_by_xpath('//*[@id="fave_property_land"]').send_keys(larea)
    browser.find_element_by_xpath('//*[@id="fave_property_year"]').send_keys(year)

    # chooses layout
    layoutselect = Select(browser.find_element_by_xpath('//*[@id="fave_layout"]'))
    layoutselect.select_by_visible_text(layout)

    # chooses land title
    landtitleselect = Select(browser.find_element_by_xpath('//*[@id="fave_land-title"]'))
    landtitleselect.select_by_value("Ownership")

    # chooses traffic
    trafficselect = Select(browser.find_element_by_xpath('//*[@id="fave_walk-to-station"]'))
    trafficselect.select_by_value(str(trafficnumber) + " min")

    # chooses road width (if applicable)
    if road is not None:
        roadselect = Select(browser.find_element_by_xpath('//*[@id="fave_width-of-road"]'))
        roadselect.select_by_visible_text(str(road) + " m")
    
    # chooses parking spaces (if applicable)
    if parking is not None:
        if len(parkinglist) == 0:
            parkingselect = Select(browser.find_element_by_xpath('//*[@id="fave_of-parking-space"]'))
            parkingselect.select_by_value("Avail")
        else:
            parkingselect = Select(browser.find_element_by_xpath('//*[@id="fave_of-parking-space"]'))
            if parking == 1:
                parkingselect.select_by_value(str(parking) + " car")
            else:
                parkingselect.select_by_value(str(parking) + " cars")

    # opens all the dropdown menus on the right
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[3]/h2/button').click() #type dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[4]/h2/button').click() #status dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[6]/h2/button').click() #labels dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[7]/h2/button').click() #state dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[8]/h2/button').click() #city dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[9]/h2/button').click() #area dropdown
    browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[10]/h2/button').click() #featured image dropdown
    time.sleep(2)

    # checks single family home
    browser.find_element_by_xpath('//label[normalize-space()="Single Family Home"]').click()
    
    # checks for sale
    browser.find_element_by_xpath('//label[normalize-space()="For Sale"]').click()

    # checks newly built
    browser.find_element_by_xpath('//label[normalize-space()="NEWLY BUILT"]').click()

    # checks state
    browser.find_element_by_xpath(f'//label[text()="{propertystate}"]').click()

    # checks city
    city_tab = browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[8]/div') #city tab
    city_tab.find_element_by_xpath(f'.//label[normalize-space()="{propertycity}"]').click()
    
    # checks area
    if propertyarea != "None":
        area_tab = browser.find_element_by_xpath('//*[@id="editor"]/div[1]/div[1]/div[2]/div[2]/div/div[3]/div[9]/div') #area tab
        area_tab.find_element_by_xpath(f'.//label[normalize-space()="{propertyarea}"]').click()
    
    # checks property expiration, changes month and year (if necessary)
    browser.find_element_by_xpath('//label[normalize-space()="Enable Property Expiration"]').click()
    jpmonth = datetime.datetime.utcnow().month
    newmonth = 0
    if jpmonth + 3 > 12:
        newmonth = str(jpmonth + 3 - 12)
        newyear = str(datetime.datetime.utcnow().year + 1)
        yearselect = Select(browser.find_element_by_xpath('//*[@id="expirationdate_year"]'))
        yearselect.select_by_visible_text(newyear)
    else:
        newmonth = str(jpmonth + 3)
    datetime_object = datetime.datetime.strptime(newmonth, "%m")
    new_month_name = datetime_object.strftime("%B")
    monthselect = Select(browser.find_element_by_xpath('//*[@id="expirationdate_month"]'))
    monthselect.select_by_visible_text(new_month_name)

    # selects map tab
    map_tab.click()




username = "random"
password = "random"
while True:
    print("Hello! Are you Billy or Jamie? Enter b or j.")
    person = input()
    if person.lower() == "b":
        username = 'billylee'
        password = ')RWNAHSs1iCmRvzYGpXFK83b'
        break
    elif person.lower() == "j":
        username = 'mjamie'
        password = 'Jam2002^'
        break
    else:
        print("Unknown person! Try again.")
print("Please enter the state: (chiba/kanagawa/saitama/tokyo)")
propertystate = input()
propertystate = propertystate.capitalize()
print("Please enter the city: (23 wards/chiba/inagi...)")
propertycity = input()
propertycity = propertycity.capitalize()
print("Please enter the area: (naka/nishi/midori...)(If no area then enter none)")
propertyarea = input()
propertyarea = propertyarea.capitalize()
    
while True:
    print("Please enter the website: q to quit")
    web = input()
    if web.lower() == "q":
        quit()
    try:
        scrape(web, username, password, propertystate, propertycity, propertyarea)
        print("Success! Results are stored in input.txt file.")
        #os.startfile('input.txt')
    except Exception as e:
        print("Something went wrong! Read error message below:")
        print(e)







