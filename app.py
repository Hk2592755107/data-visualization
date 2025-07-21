from flask import Flask, redirect
from route.customers import customers_bp
from route.medicines import medicines_bp
from route.sales import sales_bp
import json
import requests
from flask import request
from route.suppliers import suppliers_bp
from route.categories import categories_bp
from route.user_activity import user_activity_bp
from user_info import user_info_bp

app = Flask(__name__)
app.register_blueprint(customers_bp)
app.register_blueprint(medicines_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(suppliers_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(user_activity_bp)
app.register_blueprint(user_info_bp)



@app.route("/")
def home():
    return redirect("/medicines")



import requests

@app.route('/log_event', methods=['POST'])
def log_event():
    data = request.json
    ip = data.get('details', {}).get('ip') or request.remote_addr

    # # Only fetch geo info if not already present
    # if not all(k in data['details'] for k in ['country', 'region', 'city', 'timezone']):
    #     try:
    #         geo = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,timezone").json()
    #         if geo.get("status") == "success":
    #             data['details']['country']  = geo.get('country',    '-')
    #             data['details']['region']   = geo.get('regionName', '-')
    #             data['details']['city']     = geo.get('city',       '-')
    #             data['details']['timezone'] = geo.get('timezone',   '-')
    #         else:
    #             data['details']['country'] = data['details']['region'] = data['details']['city'] = data['details']['timezone'] = '-'
    #     except Exception:
    #         data['details']['country'] = data['details']['region'] = data['details']['city'] = data['details']['timezone'] = '-'

    with open("user_activity_log.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
    return '', 204




if __name__ == "__main__":
    app.run(debug=True)



