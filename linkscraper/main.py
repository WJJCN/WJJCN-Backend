from datetime import datetime
from typing import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import pymongo
import sys
import re
import certifi

ca = certifi.where()

brands = []
products = []
internal_urls = set()
read_links = []
to_scrape = set()
not_found = set()
products_with = []
products_with2 = []
retailers = []
brands_with = []

domain_url = ""

first_url = ""
total_urls_visited = 0
timeout_counter = 0

timeout_retry = 15
request_timeout_in_seconds = 5

''' 
    WEBCRAWLER
'''


def is_valid(url):
    # Checks whether `url` is a valid URL.
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def check_if_url_starts_with_domain(domain, linke):
    global new_domain
    global new_link

    new_domain = domain
    new_link = linke

    if "https://" in new_domain or "https://" in new_link:
        new_domain = new_domain.replace("https://", "")
        new_link = new_link.replace("https://", "")

    if "www." in new_domain or "www." in new_link:
        new_domain = new_domain.replace("www.", "")
        new_link = new_link.replace("www.", "")

    result = re.findall(new_domain, new_link)
    if result != []:
        return True
    else:
        return False


def pause_and_resume_script():
    print("Pausing program \nPlease press enter")
    global timeout_counter

    run = True
    while run == True:
        try:
            # Loop Code Snippet
            val = input()
            val = int(val)
        except ValueError:
            print("""~~~~~~~Code interrupted~~~~~~~ \n Press 1 to resume \n Press 2 to quit """)
            res = input()
            if res == "1":
                timeout_counter = 0
                print("resuming code")
                run = False
            if res == "2":
                sys.exit()


def get_url(url):
    global timeout_counter
    counter = timeout_counter

    html = requests

    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    if counter != timeout_retry:
        try:
            html = requests.get(url, headers=agent, timeout=request_timeout_in_seconds).text

            if html != requests:
                soup = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
                return soup
            else:
                get_url(url)
        except:
            print("An error occurred. Please check your internet connection.")
            counter += 1
            timeout_counter = counter
            get_url(url)
    else:
        pause_and_resume_script()
        timeout_counter = 0
        get_url(url)

        if html != requests:
            soup = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
            return soup
        else:
            get_url(url)


# the method below calls a few methods above to find all links on a page and then checks if they are valid
def get_all_website_links(url):
    if "<" not in str(url):
        # all URLs of on url that is being checked
        urls = set()

        soup = get_url(url)

        try:
            # A loop that loops over all a tags on the webpage that is being checked and then finds all href tags
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")

                if href == "" or href is None:
                    continue
                if href.startswith("#"):
                    continue
                if "https://" not in href:
                    if not href.startswith("/"):
                        href = "/" + href
                if "https://www." not in href:
                    if "https://" not in href:
                        if not href.startswith("/"):
                            href = "/" + href

                href = urljoin(url, href)
                # checks if the given url starts with the correct domain else it goes to the next link on the page
                if not check_if_url_starts_with_domain(first_url, href):
                    continue
                # if the url doesn't end with a "/" an "/" will be added to the link
                if not href.endswith("/"):
                    href = href + "/"
                # if the url starts with a space (" ") it will remove the space (" ") form the url
                if href.startswith(" "):
                    href = href.lstrip(' ')
                # if the url contains a query of contains "tel:" it'll be skipped, and it'll go to the next link on the page
                if "#" in href or "tel:" in href:
                    continue
                # if the url already has been scraped it'll be skipped, and it'll go to the next link on the page
                if href in internal_urls:
                    continue
                # a second check to see if the found link does start with the domain, then we'll add the link to the found
                # internal links set
                if check_if_url_starts_with_domain(first_url, href):
                    urls.add(href)
                    internal_urls.add(href)
                # if the found link starts with an "/" we'll add the domain url so every link is a correct link, and we
                # don't have to check where the link came form
                if href.startswith("/"):
                    href = domain_url + href
                    urls.add(href)
                    internal_urls.add(href)
                continue
        except AttributeError:
            print("Could not crawl the given URL.")
    return urls


def crawl(url):
    global domain_url
    global domain_name

    # if statement finds the "main" link, it strips all tags after .com
    if domain_url == "":
        stripped_domain = re.findall("(\w+://[\w\-\.]+)", url)
        domain_url = stripped_domain[0]

    # finds the domain name, it strips https from the url to just get the domain (ex https://www.google.com/ -> google.com)
    domain_name = re.match(r'(?:\w*://)?(?:.*\.)?([a-zA-Z-1-9]*\.[a-zA-Z]{1,}).*', url).groups()[0]

    # after finding the domain name it changes . to - to remove conflict in saving it in the explorer
    if "." in domain_name:
        domain_name = domain_name.replace(".", "-")

    global total_urls_visited
    total_urls_visited += 1

    links = get_all_website_links(url)

    print(f"[*] Crawling: {url}")

    for link in links:
        # if total_urls_visited > 200:
        #    break
        if check_if_url_starts_with_domain(url, link):
            crawl(link)
        else:
            continue


''' 
    END WEBCRAWLER
'''


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def find_product_in_urls(url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    selected_retailer = ""
    selected_retailer_url = ""
    selected_brand = ""
    brand_temp_list = []

    with client:
        db = client.wjjcn
        b = db.retailers.find()

        for item in b:
            if item['base_url'] in url:
                selected_retailer = item['_id']
                selected_retailer_url = item['base_url']
                retailers.append(item['base_url'])

        e = db.products.find({"retailer": selected_retailer})

        for item in e:
            if item['retailer'] == selected_retailer:
                brand_temp_list.append(item['brand'])
                # item['product'] = item['product'].split(" -", 1)[0]
                item['product'] = re.sub(' +', '-', item['product'])
                item['product'] = re.sub('-+', '-', item['product'])
                products.append(item['product'])

        a = db.brands.find()

        for brand in a:
            for bra in brand_temp_list:
                if brand["_id"] == bra:
                    brands.append(brand["name"])

    with open('linksjumbo-com.txt') as f:
        for line in f.readlines():
            read_links.append(line.strip())

        f.close()

    for link in internal_urls:
        read_links.append(link)

    for j in range(len(list(read_links))):
        i = 0
        while i < len(list(products)):
            if check_if_url_starts_with_domain(selected_retailer_url, read_links[j]):
                products_with.append(products[i])
                split_link = read_links[j].split("/")
                filtered_link = list(filter(None, split_link))

                for x in range(len(filtered_link)):

                    for b in range(len(brands)):
                        brands_with.append(brands[b].replace(" ", "-"))

                        if brands_with[b].lower() in filtered_link[x]:
                            # regexMatch = '(' + products[i].lower() + ')(.*)'
                            # result = re.match(regexMatch, filtered_link[x])
                            # if result:
                                correct_count = 0
                                percentage = 80

                                product_in_database = products_with[i].lower().split("-")
                                found_product_url = filtered_link[x].split("-")

                                # for remo in range(len(found_product_url)):
                                #     if 'BLK' in found_product_url[remo] or 'PAK' in found_product_url[remo] or 'TRL' in found_product_url[remo]:
                                #         del found_product_url[remo]

                                for p in range(len(product_in_database)):
                                    for p2 in range(len(found_product_url)):
                                        if product_in_database[p] in found_product_url[p2]:
                                            # if product_in_database[p] == found_product_url[p2]:
                                            correct_count += 1
                                            if correct_count == len(product_in_database):
                                                if has_numbers(found_product_url[-1]):
                                                    percentage = 72
                                                if (len(product_in_database) / len(found_product_url)) * 100 > percentage:
                                                    to_scrape.add(read_links[j])
                                                    break
                                                break
            i += 1
            # else:
            #     not_found.add(products[i] + " not found")

    if len(to_scrape) > 0:
        for product_url in to_scrape:
            print(product_url)
    else:
        print("No products found in the scraped URL's...")


def clear_lists():
    internal_urls.clear()
    read_links.clear()
    to_scrape.clear()
    products_with.clear()
    brands_with.clear()


''' 
    PROGRAM
'''


def main():
    try:
        print("-- Enter the URL you want to crawl --")
        clear_lists()
        enter_url = input()

        if enter_url != "":
            try:

                first_url = enter_url
                start_time = datetime.now()

                crawl(first_url)

                print("[/---------------------------/]")
                print(len(internal_urls))
                print("[/---------------------------/]")

                with open('links' + domain_name + '.txt', 'w') as f:
                    for link in internal_urls:
                        print("found link: ", link)
                        f.write(link)
                        f.write('\n')

                f.close()

                print("[+] Total links:", len(internal_urls))

                end_time = datetime.now()
                print('Duration: {}'.format(end_time - start_time))

                find_product_in_urls(first_url)
            except:
                print("link is not valid")
            finally:
                main()

        if enter_url == "":
            sys.exit()
    except ValueError:
        sys.exit()


''' 
    END PROGRAM
'''

# main()
find_product_in_urls("https://www.jumbo.com/producten")