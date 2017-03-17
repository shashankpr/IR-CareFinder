# -*- encoding: utf-8 -*-
import time
import random
import foursquare
import math
import openpyxl
import matplotlib.pyplot as plt

#order: northeast, southwest.

#convert string to coordinate
def str2coor(coorStr):
    coorData=[]
    for item in coorStr:
        tmptup=[]
        for coor in item.split(','):
            tmptup.append(float(coor.strip()))

        coorData.append(tmptup)

    return coorData

#convert coordinate to string
def coor2str(coor):
    return [str(coor[0]),str(coor[1])]

def extendArea(coor,step):
    vdis=math.ceil(math.fabs((coor[0][0]-coor[1][0])/step))
    hdis=math.ceil(math.fabs((coor[0][1]-coor[1][1])/step))
    return [vdis,hdis]



def getHospitalDetails(coorStr,step=0.1):
    client = foursquare.Foursquare(client_id='3MYPVCD3D3MT0R0IRFQNT4AG11JS3UOG3BLN35OFTI5NTVMO',
                                   client_secret='1A4PZTRJU5QUBRSNCGYAPFVTUBOVO5Z0WLJJMTONNS254K5M')
    coor=str2coor(coorStr)

    exstep=extendArea(coor,step)#number of steps in two direction (vertical, horizontal)

    featureSeq=['url','name','id','location','contact']
    locSeq=['formattedAddress','lat','lng'] #subsection of location
    conSeq=['formattedPhone','facebookName','twitter'] #subsection of contact information


    workbook=openpyxl.Workbook(write_only=True)
    worksheet = workbook.create_sheet()

    ######
    xSeq=[]
    ySeq=[]
    xxSeq=[]
    yySeq=[]
    ######

    for i in range(exstep[0]):
        for j in range(exstep[1]):
            nepoint=str([round(coor[0][0]-i*step,2),round(coor[0][1]-j*step,2)])[1:-2]
            swpoint=str([round(coor[0][0]-step*(i+1),2),round(coor[0][1]-step*(j+1),2)])[1:-2]
            print(nepoint,swpoint)

            xSeq.append(round(coor[0][0]-i*step,2))
            ySeq.append(round(coor[0][1]-j*step,2))
            xxSeq.append(round(coor[0][0]-step*(i+1),2))
            yySeq.append(round(coor[0][1]-step*(j+1),2))


            results=client.venues.search(params={'query':'hospitals','intent':'browse',
                                               'ne':nepoint,
                                               'sw':swpoint})
            print(len(results['venues']))
            for item in results['venues']:

                tmpDict={}
                tmpSeq=[]

                #convert from tuples to dictionary
                for chara in item.items():
                    tmpDict[chara[0]]=chara[1]

                #get information of interest
                for fea in featureSeq:
                    if fea=='location':
                        tmpLoc=tmpDict.get(fea,'')
                        for ffea in locSeq:
                            if ffea=='formattedAddress':
                                tmpAd=tmpLoc.get(ffea,'')
                                tmpSeq.append(" ".join(tmpAd))
                                continue
                            tmpSeq.append(tmpLoc.get(ffea,''))
                        continue
                    if fea=='contact':
                        tmpCon=tmpDict.get(fea,'')
                        for ffea in conSeq:
                            tmpSeq.append(tmpCon.get(ffea,''))
                        continue
                    tmpSeq.append(tmpDict.get(fea,''))
                print(tmpSeq[1])
                worksheet.append(tmpSeq)

        #     break
        # break

            time.sleep(random.randint(2,3))
    workbook.save("foursquare/data.xlsx")
    plt.scatter(xSeq,ySeq)
    plt.scatter(xxSeq,yySeq)
    plt.show()

targetSquare=["40.797480, -73.858479","40.645527, -74.144426"] #new york city

getHospitalDetails(targetSquare,step=0.05)
