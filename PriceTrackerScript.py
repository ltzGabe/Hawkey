import boto3
import os
import datetime
import glob



def lambda_handler(event, context):
    accesskey = "AKIAXRTRLIKSIJBP6VFQ"
    privatekey = "OwO1mo8Bx/dI3gzXVKP0ZI0B1f7ny3knmS6BYro2"
    client = boto3.client("s3", aws_access_key_id = accesskey, aws_secret_access_key = privatekey)
    s3 = boto3.resource("s3", aws_access_key_id = accesskey, aws_secret_access_key = privatekey)
    bucket = s3.Bucket('productsdatafiles')
    count_obj = 0
    dir = '/tmp/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    for i in bucket.objects.all():
        count_obj = count_obj + 1
        client.download_file('productsdatafiles', i.key, '/tmp/' + str(i.key))

    KEY = "AKIAIDTHQ4TOY2C5SD5A"
    SECRETKEY = "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"
    TAG = "hawkeyo-21"  
    COUNTRY = "UK"
    #amazon = AmazonApi(KEY, SECRETKEY, TAG, COUNTRY, throttling=1)
    scrapeOrder = []
    #Finds the amount of entries for each product and pritires the least tracked products 
    line_count = 0
    for i in bucket.objects.all():
        productFile = open(
                "/tmp/"+str(i.key), "r")
    
        for line in productFile:
            if line != "\n":
                line_count += 1
        scrapeOrder.append([line_count,str(i.key)])
        productFile.close()
    
    scrapeOrderSorted = sorted(scrapeOrder, key=lambda x:x[0], reverse=False)#Sorted from most to leasted scraped
    print(len(scrapeOrderSorted))
    for i in range(len(scrapeOrderSorted)):
            dt = datetime.datetime.today() #gets the current time
            scrapedProduct = amazon.get_items(product.productASIN)[0]
            productFile = open(
                "/tmp/"+(scrapeOrderSorted[i][1]), "r")
            line = productFile.readline()
            productFile = open(
                "/tmp/"+scrapeOrderSorted[i][1], "a")
		if (scrapedProduct.offers.summaries[0].condition.value) == "Used":
                            offersUsedProductPRICE   = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersNewProductPRICE    = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                pass
                else:
                            offersNewProductPRICE    = scrapedProduct.offers.summaries[0].lowest_price.amount
                            try:
                                offersUsedProductPRICE   = scrapedProduct.offers.summaries[1].lowest_price.amount
                            except:
                                pass    
            if line == f"": #If its a new file a special line must be added
                productFile.write("hour,Price,Offer(new),Offer(old)"+"\n")
                try:
                        
                    productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                            str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE)+"," + str(offersUsedProductPRICE)+"\n")
                except:
                        try:
                            productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                                str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + ",None," + str(offersNewProductPRICE) +"\n")
                        except:
                            pass
                productFile.close()
            else:
                    try: 
                        productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                            str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + "," + str(offersNewProductPRICE) +"," + str(offersUsedProductPRICE)+"\n")
                    except:
                        try:
                            productFile.write(str(dt.year)+"/"+str('%02d' % dt.month)+"/" + str('%02d' % dt.day)+" "+
                                str('%02d' % dt.hour)+":00:00,"+str(scrapedProduct.offers.listings[0].price.amount) + ",None," + str(offersNewProductPRICE)+"\n")
                        except:
                            pass
                    productFile.close()



    #uploads all files to s3 database
    client = boto3.client("s3", aws_access_key_id = accesskey, aws_secret_access_key = privatekey)
    os.chdir("/tmp/")
    for file in os.listdir('/tmp/'):
        bucket = "productsdatafiles"
        bucketKey = str(file)
        client.upload_file(file,bucket, bucketKey)