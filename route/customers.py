import re
import traceback
from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
from datetime import datetime

customers_bp = Blueprint('customers_bp', __name__)

def is_valid_name(name):
    # Only letters and spaces, must start and end with a letter, at least two characters, no double spaces
    pattern = r"^[A-Za-z]+(?: [A-Za-z]+)*$"
    return bool(re.match(pattern, name.strip()))

def format_created_at(cust):
    if cust and "created_at" in cust and cust["created_at"]:
        if isinstance(cust["created_at"], datetime):
            cust["created_at"] = cust["created_at"].strftime("%b %d, %Y, %I:%M %p")
        else:
            cust["created_at"] = str(cust["created_at"])
    return cust

def is_valid_email(email):
    if not email:
        return True
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_contact(phone):
    phone = phone.strip()
    # Check length limits (min 7, max 20)
    if len(phone) < 7 or len(phone) > 20:
        return False
    # Pattern check
    pattern = r"^\+?\d{1,3}?[-\s]?\d{3,4}[-\s]?\d{6,7}$"
    return bool(re.match(pattern, phone))


@customers_bp.route("/customers")
def customers():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, name, contact_number, email, created_at FROM customers"
        )
        customers = cursor.fetchall()
        # Format dates for each row
        for cust in customers:
            format_created_at(cust)
        cursor.close()
        db.close()
        return render_template("customers.html", customers=customers)
    except Exception as e:
        print("Error fetching customers:", e)
        traceback.print_exc()
        return "Database error", 500
    
@customers_bp.route("/add_customer", methods=["POST"])
def add_customer():
    try:
        name = request.form.get("name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()

        # --- Validation ---
        if not name:
            return jsonify({"error": "Customer name is required."}), 400
        if not is_valid_name(name):
            return jsonify({
            "error": (
                "Name must only contain letters, spaces. "
                "It must start and end with a letter, and not contain special characters like hyphens."
                )
        }), 400

        if not contact_number:
            return jsonify({"error": "Contact number is required."}), 400
        if len(contact_number) < 7 or len(contact_number) > 20:
            return jsonify({"error": "Contact number must be between 7 and 20 characters."}), 400
        if not is_valid_contact(contact_number):
            return jsonify({"error": "Contact number must be a valid number (e.g. +92-333-34324355)."}), 400

    
        if email and not is_valid_email(email):
            return jsonify({"error": "Invalid email address."}), 400

        db = get_db_connection()
        cursor = db.cursor()
        # Prevent duplicates (by contact number)
        cursor.execute("SELECT id FROM customers WHERE contact_number = %s", (contact_number,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"error": "A customer with this contact number already exists."}), 409

        cursor.execute(
            "INSERT INTO customers (name, contact_number, email) VALUES (%s, %s, %s)",
            (name, contact_number, email)
        )
        db.commit()
        customer_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, name, contact_number, email, created_at FROM customers WHERE id = %s",
            (customer_id,)
        )
        customer = cursor.fetchone()
        customer = format_created_at(customer)
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

@customers_bp.route("/get_customer/<int:customer_id>")
def get_customer(customer_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, name, contact_number, email, created_at FROM customers WHERE id = %s",
            (customer_id,)
        )
        customer = cursor.fetchone()
        customer = format_created_at(customer)
        cursor.close()
        db.close()

        if customer:
            return jsonify(customer)
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        print("Error fetching customer:", e)
        return jsonify({"error": str(e)}), 500

@customers_bp.route("/update_customer", methods=["POST"])
def update_customer():
    try:
        customer_id = request.form.get("id", "").strip()
        name = request.form.get("name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip().lower()

        # --- Validation ---
        if not customer_id:
            return jsonify({"error": "Customer ID is required."}), 400
        if not customer_id.isdigit():
            return jsonify({"error": "Customer ID must be a valid integer."}), 400
        customer_id_int = int(customer_id)
        if not name:
            return jsonify({"error": "Name is required."}), 400
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters."}), 400
        if not is_valid_name(name):
            return jsonify({
            "error": (
                "Name must only contain letters, spaces. "
                "It must start and end with a letter, and not contain special characters like hyphens."
                )
        }), 400
        if not contact_number:
            return jsonify({"error": "Contact number is required."}), 400
        if len(contact_number) < 7 or len(contact_number) > 20:
            return jsonify({"error": "Contact number must be between 7 and 20 characters."}), 400
        if not is_valid_contact(contact_number):
            return jsonify({"error": "Contact number must be a valid number (e.g. +92-333-34324355)."}), 400
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email address."}), 400
        db = get_db_connection()
        cursor = db.cursor()

        # Prevent duplicate contact number (exclude self)
        cursor.execute(
            "SELECT id FROM customers WHERE contact_number = %s AND id != %s",
            (contact_number, customer_id_int)
        )
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"error": "A customer with this contact number already exists."}), 409

        # Check if customer exists before updating
        cursor.execute("SELECT id FROM customers WHERE id = %s", (customer_id_int,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"error": "Customer not found."}), 404

        # Update
        cursor.execute(
            "UPDATE customers SET name = %s, contact_number = %s, email = %s WHERE id = %s",
            (name, contact_number, email, customer_id_int)
        )
        db.commit()

        cursor.execute(
            "SELECT id, name, contact_number, email, created_at FROM customers WHERE id = %s",
            (customer_id_int,)
        )
        customer = cursor.fetchone()
        cursor.close()
        db.close()
        if not customer:
            return jsonify({"error": "Could not retrieve updated customer."}), 404

        customer = format_created_at(customer)

        return jsonify({
            "message": "Customer updated successfully.",
            "customer": customer
        }), 200

    except Exception as e:
        print("Error updating customer:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to update customer due to a server error."}), 500



@customers_bp.route("/delete_customer/<int:customer_id>", methods=["POST"])
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
