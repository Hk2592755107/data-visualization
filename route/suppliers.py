import re
from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from datetime import datetime

suppliers_bp = Blueprint('suppliers_bp', __name__)

def is_valid_contact(contact_number):
    return contact_number.isdigit() and 7 <= len(contact_number) <= 15

def is_valid_email(email):
    if not email:
        return True  # Allow blank
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def format_dt(dt):
    """Format datetime as 'Jul 14, 2025, 07:31 PM' or return empty string."""
    if not dt:
        return ""
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return dt
    return dt.strftime("%b %d, %Y, %I:%M %p")

# ---------- ADD/GET SUPPLIERS ----------
@suppliers_bp.route("/suppliers", methods=["GET", "POST"])
def suppliers():
    db = get_db_connection()
    cursor = db.cursor()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()
        city = request.form.get("city", "").strip()

        # --- Validation ---
        if not name:
            cursor.close(); db.close()
            return jsonify({"error": "Supplier name is required."}), 400
        if not contact_number:
            cursor.close(); db.close()
            return jsonify({"error": "Contact number is required."}), 400
        if not is_valid_contact(contact_number):
            cursor.close(); db.close()
            return jsonify({"error": "Contact number must be 7-15 digits."}), 400
        if email and not is_valid_email(email):
            cursor.close(); db.close()
            return jsonify({"error": "Invalid email address."}), 400

        cursor.execute("SELECT id FROM suppliers WHERE name = %s AND contact_number = %s", (name, contact_number))
        if cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({"error": "Supplier with this name and contact already exists."}), 409

        try:
            cursor.execute("""
                INSERT INTO suppliers (name, contact_number, email, city)
                VALUES (%s, %s, %s, %s)
            """, (name, contact_number, email, city))
            supplier_id = cursor.lastrowid
            db.commit()
            cursor.execute("""
                SELECT id, name, contact_number, email, city, created_at 
                FROM suppliers WHERE id = %s
            """, (supplier_id,))
            supplier = cursor.fetchone()
            cursor.close(); db.close()
            # Format created_at for display (AJAX)
            created_at_str = format_dt(supplier["created_at"]) if supplier else ""
            return jsonify({
                "message": "Supplier added successfully!",
                "supplier": {
                    "id": supplier["id"],
                    "name": supplier["name"],
                    "contact_number": supplier["contact_number"],
                    "email": supplier["email"],
                    "city": supplier["city"],
                    "created_at": created_at_str
                }
            }), 201
        except Exception as e:
            print("Error:", e)
            cursor.close(); db.close()
            return jsonify({"error": "Failed to add supplier."}), 500

    # GET request handling
    cursor.execute("SELECT id, name, contact_number, email, city, created_at FROM suppliers")
    suppliers = cursor.fetchall()
    # Format created_at for table (Jinja)
    for s in suppliers:
        s["created_at_display"] = format_dt(s["created_at"])
    cursor.close(); db.close()
    return render_template("add_suppliers.html", suppliers=suppliers)

# ---------- GET SUPPLIER ----------
@suppliers_bp.route("/get_supplier/<int:supplier_id>")
def get_supplier(supplier_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id=%s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close(); db.close()
    if supplier:
        supplier["created_at"] = format_dt(supplier["created_at"])
        return jsonify(supplier)
    return jsonify({"error": "Not found"}), 404

# ---------- UPDATE SUPPLIER ----------
@suppliers_bp.route("/update_supplier", methods=["POST"])
def update_supplier():
    try:
        id = request.form.get("id")
        name = request.form.get("name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()
        city = request.form.get("city", "").strip()

        # --- Validation ---
        if not name:
            return jsonify({"error": "Supplier name is required."}), 400
        if not contact_number:
            return jsonify({"error": "Contact number is required."}), 400
        if not is_valid_contact(contact_number):
            return jsonify({"error": "Contact number must be 7-15 digits."}), 400
        if email and not is_valid_email(email):
            return jsonify({"error": "Invalid email address."}), 400

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM suppliers WHERE name=%s AND contact_number=%s AND id != %s", (name, contact_number, id))
        if cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({"error": "Another supplier with this name and contact already exists."}), 409

        cursor.execute("""
            UPDATE suppliers
            SET name=%s, contact_number=%s, email=%s, city=%s
            WHERE id=%s
        """, (name, contact_number, email, city, id))
        db.commit()
        cursor.execute("SELECT * FROM suppliers WHERE id=%s", (id,))
        supplier = cursor.fetchone()
        cursor.close(); db.close()
        if supplier:
            supplier["created_at"] = format_dt(supplier["created_at"])
        return jsonify({"supplier": supplier})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- DELETE SUPPLIER ----------
@suppliers_bp.route("/delete_supplier/<int:supplier_id>", methods=["POST"])
def delete_supplier(supplier_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
        db.commit()
        cursor.close(); db.close()
        return jsonify({"message": "Supplier deleted"})
    except Exception as e:
        msg = str(e).lower()
        if "foreign key constraint" in msg or "1451" in msg:
            user_msg = "Cannot delete supplier: It is referenced by one or more medicines."
            return jsonify({"error": user_msg}), 409
        return jsonify({"error": str(e)}), 500
