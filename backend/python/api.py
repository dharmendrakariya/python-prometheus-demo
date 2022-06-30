from flask import Flask
import json
from prometheus_client import Counter, generate_latest


app = Flask(__name__)
data_path = "./data.json"

products_view = {}
products_buy = {}


view_metric = Counter('view', 'Product view', ['product'])
buy_metric = Counter('buy', 'Product buy', ['product'])

@app.route('/product/<product>')
def view_product(product):
    view_metric.labels(product=product).inc()
    try:
        p = load_product(product)
        # Update stats
        if product not in products_view:
            products_view[product] = 1
        else:
            products_view[product] = products_view[product] + 1
        # Add stats
        p['view'] = products_view[product] if product in products_view else 0
        p['buy'] = products_buy[product] if product in products_buy else 0
        headers = {'Content-Type': 'application/json'}
        return json.dumps(p), 200, headers
    except ValueError:
        return "No such product", 404


@app.route('/buy/<product>')
def buy_product(product):
    buy_metric.labels(product=product).inc()
    try:
        p = load_product(product)
        # Update stats
        if product not in products_buy:
            products_buy[product] = 1
        else:
            products_buy[product] = products_buy[product] + 1
        return 'Thanks for buying opensource software ;-)'
    except ValueError:
        return "No such product", 404


def load_product(product):
    with open(data_path, "r") as file:
        json_products = json.loads(file.read())
        for p in json_products['products']:
            if p['name'] == product:
                return p
        raise ValueError('Product %s not found' % product)


@app.route("/")
def products():
    with open(data_path, "r") as file:
        headers = {'Content-Type': 'application/json'}
        return file.read(), 200, headers



# view_metric = Counter('view', 'Product view', ['product'])
# buy_metric = Counter('buy', 'Product buy', ['product'])

# @app.route('/view/<id>')
# def view_product(id):
#     view_metric.labels(product=id).inc()
#     return "View %s" % id

# @app.route('/buy/<id>')
# def buy_product(id):
#     buy_metric.labels(product=id).inc()
#     return "Buy %s" % id

@app.route('/metrics')
def metrics():
    return generate_latest()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
