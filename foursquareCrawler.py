# -*- encoding: utf-8 -*-
import io
import sys
import requests
from bs4 import BeautifulSoup
import xlrd
import xlwt
import time
import random

# from tools.webtools import headerTrans

#get hospitals according to the address
def getHospitals(adr="New York"):
    param={"mode":"typed","near":adr,"q":"hospital"}
    headers={'Upgrade-Insecure-Requests': '1', 'Referer': 'https', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv', 'Cookie': 'bbhive=XJQMDX43CFNYXY3DPO3WV5W3AO4K01%3A%3A1551607069; PixelDensity=1; XSESSIONID=fsan408084~5qa23xj1pt5a118bfmiirjgm; __utma=51454142.165688144.1488535071.1488535071.1488535071.1; __utmb=51454142.1.10.1488535071; __utmc=51454142; __utmz=51454142.1488535071.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1', 'Connection': 'keep-alive', 'Host': 'foursquare.com', 'Accept-Encoding': 'gzip, deflate, br'}
    r=requests.get("https://foursquare.com/explore",params=param,headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    urlPool=[]
    for item in soup.find_all("div",attrs={"class":"contentHolder"}):
        urlPool.append(item.find("div",attrs={"class":"venueName"}).find("a")["href"])
    return urlPool

#get hospital details according to the url
def getHospitalDetails(hosUrl):
    hosUrl="https://foursquare.com"+hosUrl
    headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv', 'Host': 'foursquare.com', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Cookie': 'bbhive=XJQMDX43CFNYXY3DPO3WV5W3AO4K01%3A%3A1551607069; PixelDensity=1; XSESSIONID=fsan408084~5qa23xj1pt5a118bfmiirjgm; __utma=51454142.165688144.1488535071.1488535071.1488536997.2; __utmc=51454142; __utmz=51454142.1488536997.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmb=51454142.10.10.1488536997; lc=%7B%22lat%22%3A40.747296%2C%22lng%22%3A-73.975591%2C%22loc%22%3A%22Murray%20Hill%22%2C%22cc%22%3A%22US%22%2C%22longGeoId%22%3A%227650%22%7D; _ga=GA1.2.165688144.1488535071; __gads=ID=59c5d8350720dfae', 'Upgrade-Insecure-Requests': '1', 'Referer': 'https', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0'}
    r=requests.get(hosUrl,headers=headers)
    soup=BeautifulSoup(r.text,"lxml")
    detailBlock=soup.find("div",attrs={"class":"venueDetails"})
    detail={}

    detail["name"]=detailBlock.find("div",attrs={"class","venueName"}).string

    address=''
    for ad in detailBlock.find("div",attrs={"class":"venueAddress"}).\
        find("div",attrs={"class":"adr"}).find_all("span"):
        address+=ad.string+' '
    detail["address"]=address

    try:
        detail["tele"]=detailBlock.find("span",attrs={"class":"tel"}).string
        detail["web"]=detailBlock.find("a",attrs={"class":"url"})["href"]
    except:
        print("no telephone, no official website")

    try:
        detail["fb"] = detailBlock.find("a", attrs={"class": "facebookPageLink"})["href"]
        detail["tw"] = detailBlock.find("a", attrs={"class": "twitterPageLink"})["href"]
    except:
        print("no facebook, no twitter")
    return detail
    # for item in soup.find("div",attrs={"class":"venueDetails"}).find_all("div",attrs={"class":"venueRowContent"}):
    #     print(item)



def getCounty():
    #list of counties in the united states
    r=requests.get("https://en.wikipedia.org/wiki/List_of_United_States_counties_and_county_equivalents")


#main program
workbook=xlwt.Workbook()
worksheet=workbook.add_sheet("sheet")

index=0
for hos in getHospitals():

    detail=getHospitalDetails(hos)
    time.sleep(random.randint(2,3))

    #print(detail.get('fb',0))
    info=['name','web','tele','address','fb','tw']
    for i in range(len(info)):
        worksheet.write(index,i,str(detail.get(info[i],'')))
    index+=1

workbook.save("ir/foursquare.xls")
