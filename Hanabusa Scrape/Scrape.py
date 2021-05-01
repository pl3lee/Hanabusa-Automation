from bs4 import BeautifulSoup
import requests
import os

#website = 'https://www.homes.co.jp/kodate/b-74250025966/'/
def scrape(website):
    source = requests.get(website).text
    file = open("input.txt", "w")

    soup = BeautifulSoup(source, 'lxml')
    #print(soup.prettify())

    mainbody = soup.find('body')
    #propertyspecs = mainbody.find('div', id='contents')
    propertyspecs = mainbody.find('div', class_='bukkenSpec')


    pricediv = propertyspecs.find('div', class_='line')
    #print(pricediv.prettify())
    price = pricediv.dd.text
    #print(price)
    pricelist = []
    for char in price:
        if char.isdigit() or char == ".":
            pricelist.append(char)
    #print(pricelist)
    pricelen = len(pricelist)
    price = float("".join(pricelist))
    price *= 10000

    price = int(price)
    #print(price)
    #file.write(f"Price: {price}\n")
    file.write(f"{price}\n")




    alltraffic = propertyspecs.find('dd', id='chk-bkc-fulltraffic')
    #print(alltraffic)
    #print(alltraffic.p)
    traffics = []
    for i in alltraffic.find_all('p', class_='traffic'):
        traffics.append(i.text)
        #print(i.text)
    #print(traffics)

    for item in range(len(traffics)):
        if "バス" not in traffics[item]:
            fastest_traffic = traffics[item]
            break
    #print(fastest_traffic)
    trafficlist = list(fastest_traffic)
    trafficnumber = []
    for char in trafficlist:
        if char.isdigit():
            trafficnumber.append(str(char))
    trafficnumber = int("".join(trafficnumber))
    #print(trafficnumber)
    #file.write(f"Traffic: {trafficnumber}\n")
    file.write(f"{trafficnumber}\n")
    file.close()


    file = open('input.txt', 'a',encoding='utf8')
    address = propertyspecs.find('dd', id='chk-bkc-fulladdress').text.strip()
    #print(address)
    #file.write(f"Address: {address}\n")
    file.write(f"{address}\n")
    file.close()

    file = open('input.txt', 'a')
    year = propertyspecs.find('dd', id='chk-bkc-kenchikudate').text.strip()
    year = year[0:4]
    #print(year)
    #file.write(f"Year built: {year}\n")
    file.write(f"{year}\n")

    housearea = propertyspecs.find('dd', id='chk-bkc-housearea').text.strip()
    harea = ""
    for char in housearea:
        if char == "m":
            break
        elif char != "m":
            harea += char
    #print(harea)
    #file.write(f"House Area: {harea}\n")
    file.write(f"{harea}\n")

    landarea = propertyspecs.find('dd', id='chk-bkc-landarea').text.strip()
    larea = ""
    for char in landarea:
        if char == "m":
            break
        elif char != "m":
            larea += char
    #print(larea)
    #file.write(f"Land Area: {larea}\n")
    file.write(f"{larea}\n")

    layout = propertyspecs.find('dd', id='chk-bkc-marodi').text.strip()[0:5].strip()
    #print(layout)
    #file.write(f"Layout: {layout}\n")
    file.write(f"{layout}\n")


    detailedspecs = mainbody.find('div', class_='mod-bukkenSpecDetail')

    
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
        if len(roads) == 0:
            file.write("No Road\n")
        else:
            road = max(roads)
        #print(road)
        #file.write(f"Road Width: {road}\n")
        file.write(f"{road}\n")
            

    
    if detailedspecs.find('td', id='chk-bkd-parking') is None:
        file.write("No Parking")
    else:
        parkingspaces = detailedspecs.find('td', id='chk-bkd-parking').text.strip()
        parking = []
        for k in parkingspaces:
            if k.isdigit():
                parking.append(k)
        if len(parking) == 0:
            file.write("Parking Available\n")
        else:
            parking = int("".join(parking))
            #file.write(f"Parking Spaces: {parking}\n")
            file.write(f"{parking}\n")

    #print(parking)
    file.close()
while True:
    print("Please enter the website: q to quit")
    web = input()
    if web.lower() == "q":
        quit()
    try:
        scrape(web)
        print("Success")
        os.startfile('input.txt')
    except:
        print("Website incorrect")
