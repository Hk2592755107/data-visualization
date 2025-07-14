from flask import Blueprint, request, jsonify
from db import get_db_connection


categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route("/categories")
def get_categories():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM categories WHERE name IS NOT NULL AND name != ''")
    categories = [{"id": row["id"], "name": row["name"]} for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return jsonify(categories)

@categories_bp.route("/add_category", methods=["POST"])
def add_category():
    try:
        category_name = request.form.get("name")
        # Fallback to JSON if form is empty
        if not category_name:
            data = request.get_json(silent=True)
            if data:
                category_name = data.get("name", "").strip()
        else:
            category_name = category_name.strip()
        if not category_name:
            return jsonify({"error": "Category name is required"}), 400
        if len(category_name) < 2 or len(category_name) > 50:
            return jsonify({"error": "Category name must be 2-50 characters."}), 400

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
