from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
import traceback

sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/sale/<int:sale_id>')
def sale_details(sale_id):
    try:
        if sale_id <= 0:
            return "Invalid sale ID.", 400

        db = get_db_connection()
        cursor = db.cursor()

        # Fetch sale and customer info
        cursor.execute("""
            SELECT s.id, s.date, s.total_amount,
                   c.name AS customer_name, c.contact_number, c.email
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.id = %s
        """, (sale_id,))
        sale = cursor.fetchone()

        if not sale:
            cursor.close()
            db.close()
            return render_template("sale_details.html", sale=None), 404

        # Fetch sold items for this sale
        cursor.execute("""
            SELECT si.quantity, si.price as unit_price, si.discount, si.total_price,
                   m.name AS medicine_name
            FROM sales_item si
            JOIN medicines m ON si.medicine_id = m.id
            WHERE si.sale_id = %s
        """, (sale_id,))
        items = cursor.fetchall()

        cursor.close()
        db.close()

        # Attach items to sale dict for easy template looping
        if sale is not None:
            sale["items"] = items

        return render_template("sale_details.html", sale=sale)
    except Exception as e:
        print("Error loading sale details:", e)
        traceback.print_exc()
        return "Error loading sale details", 500

@sales_bp.route("/sales_history")
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
