from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = 'dev'

# In-memory product catalog with categories, subcategories, images, and delivery
PRODUCTS = [
    # Patike - Yeezy
    {
        'id': 1,
        'name': 'Yeezy Boost 350 V2 (Cinder)',
        'price': 230,
        'category': 'Patike',
        'subcategory': 'Yeezy',
        'image': 'https://stockx.imgix.net/images/Adidas-Yeezy-Boost-350-V2-Cinder-Product.jpg?fit=fill&bg=FFFFFF&w=700&h=500&auto=format,compress&q=90&dpr=2&trim=color&updated_at=1606321670',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Sve godine',
        'description': 'Premium Kanye West dizajn. Ultralagane i udobne sa Boost tehnologijom. Čekan model za kolekcionare i ljubitelje sneakera.',
    },
    {
        'id': 2,
        'name': 'Yeezy Boost 350 V2 (Static)',
        'price': 235,
        'category': 'Patike',
        'subcategory': 'Yeezy',
        'image': 'https://stockx.imgix.net/images/Adidas-Yeezy-Boost-350-V2-Zebra-Product-1.jpg?fit=fill&bg=FFFFFF&w=700&h=500&auto=format,compress&q=90&dpr=2&trim=color&updated_at=1606321670',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Sve godine',
        'description': 'Kultna verzija sa static obrascem. Moderna i udobna, idealno za svakodnevnu nošnju i događaje.',
    },
    # Patike - Jordan
    {
        'id': 3,
        'name': 'Jordan 1 Retro High OG (Chicago)',
        'price': 280,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://picsum.photos/400/400?random=3',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Legedarna NBA patika. Ikoničan crveno-belo-crni dizajn. Savršena za basketball ili street style.',
    },
    {
        'id': 4,
        'name': 'Jordan 1 Retro High OG (Bred)',
        'price': 260,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://picsum.photos/400/400?random=4',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Klasična "Bred" verzija. Crven i crn detalj sa premium kožom. Investicija za svakog sneaker hedera.',
    },
    # Patike - Nike
    {
        'id': 5,
        'name': 'Nike Air Force 1 Low (White)',
        'price': 120,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://picsum.photos/400/400?random=5',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Veikovni klasik. Čista bela boja, minimalističan dizajn. Savršena za bilo koji outfit, od casual do formal.',
    },
    {
        'id': 6,
        'name': 'Nike Air Max 90 (Crna)',
        'price': 130,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://picsum.photos/400/400?random=6',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Klasičan Air Max sa vidljiv Air jastuku. Odličan za proleće i jesen, udoban ceo dan.',
    },
    # Patike - Adidas
    {
        'id': 16,
        'name': 'Adidas Ultraboost 21 (Crna)',
        'price': 150,
        'category': 'Patike',
        'subcategory': 'Adidas',
        'image': 'https://picsum.photos/400/400?random=7',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Premium Boost tehnologija. Savršena za trčanje ili casual nošnju. Laganost i podrška su osigurani.',
    },
    {
        'id': 17,
        'name': 'Adidas Ultraboost 21 (Bela)',
        'price': 150,
        'category': 'Patike',
        'subcategory': 'Adidas',
        'image': 'https://brand.assets.adidas.com/capi/enUS/Images/seo-what-is-boost-body-image-2_221-620467.jpg',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Čista bela verzija za minimaliste. Elegantna za sve godišnje doba. Popularna kod fashion influensera.',
    },
    {
        'id': 18,
        'name': 'Nike React (Žuta)',
        'price': 130,
        'category': 'Patike',
        'subcategory': 'Nike',
        'image': 'https://picsum.photos/400/400?random=9',
        'delivery': '2-4 days',
        'type': 'Muške',
        'season': 'Leto/Proleće',
        'description': 'Neona žuta za letnje dane. Lagana React potplata. Idealno za fitness ili šetnje u toplije vreme.',
    },
    {
        'id': 19,
        'name': 'Jordan 4 (Siva)',
        'price': 200,
        'category': 'Patike',
        'subcategory': 'Jordan',
        'image': 'https://picsum.photos/400/400?random=10',
        'delivery': '2-4 days',
        'type': 'Muške/Ženske',
        'season': 'Sve godine',
        'description': 'Retro Jordan 4 sa sivim tonom. Trapez detaljima i Jumpman logotipom. Ozbiljna kolekcionarska vrednost.',
    },
    # Patike - Nsport/Buzz/Djak
    {
        'id': 20,
        'name': 'Nsport Turbo Runner',
        'price': 110,
        'category': 'Patike',
        'subcategory': 'Nsport',
        'image': 'https://picsum.photos/400/400?random=11',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Brzi i lagani za trčanje. Airflow ventilacija. Odličan omjer cene i kvalitete.',
    },
    {
        'id': 21,
        'name': 'Buzz Street Runner',
        'price': 105,
        'category': 'Patike',
        'subcategory': 'Buzz',
        'image': 'https://picsum.photos/400/400?random=12',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Urbano dizajnirano za street style. Čvrst potključ, fleksibilna fleksija. Popularna na društvenim mrežama.',
    },
    {
        'id': 22,
        'name': 'Djak Sneaker Classic',
        'price': 95,
        'category': 'Patike',
        'subcategory': 'Djak',
        'image': 'https://picsum.photos/400/400?random=13',
        'delivery': '2-4 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Pristupačna cena, solidna kvaliteta. Svestriana patika za školu, posao ili druženja.',
    },
    # Odeća - Majice
    {
        'id': 7,
        'name': 'Grafička majica (Crna)',
        'price': 25,
        'category': 'Odeća',
        'subcategory': 'Majice',
        'image': 'https://picsum.photos/400/400?random=14',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Kaotična grafika na crnom pamuku. Vega za letnje dane. Lagana i prozračna.',
    },
    {
        'id': 8,
        'name': 'Grafička majica (Bela)',
        'price': 17,
        'category': 'Odeća',
        'subcategory': 'Majice',
        'image': 'https://picsum.photos/400/400?random=15',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Minimalni dizajn na beloj majici. Kombinuje se sa sve. Osnovni komad garderobe.',
    },
    # Odeća - Dukserice
    {
        'id': 9,
        'name': 'Dukserica (Siva)',
        'price': 40,
        'category': 'Odeća',
        'subcategory': 'Dukserice',
        'image': 'https://picsum.photos/400/400?random=16',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Jesen/Zima',
        'description': 'Topla i udobna siva dukserica. Savršena za hladnije dane. Džepovi sa zatvaračem.',
    },
    {
        'id': 12,
        'name': 'Dukserica (Crna)',
        'price': 40,
        'category': 'Odeća',
        'subcategory': 'Dukserice',
        'image': 'https://picsum.photos/400/400?random=17',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Jesen/Zima',
        'description': 'Klasična crna dukserica za svaki outfit. Debela i izdržljiva. Odličnog kvaliteta.',
    },
    # Odeća - Pantalone
    {
        'id': 13,
        'name': 'Pantalone (Plave)',
        'price': 35,
        'category': 'Odeća',
        'subcategory': 'Pantalone',
        'image': 'https://picsum.photos/400/400?random=18',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Moderne plave pantalone sa fleksibilnim pamуkom. Udobne za ceo dan. Moderne boje.',
    },
    {
        'id': 14,
        'name': 'Šorcevi (Crni)',
        'price': 30,
        'category': 'Odeća',
        'subcategory': 'Šorcevi',
        'image': 'https://picsum.photos/400/400?random=19',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Leto',
        'description': 'Lagani letnji šorcevi sa elastičnom pojasom. Odlični za plažu i sport. Brzo se suše.',
    },
    # Nakit - Ogrlice
    {
        'id': 10,
        'name': 'Srebrna ogrlica',
        'price': 60,
        'category': 'Nakit',
        'subcategory': 'Ogrlice',
        'image': 'https://picsum.photos/400/400?random=20',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Elegantna srebrna ogrlica sa minimalnim dizejalnom. Savršena za svečane prilike.',
    },
    {
        'id': 15,
        'name': 'Narukvica (Koža)',
        'price': 45,
        'category': 'Nakit',
        'subcategory': 'Narukvice',
        'image': 'https://picsum.photos/400/400?random=21',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Ručno savijena pravoj kože narukvica. Dugovečna i udobna. Poveća se vremenom.',
    },
    {
        'id': 11,
        'name': 'Zlatni prsten',
        'price': 90,
        'category': 'Nakit',
        'subcategory': 'Prstenovi',
        'image': 'https://picsum.photos/400/400?random=22',
        'delivery': '1-3 days',
        'type': 'Uniseks',
        'season': 'Sve godine',
        'description': 'Premium zlatni prsten sa sitnim detaljima. Komad koji vrijednosti raste. Savršen poklon.',
    },
]

# Mock vendor API endpoint (would be actual URLs in real app)
VENDOR_API_URL = 'https://example-vendor.com/api/order'

@app.route('/')
def index():
    # category and subcategory filters
    category = request.args.get('category')
    subcat = request.args.get('subcategory')

    filtered = PRODUCTS
    if category:
        filtered = [p for p in filtered if p['category'] == category]
    if subcat:
        filtered = [p for p in filtered if p.get('subcategory') == subcat]

    # build category->subcategories mapping
    categories = {}
    for p in PRODUCTS:
        cat = p['category']
        sub = p.get('subcategory') or 'All'
        categories.setdefault(cat, set()).add(sub)
    # sort subcategories and convert to list
    categories = {cat: sorted(subs) for cat, subs in categories.items()}

    return render_template(
        'index.html',
        products=filtered,
        categories=categories,
        selected_category=category,
        selected_subcategory=subcat,
    )

@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        flash('Product not found')
        return redirect(url_for('index'))
    if request.method == 'POST':
        customer = {
            'name': request.form['name'],
            'address': request.form['address'],
            'phone': request.form['phone'],
        }
        # Here we would process payment; skipping for now
        # Simulate vendor order
        success = place_vendor_order(product, customer)
        if success:
            flash('Order placed successfully!')
            return redirect(url_for('index'))
        else:
            flash('Vendor order failed.')
            return redirect(url_for('order', product_id=product_id))
    return render_template('order.html', product=product)


def place_vendor_order(product, customer):
    # In a real implementation we would POST to vendor API with auth and data.
    # Here we just print to console and pretend it succeeded.
    print(f"Placing vendor order for {product['name']} to {customer}")
    # Example of what you might do with requests:
    # resp = requests.post(VENDOR_API_URL, json={
    #     'product_id': product['id'],
    #     'quantity': 1,
    #     'delivery': customer
    # })
    # return resp.status_code == 200
    return True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
