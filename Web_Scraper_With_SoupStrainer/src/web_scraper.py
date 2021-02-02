import bs4
from urllib.request import urlopen as request
from bs4 import BeautifulSoup as soup
from bs4 import SoupStrainer as strainer
import csv

# dictionary that has key-value pairs of
# manufacturer name: manufacturer id number
manufacturers = {
    'MSI': '50001312',
    'GIGABYTE': '50001314',
    'ASUS': '50001315',
    'ASRock': '50001944',
    'EVGA': '50001402',
    'VisionTek': '50001180'
}

base_url = 'https://www.newegg.com/p/pl?d=graphics+cards&N=' + manufacturers['GIGABYTE'] + '&page='

# creates a SoupStrainer object that is used to
# generate minimal HTML in each parsed document
only_item_cells = strainer("div", attrs={"class": "item-cell"})

min_page_number = 1
max_page_number = 6 # based on checking newegg.com, number will vary when site is updated
page_cells = []

# opening connection, grabbing the HTML from each page
# and generating the corresponding page soup
for num in range(min_page_number, max_page_number + 1):
    client = request(base_url + str(num))
    page_html = client.read()
    page_soup = soup(page_html, 'html.parser', parse_only=only_item_cells)
    page_soup_list = list(page_soup)
    page_cells.append(page_soup_list)
client.close()

with open('graphics_cards.csv', mode='w', newline='') as graphics_cards_file:
    file_writer = csv.writer(graphics_cards_file)
    file_writer.writerow(['Brand', 'Product Name', 'Price', 'Shipping'])
    for cell in page_cells:
        for html in cell:
            # checking to see if cell is an advertisement, if
            # condition is true, then cell is not an advertisement
            # and we can execute the code below without an error
            if html.find("div", attrs={"class": "txt-ads-link"}) == None:
                try:
                    # obtaining the brand name
                    brand_tag = html.find_all("div", attrs={"class": "item-branding"})
                    brand_name = brand_tag[0].img["title"]

                    # obtaining the product name
                    title_tag = html.find_all("a", attrs={"class": "item-title"})
                    product_name = title_tag[0].text

                    # checking for promo situations (out of stock, limited time offer) 
                    if html.find_all("p", attrs={"class": "item-promo"}) != []:
                        # obtaining the price info
                        promo_tag = html.find_all("p", attrs={"class": "item-promo"})
                        promo_info = promo_tag[0].text

                        if promo_info == "OUT OF STOCK":
                            pricing_info = promo_info
                            shipping_tag = html.find_all("a", attrs={"class": "shipped-by-newegg"})
                            shipping_info = shipping_tag[0].text
                        else: # handles limited time offer
                            price_tag = html.find_all("li", attrs={"class": "price-current"})
                            dollar_sign = price_tag[0].text[0]
                            dollars = price_tag[0].strong.text
                            cents = price_tag[0].sup.text

                            pricing_info = dollar_sign + dollars + cents + ', ' + promo_info

                            shipping_tag = html.find_all("li", attrs={"class": "price-ship"})
                            shipping_info = shipping_tag[0].text
                    else:
                        # obtaining the price info
                        price_tag = html.find_all("li", attrs={"class": "price-current"})
                        dollar_sign = price_tag[0].text[0]
                        dollars = price_tag[0].strong.text
                        cents = price_tag[0].sup.text
                        pricing_info = dollar_sign + dollars + cents

                        # obtaining the shipping info
                        shipping_tag = html.find_all("li", attrs={"class": "price-ship"})
                        shipping_info = shipping_tag[0].text
                    
                    file_writer.writerow([brand_name, product_name, pricing_info, shipping_info])
                except Exception as error:
                    print(f'Error that occurred: {error.__class__.__name__}')
                    print(f'Error message: {error}')
                    print(f'Cell where error occurred: {html}')
                    print()
