from flask import Flask, render_template, request, redirect, jsonify
import pymysql
from datetime import datetime, date
import traceback
app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="medical_store",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return redirect("/medicines")

# --------------------- MEDICINES CRUD ------------------------

@app.route("/medicines")
def medicines():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT m.id, m.name, m.brand, m.category, m.quantity, m.price, m.expiry_date, s.name AS supplier_name
            FROM medicines m
            JOIN suppliers s ON m.supplier_id = s.id
        """)
        medicines = cursor.fetchall()

        cursor.execute("SELECT id, name FROM suppliers")
        suppliers = cursor.fetchall()


        cursor.execute("SELECT id, name FROM customers")
        customers = cursor.fetchall()

        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template("medicines.html", medicines=medicines, suppliers=suppliers, customers=customers, categories=categories)

    except Exception as e:
        print("Error fetching medicines data:", e)
        traceback.print_exc()
        return "Database error", 500
    
@app.route("/add_medicines", methods=["POST"])
def add_medicine():
    try:
        name = request.form["name"]
        brand = request.form["brand"]
        category_id = int(request.form["category"])   # <-- now category is id, not name!
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        expiry_date = request.form["expiry_date"]
        supplier_id = int(request.form["supplier_id"])

        db = get_db_connection()
        cursor = db.cursor()

        # Check if medicine already exists (with this category_id)
        cursor.execute("""
            SELECT id, quantity FROM medicines
            WHERE name = %s AND brand = %s AND category_id = %s AND price = %s
              AND expiry_date = %s AND supplier_id = %s
        """, (name, brand, category_id, price, expiry_date, supplier_id))
        existing = cursor.fetchone()

        if existing:
            new_quantity = existing['quantity'] + quantity
            cursor.execute("UPDATE medicines SET quantity = %s WHERE id = %s", (new_quantity, existing['id']))
            medicine_id = existing['id']
        else:
            cursor.execute("""
                INSERT INTO medicines (name, brand, category_id, quantity, price, expiry_date, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, brand, category_id, quantity, price, expiry_date, supplier_id))
            medicine_id = cursor.lastrowid

        db.commit()

        # Fetch medicine with category name and supplier name
        cursor.execute("""
            SELECT m.id, m.name, m.brand, c.name AS category, m.quantity, m.price, m.expiry_date, s.name AS supplier_name
            FROM medicines m
            JOIN categories c ON m.category_id = c.id
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.id = %s
        """, (medicine_id,))
        med = cursor.fetchone()
        cursor.close()
        db.close()

        expiry_date_val = med['expiry_date']
        if isinstance(expiry_date_val, (datetime, date)):
            expiry_date_str = expiry_date_val.strftime("%Y-%m-%d")
        else:
            expiry_date_str = str(expiry_date_val)
        
        return jsonify({
            "id": med['id'],
            "name": med['name'],
            "brand": med['brand'],
            "category": med['category'],  # this is now the category NAME from the join
            "quantity": med['quantity'],
            "price": float(med['price']),
            "expiry_date": expiry_date_str,
            "supplier_name": med['supplier_name']
        })

    except Exception as e:
        print("Error inserting/merging medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to add or merge medicine"}), 500



@app.route('/get_medicine/<int:med_id>')
def get_medicine(med_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, name, brand, category_id, quantity, price, expiry_date, supplier_id
        FROM medicines WHERE id = %s
    """, (med_id,))
    med = cursor.fetchone()
    cursor.close()
    db.close()
    if med:
        expiry_date = med['expiry_date']
        if isinstance(expiry_date, (datetime, date)):
            expiry_date = expiry_date.strftime("%Y-%m-%d")
        return jsonify({
            'id': med['id'],
            'name': med['name'],
            'brand': med['brand'],
            'category': med['category_id'],  # This is id!
            'quantity': med['quantity'],
            'price': float(med['price']),
            'expiry_date': expiry_date,
            'supplier_id': med['supplier_id']
        })
    else:
        return jsonify({"error": "Medicine not found"}), 404



@app.route("/update_medicine", methods=["POST"])
def update_medicine():
    try:
        med_id = int(request.form["id"])
        name = request.form["name"]
        brand = request.form["brand"]
        category = request.form["category"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        expiry_date = request.form["expiry_date"]
        supplier_id = int(request.form["supplier_id"])

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE medicines
            SET name=%s, brand=%s, category=%s, quantity=%s, price=%s, expiry_date=%s, supplier_id=%s
            WHERE id=%s
        """, (name, brand, category, quantity, price, expiry_date, supplier_id, med_id))
        db.commit()

        # Fetch updated medicine data with supplier name
        cursor.execute("""
            SELECT m.id, m.name, m.brand, m.category, m.quantity, m.price, m.expiry_date, s.name AS supplier_name
            FROM medicines m
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.id = %s
        """, (med_id,))
        med = cursor.fetchone()
        cursor.close()
        db.close()

        expiry_date_val = med['expiry_date']
        if isinstance(expiry_date_val, (datetime, date)):
            expiry_date_str = expiry_date_val.strftime("%Y-%m-%d")
        else:
            expiry_date_str = str(expiry_date_val)

        return jsonify({
            "message": "Medicine updated successfully",
            "medicine": {
                "id": med['id'],
                "name": med['name'],
                "brand": med['brand'],
                "category": med['category'],
                "quantity": med['quantity'],
                "price": float(med['price']),
                "expiry_date": expiry_date_str,
                "supplier_name": med['supplier_name']
            }
        }), 200
    except Exception as e:
        print("Error updating medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to update medicine"}), 500

@app.route("/delete_medicine/<int:medicine_id>", methods=["POST"])
def delete_medicine(medicine_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # First delete from sales_item
        cursor.execute("DELETE FROM sales_item WHERE medicine_id = %s", (medicine_id,))
        
        # Then delete the medicine
        cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Medicine deleted successfully"}), 200
    except Exception as e:
        print("Error deleting medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to delete medicine"}), 500


@app.route('/sell_medicine')
def sell_medicine():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Join with categories to get category name
        cursor.execute("""
            SELECT m.id, m.name, m.quantity, m.price, c.name AS category
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            WHERE m.quantity > 0
        """)
        medicines = cursor.fetchall()

        # Get customers
        cursor.execute("SELECT id, name FROM customers")
        customers = cursor.fetchall()

        # Get categories (if you want to show a category dropdown)
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            'sell_medicine.html',
            medicines=medicines,
            customers=customers,
            categories=categories
        )
    except Exception as e:
        print("Error loading sell medicine page:", e)
        traceback.print_exc()
        return "Database error", 500



@app.route('/sell_medicine', methods=['POST'])
def process_sale():
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        items = data.get('items', [])

        if not customer_id or not items:
            return jsonify({"error": "Missing customer or items"}), 400

        db = get_db_connection()
        cursor = db.cursor()

        total_amount = 0

        # Validate and calculate total
        for item in items:
            medicine_id = item['medicine_id']
            quantity = item['quantity']
            discount = item.get('discount', 0)

            cursor.execute("SELECT price, quantity AS stock FROM medicines WHERE id = %s", (medicine_id,))
            med = cursor.fetchone()

            if not med:
                return jsonify({"error": f"Medicine ID {medicine_id} not found"}), 404

            if med['stock'] < quantity:
                return jsonify({"error": f"Insufficient stock for medicine ID {medicine_id}"}), 400

            price = float(med['price'])
            amount = price * quantity
            total_price = amount * (1 - discount / 100)
            total_amount += total_price

        # Insert into sales table
        cursor.execute(
            "INSERT INTO sales (customer_id, total_amount) VALUES (%s, %s)",
            (customer_id, total_amount)
        )
        sale_id = cursor.lastrowid

        # Insert sale items and update stock
        for item in items:
            medicine_id = item['medicine_id']
            quantity = item['quantity']
            discount = item.get('discount', 0)

            cursor.execute("SELECT price FROM medicines WHERE id = %s", (medicine_id,))
            price = float(cursor.fetchone()['price'])
            amount = price * quantity
            total_price = amount * (1 - discount / 100)

            cursor.execute("""
                INSERT INTO sales_item (sale_id, medicine_id, quantity, price, discount, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sale_id, medicine_id, quantity, price, discount, total_price))

            cursor.execute("""
                UPDATE medicines SET quantity = quantity - %s WHERE id = %s
            """, (quantity, medicine_id))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Sale completed successfully!"})

    except Exception as e:
        print("Error processing sale:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to process sale"}), 500

@app.route("/categories")
def get_categories():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM categories WHERE name IS NOT NULL AND name != ''")
    categories = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return jsonify(categories)




@app.route("/add_category", methods=["POST"])
def add_category():
    try:
        category_name = request.form.get("name") 
        if not category_name:
            return jsonify({"error": "Category name is required"}), 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Category already exists"}), 409

        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
        db.commit()
        category_id = cursor.lastrowid

        cursor.close()
        db.close()

        return jsonify({"message": "Category added", "id": category_id, "name": category_name}), 201

    except Exception as e:
        print("Error adding category:", e)
        return jsonify({"error": "Failed to add category"}), 500



@app.route('/sale/<int:sale_id>')
def sale_details(sale_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

      
        cursor.execute("""
            SELECT s.id, s.date, s.total_amount,
                   c.name AS customer_name, c.contact_number, c.email
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.id = %s
        """, (sale_id,))
        sale = cursor.fetchone()

        if not sale:
            return "Sale not found", 404

        # Fetch sale items
        cursor.execute("""
            SELECT si.quantity, si.price, si.discount, si.total_price,
                   m.name AS medicine_name
            FROM sales_item si
            JOIN medicines m ON si.medicine_id = m.id
            WHERE si.sale_id = %s
        """, (sale_id,))
        items = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template("sale_details.html", sale=sale, items=items)

    except Exception as e:
        print("Error loading sale details:", e)
        traceback.print_exc()
        return "Error loading sale details", 500

@app.route("/sales_history")
def sales_history():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT s.id, s.date, s.total_amount,
                   c.name AS customer_name
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            ORDER BY s.date DESC
        """)
        sales = cursor.fetchall()
        cursor.close()
        db.close()

        return render_template("sales_history.html", sales=sales)

    except Exception as e:
        print("Error loading sales history:", e)
        traceback.print_exc()
        return "Database error", 500


@app.route("/suppliers", methods=["GET", "POST"])
def suppliers():
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        try:
            name = request.form.get("name")
            contact_number = request.form.get("contact_number")
            email = request.form.get("email", "")
            city = request.form.get("city", "")

            if not name or not contact_number:
                return "Name and contact number required", 400

            cursor.execute("""
                INSERT INTO suppliers (name, contact_number, email, city)
                VALUES (%s, %s, %s, %s)
            """, (name, contact_number, email, city))
            db.commit()
        except Exception as e:
            print("Error:", e)
            return "Failed to add supplier", 500

    cursor.execute("SELECT id, name, contact_number, email, city FROM suppliers")
    suppliers = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("add_suppliers.html", suppliers=suppliers)


# --------------------- CUSTOMERS CRUD ------------------------

@app.route("/customers")
def customers():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, contact_number, email FROM customers")
        customers = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("customers.html", customers=customers)
    except Exception as e:
        print("Error fetching customers:", e)
        traceback.print_exc()
        return "Database error", 500


@app.route("/add_customer", methods=["POST"])
def add_customer():
    try:
        name = request.form["name"]
        contact_number = request.form["contact_number"]
        email = request.form.get("email", "")

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO customers (name, contact_number, email)
            VALUES (%s, %s, %s)
        """, (name, contact_number, email))
        db.commit()

        customer_id = cursor.lastrowid

        cursor.execute("SELECT id, name, contact_number, email FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        db.close()

        return jsonify({
            "message": "Customer added successfully",
            "customer": customer
        }), 201

    except Exception as e:
        print("Error adding customer:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to add customer"}), 500


@app.route("/get_customer/<int:customer_id>")
def get_customer(customer_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, contact_number, email FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        db.close()

        if customer:
            return jsonify(customer)
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        print("Error fetching customer:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/update_customer", methods=["POST"])
def update_customer():
    try:
        customer_id = int(request.form["id"])
        name = request.form["name"]
        contact_number = request.form["contact_number"]
        email = request.form.get("email", "")

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE customers
            SET name = %s, contact_number = %s, email = %s WHERE id = %s
        """, (name, contact_number, email, customer_id))
        db.commit()

        cursor.execute("SELECT id, name, contact_number, email FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        cursor.close()
        db.close()

        return jsonify({
            "message": "Customer updated successfully",
            "customer": customer
        }), 200
    except Exception as e:
        print("Error updating customer:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to update customer"}), 500

@app.route("/delete_customer/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        print("Error deleting customer:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to delete customer"}), 500

if __name__ == "__main__":
    app.run(debug=True)
