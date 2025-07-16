from flask import Flask, redirect
from route.customers import customers_bp
from route.medicines import medicines_bp
from route.sales import sales_bp
import json
from flask import request
from route.suppliers import suppliers_bp
from route.categories import categories_bp

app = Flask(__name__)
app.register_blueprint(customers_bp)
app.register_blueprint(medicines_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(suppliers_bp)
app.register_blueprint(categories_bp)

@app.route("/")
def home():
    return redirect("/medicines")

@app.route('/log_event', methods=['POST'])
def log_event():
    data = request.json
    with open("user_activity_log.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)



