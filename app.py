import os
from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from bs4 import BeautifulSoup
import requests
import re


cred = credentials.Certificate('./saharacoders-88c70-adba549f86b1.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

phone_site = "https://www.gsmarena.com/makers.php3"
phone_brands = [
   
   {
        "name":"Tecno",
        "url":"tecno-phones-120.php"
    },
   
]








@app.route('/get_phones')
def get_phones():
    data = []
    page_no = []
    page_links = []
    phone_dt = []
    for brand in phone_brands:
        page = requests.get(f"https://www.gsmarena.com/{brand['url']}")

        page_links.append({'url':brand['url'],'brand':brand['name']})
        soup = BeautifulSoup(page.content, 'html.parser')

        phones = soup.find('div', {'class': 'nav-pages'})
        for link in phones.findAll('a'):
            page_links.append({'url':link['href'],'brand':brand['name']})

    for item in page_links:
        page = requests.get(f"https://www.gsmarena.com/{item['url']}")
        soup = BeautifulSoup(page.content, 'html.parser')
        brand = soup.find('h1', {'class': 'article-info-name'}).get_text()
        models = soup.find('div', {'class': 'makers'})
        for model in models.findAll('a'):
            model_list = {}
            model_list['brand'] = brand
            model_list['model_name']=item['url']
            model_list['phone_url'] = model['href']
            data.append(model_list)

    # iterating through each and every deice in the array
    for item in data:
        page = requests.get(f"https://www.gsmarena.com/{item['phone_url']}")
        soup = BeautifulSoup(page.content, 'html.parser')
        phone_details = {}
        def chipset():
            try:
                return soup.find('td', {'data-spec': 'cpu'}).get_text()
            except AttributeError as identifier:
                 pass
        

        def internal_m():
            try:
                return soup.find('td', {'data-spec': 'internalmemory'}).get_text()
            except AttributeError as identifier:
                 pass
        phone_details['brand']=item['brand']
        phone_details['image_url'] = soup.find(
            'div', {'class': 'specs-photo-main'}).find('img')['src']
        phone_details['name'] = soup.find(
            'h1', {'class': 'specs-phone-name-title'}).get_text()
        phone_details['release_date'] = soup.find(
            'span', {'data-spec': 'released-hl'}).get_text()
        phone_details['Android OS'] = soup.find(
            'span', {'data-spec': 'os-hl'}).get_text()
        phone_details['storage'] = soup.find(
            'span', {'data-spec': 'storage-hl'}).get_text()
        phone_details['display_size'] = f"{soup.find('span', {'data-spec':'displaysize-hl'}).get_text()} Inch, {soup.find('div', {'data-spec':'displayres-hl'}).get_text()}  "
        phone_details['Battery'] = soup.find(
            'td', {'data-spec': 'batdescription1'}).get_text()
        phone_details['CPU'] = chipset()
        phone_details['Network'] = soup.find('a', {'data-spec': 'nettech'}).get_text()
        phone_details['main_camera'] = soup.find('td', {'data-spec': 'cam1modules'}).get_text()
        phone_details['selfie_camera'] = soup.find('td', {'data-spec': 'cam2modules'}).get_text()
        phone_details['Memory'] = internal_m()
        phone_dt.append(phone_details)

        doc_ref = db.collection(item['brand']).document()
        doc_ref.set(phone_details)
        

    return jsonify(phone_dt)




@app.route('/get_devices/<variable>/')
def get_devices(variable):
    my_devices = {
            "acer":"Acer phones",
            "htc":"HTC phones",
            "infinix":"Infinix phones",
            "alcatel":"alcatel phones",
            "tecno":"TECNO phones"    
            
            }
    
    all_devices = [doc.to_dict() for doc in db.collection(my_devices[f'{variable}']).stream()]
    return jsonify(all_devices)


port = int(os.environ.get("PORT", 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
