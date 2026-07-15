from celery import shared_task
from homepage.models import Product as productModel
@shared_task
def storeProductPrice():
    allProducts = productModel.objects.all()
    import datetime
    KEY = ""
    SECRETKEY = ""
    TAG = "hawkeyo-21"
    COUNTRY = "UK"
    from amazon.paapi import AmazonAPI
    amazon = AmazonAPI(KEY, SECRETKEY, TAG, COUNTRY)
        # Writes a new line of price and date for all products in database, creates new file for new products
    dt = datetime.datetime.today()
    hourFile = open("static/homepage/Products Prices/hours.csv", "r")
    lines = hourFile.read().splitlines()
    last_line = lines[-1]
    if last_line[0:2] == str(dt.hour):
            print("same hour")
            hourFile = open("static/homepage/Products Prices/hours.csv", "w")
            hourFile.write(str(dt.hour)+"\n")
            for i in range(len(allProducts)):
                product = str(allProducts[i].productASIN)#loops through all products in database
                productFile = open(
                    "static/homepage/Products Prices/"+product+".csv", "a")
                productFile.close()#opens and cloeses the file just to create it
                productFile = open(
                    "static/homepage/Products Prices/"+product+".csv", "r")#now the file needs to be read
                line = productFile.readline()
                productFile = open(
                    "static/homepage/Products Prices/"+product+".csv", "a")
                
                if line == "": #New file so collum names are created for dygraph to recognise dates
                    productFile.write("Date,Price"+"\n")
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" +
                    str('%02d' % dt.day)+","+str(allProducts[i].productPRICE) + "\n")
                    productFile.close()
    else:
            #if the hour is differnet from the previous one, the price of all tracking products is added to its file
            print("different hour")
            productFile = open("static/homepage/Products Prices/hours.csv", "a")
            productFile.write(str(dt.hour)+"\n")
            
            for i in range(len(allProducts)):
                product = str(allProducts[i].productASIN)
                dt = datetime.datetime.today() #gets the current ti,e

                if last_line[0:8] != (dt.hour):
                    scrapedProduct = amazon.get_product(product)
                    productFile = open(
                        "static/homepage/Products Prices/"+product+".csv", "r")
                    line = productFile.readline()
                    productFile = open(
                        "static/homepage/Products Prices/"+product+".csv", "a")
                    if line == "": #If its a new file a special line must be added
                        productFile.write("Date,Price"+"\n")
                        productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/"+str(
                            '%02d' % dt.day)+","+str(scrapedProduct) + "\n")
                        productFile.close()
                    else:
                        productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/"+str(
                            '%02d' % dt.day)+","+str(scrapedProduct) + "\n")
                        productFile.close()
            
            

