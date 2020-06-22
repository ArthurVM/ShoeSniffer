"""

James' super awesome shoe sniffing module.

"""
from bs4 import BeautifulSoup as bs
import requests as req
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

class Shoe(object):
    """docstring for Shoe."""

    def __init__(self, infobox):
        super(Shoe, self).__init__()
        self.shoename = infobox[0]
        self.url = infobox[1]
        self.token = infobox[2]
        self.dtype = infobox[3]
        self.classname = infobox[4]

    def getItemCost(self):
        """ Public method function for getting the item cost of a shoe instance.
        """
        item_page = req.get(self.url)
        item_page_record = bs(item_page.content, "html.parser")

        price_string = item_page_record.find(self.token, attrs={self.dtype:self.classname})

        try:
            price = float(re.sub("\W+", "", price_string.text.strip()))

            self.price = price / 100     ## assign the cost attribute to the shoe

        except(AttributeError):
            ## catch attribute errors if they have changed the website so the given price location tokens no longer work
            self.price = None

def main(verboseflag, max_price=120.0):

    if verboseflag:
        print("Starting Sniff...\n")

    ## path to a simple text file containing email login credentials
    creds_file = "./emaildeets.txt"

    shoe_box = [
    ["Chimeras_BF", "https://www.bananafingers.co.uk/climbing-shoes/scarpa/chimera", "div", "class", "product-basics__price__sell-price"],
    ["Chimeras_RR", "https://rockrun.com/products/scarpa-chimera?variant=31463074312", "span","class","current_price"],
    ["Chimera_ET", "https://shop.epictv.co.uk/en/climbing-shoes/scarpa/chimera-climbing-shoe?sku=SCAS17M_CLSHCHI_Y/B/V41", "div", "class", "field-item even"],
    ["Chimera_AT", "https://www.alpinetrek.co.uk/scarpa-chimera-climbing-shoes/?aid=11a93713e121c0b3e4839f3d7a1edd4d&pid=10004&gclid=Cj0KCQjwl8XtBRDAARIsAKfwtxD_rA88xctwOopYoMwrasUp7ILPHYLw2ix7p_8m-0pQc1JeYYPnfUgaAgYBEALw_wcB&wt_mc=uk.pla.google_uk.254044867.25884866587.104604046507", "div", "content", "price"],
    ["Instinct_BF", "https://www.bananafingers.co.uk/climbing-shoes/scarpa/instinct-vs-r", "div", "class", "product-basics__price__sell-price"],
    ["Instinct_ET", "https://shop.epictv.co.uk/en/climbing-shoes/scarpa/instinct-vsr-climbing-shoe?sku=SCAW17_CLSHINVSR_41.5", "div", "class", "field-item even"],
    ["Instinct_RR", "https://rockrun.com/collections/climbing-shoes/products/scarpa-instinct-vs-r", "span", "class", "current_price"],
    ["C_Instincts_BF", "https://www.bananafingers.co.uk/climbing-shoes/scarpa/instinct-vs-womens", "div", "class", "product-basics__price__sell-price"]
    ]

    bargain_box = []
    bargain_flag = False

    for shoeinfo in shoe_box:
        shoe_instance = Shoe(shoeinfo)
        shoe_instance.getItemCost()

        ## checks to see if there were any problems finding the price
        if shoe_instance.price != None:
            shoestring = f" Shoe name : {shoe_instance.shoename}\n URL : {shoe_instance.url}\n Price : {shoe_instance.price}\n"

            ## always nice to have an optional verbose flag
            if verboseflag:
                print(shoestring)

            ## appends cheap shoes into the bargain bucket
            if shoe_instance.price <= max_price:
                bargain_flag = True
                bargain_box.append(shoestring)

        else:
            ## there were problems if it gets here
            ## you may want to alert yourself to any problems via email
            shoestring = f" Cannot find price for {shoe_instance.shoename} at {shoe_instance.url}\n Check that the website is still as expected.\n"
            if verboseflag:
                print(shoestring)

    ## check if there are any bargains going on
    if bargain_flag:
        email_body = "Congratulations one or more of your items is below the cost you specified!\n\n"
        email_body += "\n".join(bargain_box)

        sendEmail(email_body, creds_file)

    elif not bargain_flag:
        print("\nNo bargains today.\n")

def sendEmail(email_body, creds_file):
    """ Send an email if there is anything in the bargain box
    """
    ## get login credentials
    email_addr, password = getLoginCredentials(creds_file)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    try:
        s.login(email_addr, password)
    except(smtplib.SMTPAuthenticationError):
        ## hopefully it wont get here, but if it does check privacy and security setting on your email account
        raise Exception("LOGIN ERROR either you have got your credentials wrong or less secure apps being blocked by your email provider.")
        exit(1)

    msg = MIMEMultipart()
    msg['From'] = email_addr
    msg['To'] = email_addr
    msg['Subject'] = "WooHoo Cheap Items"

    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = f"{dt_string}\n\n{email_body}"
    msg.attach(MIMEText(message, "plain"))
    s.send_message(msg)

def getLoginCredentials(creds_file):
    """ Reads a text file and captures login details.
    The file should be structured as:

    user@email.com
    password123

    This is in no way a secure way of doing things, but better than hardcoding.
    """

    with open(creds_file, "r") as f:
        email_addr = f.readline().strip("\n")
        password = f.readline().strip("\n")

    return email_addr, password

if __name__ == "__main__":
    verboseflag=False
    if verboseflag:
        print(__doc__)
    main(verboseflag)
