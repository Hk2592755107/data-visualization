from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from datetime import datetime, date
import traceback

medicines_bp = Blueprint('medicines_bp', __name__)

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except Exception:
        return False

def format_medicine_dates(med):
    # Format created_at
    if med.get("created_at"):
        if isinstance(med["created_at"], (datetime, date)):
            med["created_at"] = med["created_at"].strftime("%b %d, %Y, %I:%M %p")
        else:
            # If it's already a string, do nothing
            pass
    # Format expiry_date
    if med.get("expiry_date"):
        if isinstance(med["expiry_date"], (datetime, date)):
            med["expiry_date"] = med["expiry_date"].strftime("%b %d, %Y")
        else:
            try:
                dt = datetime.strptime(med["expiry_date"], "%Y-%m-%d")
                med["expiry_date"] = dt.strftime("%b %d, %Y")
            except Exception:
                pass
    return med


@medicines_bp.route("/medicines")
def medicines():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT m.id, m.name, m.brand, c.name AS category, m.quantity, m.price, m.expiry_date, s.name AS supplier_name, m.created_at
            FROM medicines m
            JOIN categories c ON m.category_id = c.id
            JOIN suppliers s ON m.supplier_id = s.id
        """)
        medicines = cursor.fetchall()
        medicines = [format_medicine_dates(dict(m)) for m in medicines]

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

@medicines_bp.route("/add_medicines", methods=["POST"])
def add_medicine():
    try:
        name = request.form.get("name", "").strip()
        brand = request.form.get("brand", "").strip()
        category_id = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        price = request.form.get("price", "").strip()
        expiry_date = request.form.get("expiry_date", "").strip()
        supplier_id = request.form.get("supplier_id", "").strip()

        # --- Validation ---
        if not all([name, brand, category_id, quantity, price, expiry_date, supplier_id]):
            return jsonify({"error": "All fields are required."}), 400
        if not quantity.isdigit() or int(quantity) <= 0:
            return jsonify({"error": "Quantity must be a positive integer."}), 400
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Price must be a positive number."}), 400
        if not category_id.isdigit():
            return jsonify({"error": "Invalid category."}), 400
        if not supplier_id.isdigit():
            return jsonify({"error": "Invalid supplier."}), 400
        if not is_valid_date(expiry_date):
            return jsonify({"error": "Invalid expiry date format. Use YYYY-MM-DD."}), 400

        exp_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        if exp_dt.date() < datetime.today().date():
            return jsonify({"error": "Expiry date cannot be in the past."}), 400

        category_id = int(category_id)
        supplier_id = int(supplier_id)
        quantity = int(quantity)
        price = float(price)

        db = get_db_connection()
        cursor = db.cursor()
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
        cursor.execute("""
            SELECT m.id, m.name, m.brand, c.name AS category, m.quantity, m.price, m.expiry_date, m.created_at, s.name AS supplier_name
            FROM medicines m
            JOIN categories c ON m.category_id = c.id
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.id = %s
        """, (medicine_id,))
        med = cursor.fetchone()
        cursor.close()
        db.close()

        med = format_medicine_dates(dict(med))

        return jsonify({
            "id": med['id'],
            "name": med['name'],
            "brand": med['brand'],
            "category": med['category'],
            "quantity": med['quantity'],
            "price": float(med['price']),
            "expiry_date": med['expiry_date'],
            "supplier_name": med['supplier_name'],
            "created_at": med['created_at']
        })
    except Exception as e:
        print("Error inserting/merging medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to add or merge medicine"}), 500

@medicines_bp.route('/get_medicine/<int:med_id>')
def get_medicine(med_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT m.id, m.name, m.brand, m.category_id, c.name AS category, 
               m.quantity, m.price, m.expiry_date, 
               s.name AS supplier_name, m.created_at, m.supplier_id
        FROM medicines m
        JOIN categories c ON m.category_id = c.id
        JOIN suppliers s ON m.supplier_id = s.id
        WHERE m.id = %s
    """, (med_id,))
    med = cursor.fetchone()
    cursor.close()
    db.close()
    if med:
        med = dict(med)
        expiry_val = med.get("expiry_date")
        if isinstance(expiry_val, (datetime, date)):
            med["expiry_date"] = expiry_val.strftime("%Y-%m-%d")
        elif isinstance(expiry_val, str) and len(expiry_val) >= 10 and expiry_val[4] == '-':
            med["expiry_date"] = expiry_val[:10]
        else:
            med["expiry_date"] = ""
        created_val = med.get("created_at")
        if isinstance(created_val, (datetime, date)):
            med["created_at"] = created_val.strftime("%b %d, %Y, %I:%M %p")

        return jsonify(med)
    else:
        return jsonify({"error": "Medicine not found"}), 404



@medicines_bp.route("/update_medicine", methods=["POST"])
def update_medicine():
    try:
        med_id = request.form.get("id", "").strip()
        name = request.form.get("name", "").strip()
        brand = request.form.get("brand", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        price = request.form.get("price", "").strip()
        expiry_date = request.form.get("expiry_date", "").strip()
        supplier_id = request.form.get("supplier_id", "").strip()

        # --- Validation ---
        if not all([med_id, name, brand, category, quantity, price, expiry_date, supplier_id]):
            return jsonify({"error": "All fields are required."}), 400
        if not med_id.isdigit():
            return jsonify({"error": "Invalid medicine ID."}), 400
        if not quantity.isdigit() or int(quantity) < 0:
            return jsonify({"error": "Quantity must be zero or a positive integer."}), 400
        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Price must be zero or a positive number."}), 400
        if not category.isdigit():
            return jsonify({"error": "Invalid category."}), 400
        if not supplier_id.isdigit():
            return jsonify({"error": "Invalid supplier."}), 400
        if not is_valid_date(expiry_date):
            return jsonify({"error": "Invalid expiry date format. Use YYYY-MM-DD."}), 400

        med_id = int(med_id)
        category = int(category)
        supplier_id = int(supplier_id)
        quantity = int(quantity)
        price = float(price)

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE medicines
            SET name=%s, brand=%s, category=%s, quantity=%s, price=%s, expiry_date=%s, supplier_id=%s
            WHERE id=%s
        """, (name, brand, category, quantity, price, expiry_date, supplier_id, med_id))
        db.commit()
        cursor.execute("""
            SELECT m.id, m.name, m.brand, c.name AS category, m.quantity, m.price, m.expiry_date, s.name AS supplier_name, m.created_at
            FROM medicines m
            JOIN categories c ON m.category_id = c.id
            JOIN suppliers s ON m.supplier_id = s.id
            WHERE m.id = %s
        """, (med_id,))
        med = cursor.fetchone()
        cursor.close()
        db.close()

        med = format_medicine_dates(dict(med))
        return jsonify({
            "message": "Medicine updated successfully",
            "medicine": med
        }), 200
    except Exception as e:
        print("Error updating medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to update medicine"}), 500
    
@medicines_bp.route("/delete_medicine/<int:medicine_id>", methods=["POST"])
def delete_medicine(medicine_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM sales_item WHERE medicine_id = %s", (medicine_id,))
        cursor.execute("DELETE FROM medicines WHERE id = %s", (medicine_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Medicine deleted successfully"}), 200
    except Exception as e:
        print("Error deleting medicine:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to delete medicine"}), 500


@medicines_bp.route('/sell_medicine')
def sell_medicine():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT m.id, m.name, m.quantity, m.price, c.name AS category
            FROM medicines m
            LEFT JOIN categories c ON m.category_id = c.id
            WHERE m.quantity > 0
        """)
        medicines = cursor.fetchall()
        cursor.execute("SELECT id, name FROM customers")
        customers = cursor.fetchall()
        cursor.execute("SELECT id, name FROM categories")
        categories = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template(
            medicines=medicines,
            customers=customers,
            categories=categories
        )
    except Exception as e:
        print("Error loading sell medicine page:", e)
        traceback.print_exc()
        return "Database error", 500

@medicines_bp.route('/sell_medicine', methods=['POST'])
def process_sale():
    try:
        data = request.get_json(force=True) 
        customer_id = data.get('customer_id')
        items = data.get('items', [])

        # --- Validation ---
        if not customer_id or not str(customer_id).isdigit():
            return jsonify({"error": "Customer is required."}), 400
        if not items or not isinstance(items, list) or len(items) == 0:
            return jsonify({"error": "At least one item must be selected."}), 400

        db = get_db_connection()
        cursor = db.cursor()
        total_amount = 0

        for idx, item in enumerate(items):
            try:
                medicine_id = int(item.get('medicine_id'))
                quantity = int(item.get('quantity'))
                discount = float(item.get('discount', 0))
            except Exception as ex:
                return jsonify({"error": f"Invalid data format for item {idx+1}: {ex}"}), 400

            if medicine_id <= 0:
                return jsonify({"error": f"Invalid medicine ID (item {idx+1})."}), 400
            if quantity <= 0:
                return jsonify({"error": f"Quantity must be positive (item {idx+1})."}), 400
            if not (0 <= discount <= 100):
                return jsonify({"error": f"Discount must be between 0 and 100 (item {idx+1})."}), 400

            cursor.execute("SELECT name, price, quantity AS stock FROM medicines WHERE id = %s", (medicine_id,))
            med = cursor.fetchone()
            if not med:
               return jsonify({"error": f"Medicine not found"}), 404
            if med['stock'] is None or int(med['stock']) < quantity:
                return jsonify({"error": f"Insufficient stock for medicine: {med['name']}"}), 400


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

        for item in items:
            medicine_id = int(item['medicine_id'])
            quantity = int(item['quantity'])
            discount = float(item.get('discount', 0))

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
            cursor.execute("SELECT quantity FROM medicines WHERE id = %s", (medicine_id,))
            quantity = cursor.fetchone()['quantity'] 
            
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Sale completed successfully!", "sale_id": sale_id,"quantity":quantity,"medicine_id":medicine_id  }), 201

    except Exception as e:
        print("Error processing sale:", e)
        traceback.print_exc()
        return jsonify({"error": f"Failed to process sale: {str(e)}"}), 500


