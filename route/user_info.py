from flask import Blueprint, request, jsonify

user_info_bp = Blueprint('user_info_bp', __name__)

@user_info_bp.route('/get_my_ip')
def get_my_ip():
    client_ip = request.remote_addr
    return jsonify({"ip": client_ip})
