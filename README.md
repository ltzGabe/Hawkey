# Hawkey

This is a website made using Django full-stack web framework
An Amazon price tracker allows users to track price data for different Amazon products in Chrome-like tabs.
A cron job is run on a separate computer which loops through all the products that have been uploaded by the main code of the website to an AWS s3 Buckety in order to obtain 
price data. The updated CSV is then re-uploaded to the s3 bucket and then re-downloaded by the code of the main website to be displayed to the user
