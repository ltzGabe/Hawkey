import os
from django.contrib.auth.hashers import check_password
from homepage.models import Customer
from homepage.models import Product as productModel
from homepage.models import Tracker as trackerModel
from homepage.models import Reminder as remindersModel
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.http import JsonResponse, request, response
from homepage.forms import HomeForm
from django.contrib.auth.models import User
from .forms import CreateUserForm, UserLoginForm, CustomerForm, changeEmail1,changePassword
from django.contrib.auth.forms import UserCreationForm
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from amazon_paapi import AmazonApi
import datetime
from django.contrib.auth import get_user_model
from django_email_verification import send_email
from django_countries import CountryCode, countries
from django.core.mail import send_mail as priceEmail
from django.template.loader import render_to_string
import django
from django.utils import timezone
import boto3

headers = {
    "User-Agent"				: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding"			: "gzip, deflate",
    "Accept"					: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
    "Connection"				: "close",
    "Upgrade-Insecure-Requests"	: "1",
}

# Amazon api values
KEY = "AKIAIDTHQ4TOY2C5SD5A"
SECRETKEY = "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"
TAG = "hawkeyo-21"
COUNTRY = "UK"
amazon = AmazonApi(KEY, SECRETKEY, TAG, COUNTRY,  throttling=1)
#All the data for API to work

accesskey = "AKIA4YHZMKHLRZYQFHW4"
privatekey = "eX3rTLnVBIxPe4LCnvOw8kfCTE8f807DrezOtBJq"
client = boto3.client("s3", aws_access_key_id = accesskey, aws_secret_access_key = privatekey)

s3 = boto3.resource("s3", aws_access_key_id = accesskey, aws_secret_access_key = privatekey)
bucket = s3.Bucket('productsdatafilevalues')
for i in bucket.objects.all():
    client.download_file('productsdatafilevalues', i.key, 'static/homepage/Products Prices/' + str(i.key))
             

def chooseClosingTab(count, currentUser, closingTab, currentTab):        
            currentUser.tracker_set.all()[closingTab].delete()
            if closingTab == currentTab:
                currentTab = currentTab - 1
            if closingTab < currentTab:
                if closingTab == currentTab -1:
                    currentTab = currentTab - 1
                else:
                    currentTab = currentTab - 1
            if closingTab == currentTab-1:
                currentTab = currentTab-1
            return currentTab

# Function that takes a product object as an argument and opens the csv file 
# with the same ASIN unique identier 
def uploadFile(scrapedProduct):
    productFile = open("static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "rb")
    bucket = "productsdatafilevalues"
    client.upload_fileobj(productFile,bucket, scrapedProduct.asin+".csv")
    productFile.close()        
        
#file_list = os.listdir("static/homepage/Products Prices/")

# Loop through the files
#for file in file_list:
#    bucket = "productsdatafilevalues"
#    productFile = open("static/homepage/Products Prices/"+file, "rb")
#    file_path = os.path.join("static/homepage/Products Prices/", file)
#    if os.path.isfile(file_path):
#        client.upload_fileobj(productFile,bucket, file)

class Tracker(TemplateView):
    template_name = 'homepage/Tracker.html'
    def get(self, request, currentTab):
        type = request.GET.get("name")
        count = 0
        # Data for all the tabs are sorted (number of tabs, names of tabs)
        if request.user.is_authenticated:
            ProductNAME = []
            loginState = "True"
            currentUser = Customer.objects.get(name=request.user)
            trackingObjects = currentUser.tracker_set.all()
             #Counts the length of all the products the user is 
             # tracking, so javascript knows how many tabs to make
            for i in range(len(trackingObjects)):
                count += 1
             #for all the objects that the user is tracking the name of the
             # product is appneded to a list, if no product is being tracked 
             #the value is set to an empty string
            for i in currentUser.tracker_set.all():
                if i.product == None:
                    ProductNAME.append("")
                else:
                    ProductNAME.append(i.product.productNAME.replace(
                        "/", "").replace("'", ""))
            currentUser.numberTracking = count
            currentUser.save()
            #storeProductPrice()
        else:  # If the user is not logged in only one tab is created
            loginState = "False"
            count = 1
            ProductNAME = [""]
        form = HomeForm()
        args = {
            'currentTab': currentTab,
            "loginState": loginState,
            'form': form,
            "openTabs": count,
            "name": json.dumps(ProductNAME),
        }
        return render(request, self.template_name, args)

    def post(self, request, currentTab):
        count = 0
        type = request.POST.get("name")
        if request.user.is_authenticated:
            currentUser = Customer.objects.get(name=request.user)
            trackingObjects = currentUser.tracker_set.all()
            for i in range(len(trackingObjects)):
                count += 1
        form = HomeForm(request.POST)
        redirectTab = ""
        if "productURL" in request.POST: #If the user enters an amazon url directly
            if form.is_valid():
                dt = datetime.datetime.today()
                text = form.cleaned_data["productURL"]
                print(exists)
                scrapedProduct = amazon.get_items(text)[0]
                
                exists = productModel.objects.filter(
                    productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", "")).count()
                if exists == 1:
                    return redirect("http://127.0.0.1:8000/products/"+str(currentTab)+"Sony WH-1000XM4 Noise Cancelling Wireless Headphones - 30 hours battery life - Over Ear style - Optimised for Alexa and the Google Assistant - with built-in mic for phone calls - Black")
                if exists == 2:
                    productRRP = scrapedProduct.offers.listings[0].saving_basis.amount
                    if productRRP == None:
                        productRRP = scrapedProduct.offers.listings[0].price.amount
                    product = productModel.objects.get(
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                    product.productPRICE = scrapedProduct.offers.listings[0].price.amount
                    # Because the used product price data changes what postion in the return statement is in, 
                    # an if statement is used to find the correct used or new data. and if there is no used
                    # product price available it is set to none.
                    if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                        product.offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                        offersUsedProductPRICE= scrapedProduct.offers.summaries[0].lowest_price.amount
                        try:
                            product.offersNewProductPRICE = scrapedProduct.offers.summaries[1].lowest_price.amount
                            offersNewProductPRICE = scrapedProduct.offers.summaries[1].lowest_price.amount
                        except:
                            offersNewProductPRICE = None
                    else:
                        product.offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                        offersNewProductPRICE  = scrapedProduct.offers.summaries[0].lowest_price.amount
                        try:
                            product.offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                            offersUsedProductPRICE= scrapedProduct.offers.summaries[1].lowest_price.amount
                        except:
                            offersUsedProductPRICE = None
                    product.productRRP = productRRP
                    product.productDATE = django.utils.timezone.now()
                    product.save()
                    if request.user.is_authenticated:
                        object = trackingObjects[currentTab]
                        object.product = productModel.objects.get(
                            productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                        object.save()
                    redirectTab = productModel.objects.get(
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                    productFile = open(
                    "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE) +"\n")
                    productFile.close()
                else: 
                    scrapedProduct = amazon.get_items(text)[0]  # Searches amazon for product
                    messages.info(request,"This is the first time the product ",extra_tags='firstTime')
                    productUrl = scrapedProduct.detail_page_url
                    productRRP = scrapedProduct.offers.listings[0].saving_basis.amount

                    dt = datetime.datetime.today()

                    if "amazon.com" in productUrl:
                        productCOUNTRY = "US"
                    elif "amazon.co.uk" in productUrl:
                        productCOUNTRY = "GB"
                    #Because the used product price data changes what postion in the return statement is in, 
                    # an if statement is used to find the correct used or new data. and if there is no used
                    # product price available it is set to none.        
                    if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                            offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersNewProductPRICE = None
                    else:
                            offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersUsedProductPRICE = None    
                    
                    newProduct = productModel(
                        productURL=scrapedProduct.detail_page_url,
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""),
                        productIMAGE=scrapedProduct.images.primary.large.url,
                        productPRICE=scrapedProduct.offers.listings[0].price.amount,
                        productRRP=productRRP,
                        productMANUFACTURE=scrapedProduct.item_info.by_line_info.manufacturer.display_value,
                        productBRAND=scrapedProduct.item_info.by_line_info.brand.display_value,
                        offersNewProductPRICE=offersNewProductPRICE,
                        offersUsedProductPRICE=offersUsedProductPRICE,
                        productMODEL=scrapedProduct.item_info.manufacture_info.model.display_value[0],
                        productCONDITON="New",
                        productPRODUCTGROUP=scrapedProduct.item_info.classifications.product_group.display_value,
                        productMERCHANT=scrapedProduct.offers.listings[0].merchant_info.name,
                        productASIN=scrapedProduct.asin,
                        productCOUNTRY = productCOUNTRY
                    )
                    productFile = open(
                    "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                    newProduct.save()
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE) +"\n")
                    productFile.close()
                    uploadFile(scrapedProduct)
                    if request.user.is_authenticated:  # If user is logged in, the new product is added to their database model
                        object = trackingObjects[currentTab]
                        object.product = productModel.objects.get(
                            productURL=productUrl)
                        object.save()

                    redirectTab = productModel.objects.get(
                        productURL=scrapedProduct.detail_page_url)
        elif type == "searching":  # For when the user dosent input a URL instead a searchword querey
            text = request.POST.get("text")
            # lists that store all of the search results data
            prodnames = []
            prodimages = []
            prodprices = []
            scrapedProducts = amazon.search_items(
                item_count=10, keywords=text)
            # for all the products in the scraped list, specific values are appened to a list
            for item in scrapedProducts.items:
                prodnames.append(item.item_info.title.display_value)
                prodimages.append(item.images.primary.medium.url)
                try:
                    if item.offers.listings[0].price.display_amount == None:
                        prodprices.append("Price unavailable")
                    else:
                        prodprices.append(item.offers.listings[0].price.display_amount)
                except:
                    prodprices.append("Price unavailable")
            return JsonResponse({"names": json.dumps(prodnames),
                                 "images": json.dumps(prodimages),
                                 "prices": json.dumps(prodprices)
                                 }, status=200)
        elif type == "choosing":
            dt= datetime.datetime.today()
            text = request.POST.get("text")
            scrapedProducts = amazon.search_items(
                item_count=10, keywords=text)
            scrapedProduct = scrapedProducts.items[int(
                request.POST.get("chosenProduct"))]
            productName = scrapedProduct.item_info.title.display_value.replace(
                        "/", "").replace("'", "")
            exists = productModel.objects.filter(productNAME=productName).count()
            #Because the used product price data changes what postion in the return statement is in, 
            # an if statement is used to find the correct used or new data. and if there is no used
            # product price available it is set to none.
            if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                try:
                    offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                except:
                    offersNewProductPRICE = None
            else:
                offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                try:
                    offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                except:
                    offersUsedProductPRICE = None

            if exists == 1: 
                if request.user.is_authenticated:
                    object = trackingObjects[currentTab]
                    object.product = productModel.objects.get(
                        productNAME=productName)
                    object.save()
                redirectTab = productModel.objects.get(productNAME=productName)
                productFile = open(
                "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE) +"\n")
                productFile.close()
            else:
                messages.info(request,"This is the first time the product ",extra_tags='firstTime')#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template
                productPRICE = scrapedProduct.offers.listings[0].price.amount
                try:
                    productRRP = scrapedProduct.offers.listings[0].saving_basis.amount
                except:
                    productRRP = productPRICE
                
                if productRRP == None:
                        productRRP = scrapedProduct.offers.listings[0].price.amount
                if "amazon.com" in scrapedProduct.detail_page_url:
                        productCOUNTRY = "US"
                elif "amazon.co.uk" in scrapedProduct.detail_page_url:
                        productCOUNTRY = "GB"

                try:
                    productMODEL=scrapedProduct.item_info.manufacture_info.model.display_value,
                except:
                    productMODEL="Not available"
                try:        
                    productBRAND=scrapedProduct.item_info.by_line_info.brand.display_value  
                except:
                    productBRAND ="Not available"
                newProduct = productModel(
                        productURL=scrapedProduct.detail_page_url,
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""),
                        productIMAGE=scrapedProduct.images.primary.large.url,
                        productPRICE=scrapedProduct.offers.listings[0].price.amount,
                        productRRP=productRRP,
                        productMANUFACTURE=scrapedProduct.item_info.by_line_info.manufacturer.display_value,
                        productBRAND=productBRAND,
                        offersNewProductPRICE=offersNewProductPRICE,
                        offersUsedProductPRICE=offersUsedProductPRICE,
                        productMODEL=productMODEL[0],
                        productCONDITON="New",
                        productPRODUCTGROUP=scrapedProduct.item_info.classifications.product_group.display_value,
                        productMERCHANT=scrapedProduct.offers.listings[0].merchant_info.name,
                        productASIN=scrapedProduct.asin,
                        productCOUNTRY = productCOUNTRY
                    )
                newProduct.save()
                productFile = open(
                "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE)+"\n")
                productFile = open(
                    "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "rb")

                productFile.close()
                uploadFile(scrapedProduct)
                if request.user.is_authenticated:
                    object = trackingObjects[currentTab]
                    object.product = productModel.objects.get(
                        productNAME=productName)
                    object.save()
                redirectTab = productModel.objects.get(productNAME=productName)
            return JsonResponse({"redirect": str(currentTab)+"/"+str(redirectTab)}, status=200)
        elif type == "closetab":
            closingTab = int(request.POST.get("closingTab"))
            nextTab = chooseClosingTab(count, currentUser, closingTab, currentTab)
            if str(currentUser.tracker_set.all()[nextTab].product) == "None":
                redirectTab = ""
            else:
                redirectTab = str(currentUser.tracker_set.all()[nextTab].product)
            print(redirectTab)
            if closingTab != nextTab:
                return JsonResponse({"redirect": str(nextTab)+"/"+redirectTab}, status=200)
           
        elif type == "newtab":
            if request.user.is_authenticated:
                tab = trackerModel(
                    customer=Customer.objects.get(name=request.user))
                tab.save()
            else:
                pass

        return redirect("http://127.0.0.1:8000/products/"+str(currentTab)+"/"+str(redirectTab))

class Product(TemplateView):
    template_name = "homepage/product.html"
    model = productModel

    def get(self, request, product, currentTab):
        count = 0
        ProductNAME = []
        form = HomeForm()
        cuurentProduct = productModel.objects.get(productNAME=product)#gets product model for 
        openTab = cuurentProduct #gets ASIN for current product
        productFile = open(
                "static/homepage/Products Prices/"+openTab.productASIN+".csv", "r")#opens the file for the open Tab
        priceAndAsin = []
        lines = productFile.readlines()[0:]
        #Takes away non values from the average #Takes away non values from the average 
        priceAdj = 0
        priceOLDAdj = 0     
        priceNEWAdj = 0
        last_line = lines[-1]
        recentDate = last_line[0:10]
        recentHour = last_line[11:16]
        #Creates a list with all the values and dates for each product
        for line in lines:
            lines = line.split(",")
            date = ((str(lines[0])))
            
            price = (lines[1])
            priceNEW = (lines[2])
            priceOLD = (lines[3].strip("\n"))
            
            #If there is no value in that space it is then replaced with a 0 
            if priceOLD == "None":
                priceOLD = 0.00
                priceOLDAdj = priceOLDAdj + 1 #Counts how many non values there are
                
            else:
                priceOLD = float(priceOLD)
            if priceNEW == "None":
                priceNEW = 0.00
                priceNEWAdj = priceNEWAdj + 1
            else:
                priceNEW = float(priceNEW)
            if price == "None":
                price = 0.00
                priceAdj = priceAdj + 1
            else:
                price = float(price)
            priceAndAsin.append([date,price,priceNEW,priceOLD])
            
            productFile.close()

        
        
        total = 0.00
        NEWaveragePrice = 0.00
        OLDaveragePrice = 0.00 
        
    #AMAZON DATA FOR NEW PRODSUCTS
        priceAndAsinSorted = sorted(priceAndAsin, key=lambda x:x[1], reverse=True)
        for i in range(len(priceAndAsinSorted)):
            total = total + priceAndAsinSorted[i][1]
        try:
            averagePrice = round(total/(len(priceAndAsinSorted)-priceAdj),2)
        except:
            averagePrice = None
        lowestPrice =  round(priceAndAsinSorted[-1][1],2)
        for i in range(len(priceAndAsinSorted)):
            if lowestPrice == 0.00:
                lowestPrice = round(priceAndAsinSorted[-1-i][1],2)
            else: 
                lowestPriceDate =  priceAndAsinSorted[-1-i][0][0:10]
                lowestPrice =  round(priceAndAsinSorted[-1-i][1],2)
                break

        HighestPrice = round(priceAndAsinSorted[0][1],2)
        #Gets the date of the lowest and highest price
        HighestPriceDate = priceAndAsinSorted[0][0][0:10]
        if HighestPrice == lowestPrice:
            lowestPriceDate = HighestPriceDate

        #AMAZON DATA FOR NEW OFFERS
        priceAndAsinSorted = sorted(priceAndAsin, key=lambda x:x[2], reverse=True)
        for i in range(len(priceAndAsinSorted)):
            NEWaveragePrice = NEWaveragePrice + priceAndAsinSorted[i][2]
        try:
            NEWaveragePrice = round(NEWaveragePrice/(len(priceAndAsinSorted)-priceNEWAdj),2)
        except:
            NEWaveragePrice = 0.00
        NEWlowestPrice =  round(priceAndAsinSorted[-1][2],2)
        for i in range(len(priceAndAsinSorted)):
            if NEWlowestPrice == 0.00:
                NEWlowestPrice = round(priceAndAsinSorted[-1-i][2],2)
            else: 
                NEWlowestPrice =  round(priceAndAsinSorted[-1-i][2],2)
                NEWlowestPriceDate =  priceAndAsinSorted[-1-i][0][0:10]
                break
        NEWHighestPrice = round(priceAndAsinSorted[0][2],2)
        #Gets the date of the lowest and highest price
        NEWHighestPriceDate = priceAndAsinSorted[0][0][0:10]
        if NEWHighestPrice == NEWlowestPrice:
            NEWlowestPriceDate = NEWHighestPriceDate
            
        print(priceAndAsinSorted)    
            
         #AMAZON DATA FOR USED OFFERS
        priceAndAsinSorted = sorted(priceAndAsin, key=lambda x:x[3], reverse=True)
        for i in range(len(priceAndAsinSorted)):
            OLDaveragePrice = OLDaveragePrice + priceAndAsinSorted[i][3]
        try:
            OLDaveragePrice = round(OLDaveragePrice/(len(priceAndAsinSorted)-priceOLDAdj),2)
        except:
            OLDaveragePrice = 0.00
        OLDlowestPrice =  round(priceAndAsinSorted[-1][3],2)
        for i in range(len(priceAndAsinSorted)):
            if OLDlowestPrice == 0.00:
                OLDlowestPrice = round(priceAndAsinSorted[-1-i][3],2)
            else: 
                OLDlowestPrice =  round(priceAndAsinSorted[-1-i][3],2)
                OLDlowestPriceDate =  priceAndAsinSorted[-1-i][0][0:10]
                break

        OLDHighestPrice = round(priceAndAsinSorted[0][3],2)
        #Gets the date of the lowest and highest price
        OLDHighestPriceDate = priceAndAsinSorted[0][0][0:10]
        if OLDHighestPrice == OLDlowestPrice:
            OLDlowestPriceDate = OLDHighestPriceDate    

            
        if request.user.is_authenticated:
            currentUser = Customer.objects.get(name=request.user)
            loginState = "True"
            trackingObjects = currentUser.tracker_set.all()
            for i in range(len(trackingObjects)):
                count += 1
            for i in currentUser.tracker_set.all():
                if i.product == None:
                    ProductNAME.append("")
                else:
                    ProductNAME.append(i.product.productNAME.replace(
                        "/", "").replace("'", ""))
            currentUser.numberTracking = count
            currentUser.save()
            #phoneNumber = currentUser.phonenumber
            email = request.user.email
            
            if remindersModel.reminderPriceDB == None:
                reminderPrice = float(trackingObjects[currentTab].product.productPRICE) - 0.01
            else:
                reminderPrice = remindersModel.reminderPriceDB
            args = {
                "NEWlowestPriceDate":NEWlowestPriceDate,
                "NEWHighestPriceDate":NEWHighestPriceDate,
                "NEWaveragePrice":NEWaveragePrice,
                "NEWlowestPrice":NEWlowestPrice,
                "NEWHighestPrice":NEWHighestPrice,
                "recentDate":recentDate,
                "recentHour":recentHour,
                "OLDlowestPriceDate":OLDlowestPriceDate,
                "OLDHighestPriceDate":OLDHighestPriceDate,
                "OLDaveragePrice":OLDaveragePrice,
                "OLDlowestPrice":OLDlowestPrice,
                "OLDHighestPrice":OLDHighestPrice,
                "lowestPriceDate":lowestPriceDate,
                "HighestPriceDate":HighestPriceDate,
                "averagePrice":averagePrice,
                "lowestPrice":lowestPrice,
                "HighestPrice":HighestPrice,
                "reminderPrice":reminderPrice,
                "openTab": openTab,
                "loginState": loginState,
                'currentTab': currentTab,
                'form': form,
                "products": trackingObjects,
                "openTabs": count,
                "name": json.dumps(ProductNAME),
                "product": cuurentProduct,
                "email": email,
                #"phoneNumber": phoneNumber
            }
        else:
            loginState = "False"
            ProductNAME.append(str(cuurentProduct))
            args = {
                "NEWlowestPriceDate":NEWlowestPriceDate,
                "NEWHighestPriceDate":NEWHighestPriceDate,
                "NEWaveragePrice":NEWaveragePrice,
                "NEWlowestPrice":NEWlowestPrice,
                "NEWHighestPrice":NEWHighestPrice,
                "recentDate":recentDate,
                "recentHour":recentHour,
                "OLDlowestPriceDate":OLDlowestPriceDate,
                "OLDHighestPriceDate":OLDHighestPriceDate,
                "OLDaveragePrice":OLDaveragePrice,
                "OLDlowestPrice":OLDlowestPrice,
                "OLDHighestPrice":OLDHighestPrice,
                "lowestPriceDate":lowestPriceDate,
                "HighestPriceDate":HighestPriceDate,
                "averagePrice":averagePrice,
                "lowestPrice":lowestPrice,
                "HighestPrice":HighestPrice,
                "currentTab": 0,
                "loginState": loginState,
                'form': form,
                "openTab": openTab.productASIN,
                "openTabs": 1,
                "product": cuurentProduct,
                "name": json.dumps(ProductNAME),
            }

        #storeProductPrice()
        return render(request, self.template_name, args)

    def post(self, request, product, currentTab):
        count = 0
        type = request.POST.get("name")
        if request.user.is_authenticated:
            currentUser = Customer.objects.get(name=request.user)
            trackingObjects = currentUser.tracker_set.all()
            for i in range(len(trackingObjects)):
                count += 1   
        form = HomeForm(request.POST)
        redirectTab = ""

        if "productURL" in request.POST:
            if form.is_valid():
                dt = datetime.datetime.today()
                text = form.cleaned_data["productURL"]
                scrapedProduct = amazon.get_items(text)[0]
                
                exists = productModel.objects.filter(
                    productNAME=scrapedProduct.info.title.display_value.replace("/", "").replace("'", "")).count()
                if exists == 1:      
                    productRRP = scrapedProduct.offers.listings[0].saving_basis.amount
                    if productRRP == None:
                        productRRP = scrapedProduct.offers.listings[0].price.amount
                    product = productModel.objects.get(
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                    product.productPRICE = scrapedProduct.offers.listings[0].price.amount
                    # Because the used product price data changes what postion in the return statement is in, 
                    # an if statement is used to find the correct used or new data. and if there is no used
                    # product price available it is set to none.    
                    if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                            offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersNewProductPRICE = None
                    else:
                            offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersUsedProductPRICE = None
                    product.productRRP = productRRP
                    product.productDATE = django.utils.timezone.now()
                    product.save()
                    if request.user.is_authenticated:
                        object = trackingObjects[currentTab]
                        object.product = productModel.objects.get(
                            productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                        object.save()
                    redirectTab = productModel.objects.get(
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                    productFile = open(
                    "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE)+"\n")
                    productFile.close()
                else:
                    messages.info(request,"This is the first time the product ",extra_tags='firstTime')#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template
                    productUrl = scrapedProduct.detail_page_url
                    print(scrapedProduct.offers.listings[0].price.amount)
                    productRRP = scrapedProduct.offers.listings[0].saving_basis.amount
                    if productRRP == None:
                        productRRP = scrapedProduct.offers.listings[0].price.amount
                    if "amazon.com" in productUrl:
                        productCOUNTRY = "US"
                    elif "amazon.co.uk" in productUrl:
                        productCOUNTRY = "GB"
                    #Because the used product price data changes what postion in the return statement is in, 
                    # an if statement is used to find the correct used or new data. and if there is no used
                    # product price available it is set to none.
                    if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                            offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersNewProductPRICE = None
                    else:
                            offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                offersUsedProductPRICE = None
                    newProduct = productModel(
                        productURL=scrapedProduct.detail_page_url,
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""),
                        productIMAGE=scrapedProduct.images.primary.large.url,
                        productPRICE=scrapedProduct.offers.listings[0].price.amount,
                        productRRP=productRRP,
                        productMANUFACTURE=scrapedProduct.item_info.by_line_info.manufacturer.display_value,
                        productBRAND=scrapedProduct.item_info.by_line_info.brand.display_value,
                        offersNewProductPRICE=offersNewProductPRICE,
                        offersUsedProductPRICE=offersUsedProductPRICE,
                        productMODEL=scrapedProduct.item_info.manufacture_info.model.display_value[0],
                        productCONDITON="New",
                        productPRODUCTGROUP=scrapedProduct.item_info.classifications.product_group.display_value,
                        productMERCHANT=scrapedProduct.offers.listings[0].merchant_info.name,
                        productASIN=scrapedProduct.asin,
                        productCOUNTRY = productCOUNTRY
                    )
                    newProduct.save()
                    productFile = open(
                    "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                    newProduct.save()
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE)+"\n")
                    productFile.close()
                    uploadFile(scrapedProduct)
                    if request.user.is_authenticated:
                        object = trackingObjects[currentTab]
                        object.product = productModel.objects.get(
                            productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""))
                        object.save()
                    redirectTab = productModel.objects.get(
                        productURL=scrapedProduct.detail_page_url)
            else:
                pass
        elif type == "searching":
            text = request.POST.get("text")
            # lists that store all of the search results data
            prodnames = []
            prodimages = []
            prodprices = []
            scrapedProducts = amazon.search_items(
                item_count=10, keywords=text)
            # for all the products in the scraped list, specific values are appened to a list
            for item in scrapedProducts.items:
                prodnames.append(item.item_info.title.display_value)
                prodimages.append(item.images.primary.medium.url)
                try:
                    if item.offers.listings[0].price.display_amount == None:
                        prodprices.append("Price unavailable")
                    else:
                        prodprices.append(item.offers.listings[0].price.display_amount)
                except:
                    prodprices.append("Price unavailable")
            return JsonResponse({"names": json.dumps(prodnames),
                                 "images": json.dumps(prodimages),
                                 "prices": json.dumps(prodprices)
                                 }, status=200)
        elif type == "choosing":
            dt= datetime.datetime.today()
            text = request.POST.get("text")
            scrapedProducts = amazon.search_items(
                item_count=10, keywords=text)
            scrapedProduct = scrapedProducts.items[int(
                request.POST.get("chosenProduct"))]
            productName = scrapedProduct.item_info.title.display_value.replace(
                        "/", "").replace("'", "")
            exists = productModel.objects.filter(productNAME=productName).count()
            #Because the used product price data changes what postion in the return statement is in, 
            # an if statement is used to find the correct used or new data. and if there is no used
            # product price available it is set to none.
            if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                try:
                    offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                except:
                    offersUsedProductPRICE = None
            else:
                offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                try:
                    offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                except:
                    offersUsedProductPRICE = None

            if exists == 1:
                
                if request.user.is_authenticated:
                    object = trackingObjects[currentTab]
                    object.product = productModel.objects.get(
                        productNAME=productName)
                    object.save()
                redirectTab = productModel.objects.get(productNAME=productName)
                productFile = open(
                "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE)+"\n")                
                productFile.close()
            else:
                messages.info(request,"This is the first time the product ",extra_tags='firstTime')#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template#if product is not previsouly on database a modal is sent to the product template
                productRRP = scrapedProduct.offers.listings[0].saving_basis.amount
                productPRICE = scrapedProduct.offers.listings[0].price.amount
                if productRRP == None:
                    productRRP = scrapedProduct.offers.listings[0].price.amount
                if "amazon.com" in scrapedProduct.detail_page_url:
                        productCOUNTRY = "US"
                elif "amazon.co.uk" in scrapedProduct.detail_page_url:
                        productCOUNTRY = "GB"
                try:
                    productMODEL=scrapedProduct.item_info.manufacture_info.model.display_value
                except:
                    productMODEL="Not available"
                try:        
                    productBRAND=scrapedProduct.item_info.by_line_info.brand.display_value  
                except:
                    productBRAND ="Not available"
                newProduct = productModel(
                     productURL=scrapedProduct.detail_page_url,
                        productNAME=scrapedProduct.item_info.title.display_value.replace("/", "").replace("'", ""),
                        productIMAGE=scrapedProduct.images.primary.large.url,
                        productPRICE=scrapedProduct.offers.listings[0].price.amount,
                        productRRP=productRRP,
                        productMANUFACTURE=scrapedProduct.item_info.by_line_info.manufacturer.display_value,
                        productBRAND=productBRAND,
                        offersNewProductPRICE=offersNewProductPRICE,
                        offersUsedProductPRICE=offersUsedProductPRICE,
                        productMODEL=productMODEL[0],
                        productCONDITON="New",
                        productPRODUCTGROUP=scrapedProduct.item_info.classifications.product_group.display_value,
                        productMERCHANT=scrapedProduct.offers.listings[0].merchant_info.name,
                        productASIN=scrapedProduct.asin,
                        productCOUNTRY = productCOUNTRY
                    )
                newProduct.save()
                productFile = open(
                "static/homepage/Products Prices/"+scrapedProduct.asin+".csv", "a")
                productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                        str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount,) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE) +"\n")
                productFile.close()
                uploadFile(scrapedProduct)
                if request.user.is_authenticated:
                    object = trackingObjects[currentTab]
                    object.product = productModel.objects.get(
                        productNAME=productName)
                    object.save()
                redirectTab = productModel.objects.get(productNAME=productName)
            return JsonResponse({"redirect": str(currentTab)+"/"+str(redirectTab)}, status=200)
        elif type == "closetab":
            closingTab = int(request.POST.get("closingTab"))
            nextTab = chooseClosingTab(count, currentUser, closingTab, currentTab)
            if str(currentUser.tracker_set.all()[nextTab].product) == "None":
                redirectTab = ""
            else:
                redirectTab = str(currentUser.tracker_set.all()[nextTab].product)
            if closingTab != currentTab:
                return JsonResponse({"redirect": str(currentTab)+"/"+redirectTab}, status=200)
        elif type == "newtab":
            tab = trackerModel(
                customer=Customer.objects.get(name=request.user))
            tab.save()
        #Post reuqsting for setting an notification for price drop
        elif type == "priceNoti":
            reminderPrice = request.POST.get("reminderPrice")
            reminderType =request.POST.get("reminderType")
            newReminder = remindersModel(
                reminderPriceDB = reminderPrice,
                reminderTypeDB = reminderType,
                customer=Customer.objects.get(name=request.user),
                product = productModel.objects.get(productNAME = product),
            )
            newReminder.save()

        return redirect("http://127.0.0.1:8000/products/"+str(currentTab)+"/"+str(redirectTab))



class About(TemplateView):
    template_name = 'homepage/About.html'


class Contact(TemplateView):
    template_name = 'homepage/ContactUs.html'



class Donate(TemplateView):
    template_name = 'homepage/Donate.html'
    
def Landing(self, *args, **kwargs):
    template_name = 'homepage/Donate.html'
    
class Account(TemplateView):
    template_name = 'homepage/Account.html'

    def get(self, request):
        form = CustomerForm()
        changeEmail = changeEmail1()
        resetPassword = changePassword()
        count = 0
        ProductNAME = []
        currentUser = Customer.objects.get(name=request.user)
        trackingObjects = currentUser.tracker_set.all()
        for i in range(len(trackingObjects)):
            count += 1
        for i in currentUser.tracker_set.all():
            if i.product == None:
                ProductNAME.append("")
            else:
                ProductNAME.append(i.product.productNAME)
        args = {
            "resetPassword":resetPassword,
            "changeEmail": changeEmail,
            "form": form,
            "currentUser": currentUser,
            "openTabs": count,
            "products": trackingObjects,
            "name": json.dumps(ProductNAME),
            "currentTab": None,
        }
        #storeProductPrice()
        return render(request, self.template_name, args)

    def post(self, request):

        type = request.POST.get("name")
        form = CustomerForm(request.POST)
        changeEmail = changeEmail1(request.POST)
        resetPassword = changePassword(request.POST)
        if type == "verification_email": #ajax request for resending verification email
            user = request.user
            send_email(user)
        if type == "changePassword":
                oldPassword =   request.POST.get("oldPassword")
                password1   =   request.POST.get("password1")
                password2   =   request.POST.get("password2")
                user = authenticate(request, username=request.user.username, password=oldPassword)
                if user == None:
                    return JsonResponse({"responseType": "wrongPassword"})
                else:
                    if password1 != password2:
                        return JsonResponse({"responseType": "diffPasswords"})
                    elif password1 =="" or password2=="": 
                        exit()
                    else:
                        if check_password(password1, request.user.password) == True:
                            return JsonResponse({"responseType": "samePassword"})
                        else: 
                            user.set_password(password1)
                            user.save()
                            return JsonResponse({"responseType": "success"})
        if form.is_valid():
            #getting data from form to check if their account details can be changed
            email = form.cleaned_data.get("email")
            newUsername = form.cleaned_data.get("username")
            country = form.cleaned_data.get("country")
            #phonenumber = form.cleaned_data.get("phonenumber")
            #print(phonenumber)
            emailExists = User.objects.filter(email = email).exists()
            usernameExists = User.objects.filter(username = newUsername).exists()
            user = request.user
            storedEmail = user.email
            storedUsernname = user.username
            currentUser = Customer.objects.get(name=request.user)
            #currentUser.phonenumber = phonenumber
            currentUser.country = country
            check = True
            #checks to see if the user changed their email and if they did another check is done to see if the email already exixts
            if storedEmail != email:
                if emailExists == True:
                    messages.info(request,"This email address is already in use.",extra_tags='email')
                    check = False
                else:
                    user.is_active = False
                    send_email(user) #sends a verifivation email to the new email address
            #checks to see if the user changed their username and if they did another check is done to see if the username already exixts

            if storedUsernname != newUsername:
                if usernameExists == True:
                    check = False
                    messages.info(request,message="This username is already in use", extra_tags='username')
            if check == True: 
                #If user passes both checks then accounted details are chnaged
                #currentUser.phonenumber = phonenumber
                user.username = newUsername
                user.email = email
                currentUser.country = country
                user.save()
                currentUser.save()
                messages.info(request, 'Your account details have been changed.' ,extra_tags="success")
        elif changeEmail.is_valid(): #change email address form for unactivated users
            email = changeEmail.cleaned_data.get("changeEmail")
            user = request.user
            user.email = email
            send_email(user)
        


        args = {
            "openTabs":0,
            "resetPassword":changePassword(),
            "form": form,
            "changeEmail":changeEmail
        }
        return render(request, 'homepage/Account.html', args)


def register(request):
    if request.method == 'GET':
        template_name = 'homepage//register.html'
        #storeProductPrice()

        if request.user.is_authenticated:
            return redirect('Landing')
        else:
            form = CreateUserForm()

            args = {"form": form}

            return render(request, template_name, args)

    elif request.method == 'POST': 
        signUpForm = CreateUserForm(request.POST)
        if signUpForm.is_valid():
            username = signUpForm.cleaned_data.get("username")
            password = signUpForm.cleaned_data.get('password1')
            email = signUpForm.cleaned_data.get("email")
            user = User.objects.create_user(
                username=username, password=password, email=email)
            user.is_active = False
            login(request, user)
            send_email(user)
            newCustomer = Customer(
                name=request.user,
                numberTracking=1,
                #phonenumber="447546280315"
            )
            newCustomer.save()
            newTracker = trackerModel(
                customer=newCustomer,
            )
            newTracker.save()
            return redirect('Account')
        args = {"form": signUpForm}
        return render(request, 'homepage//register.html', args)


class loginUser(TemplateView):
    template_name = 'homepage/loginUser.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('Landing')
        else:
            form = UserLoginForm()
            args = {"form": form}
            return render(request, self.template_name, args)

    def post(self, request):
        loginForm = UserLoginForm(request.POST)
        if loginForm.is_valid():
            username = loginForm.cleaned_data.get("usernameSignIn")
            password = loginForm.cleaned_data.get("passwordSignIn")
            user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            return redirect('Landing')
        else:
            messages.info(request, 'Username or password is incorrect')

        args = {"form": loginForm}
        return render(request, 'homepage/loginUser.html', args)


def logoutUser(request):
    logout(request)
    return redirect('Landing')
def deleteUser(request):
    request.user.delete()
    return redirect('Tracker')


class password_reset_confirm(TemplateView):
    template_name = 'homepage/password_reset_page.html'

    def get(self, request):
        print("this is happening")
        resetPassword = changePassword()
        args = {"resetPassword": resetPassword}
        return render(request, self.template_name, args)
    def post(self, request):

        return render(request, 'homepage/password_reset_confirm.html')