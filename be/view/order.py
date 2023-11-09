from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.order import Order

bp_order = Blueprint("order", __name__, url_prefix="/order")


@bp_order.route("new_order_cancel/", methods=["POST"])
def new_order_cancel():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    s = Order()
    code, message = s.new_order_cancel(user_id, order_id)
    return jsonify({"message": message}), code


@bp_order.route("/check_order", methods=["POST"])
def check_order():
    user_id: str = request.json.get("user_id")
    s = Order()
    code, message = s.check_order(user_id)
    return jsonify({"message": message}), code


# @bp_order.route("check_order_status/", methods=["POST"])
# def check_order_status():
#     s = Order()
#     code, message = s.check_order_status()
#     return jsonify({"message": message}), code
#
# from flask import Blueprint, request, jsonify
# from be.model.order import Order
#
# bp_order = Blueprint("order", __name__, url_prefix="/order")
#
#
# @bp_order.route("/cancel_order", methods=["POST"])
# def cancel_order():
#     user_id = request.json.get("user_id")
#     order_id = request.json.get("order_id")
#
#     order_handler = Order()
#     code, message = order_handler.cancel_order(user_id, order_id)
#     return jsonify({"message": message}), code
#
# @bp_order.route("/get_paid_orders", methods=["GET"])
# def get_paid_orders():
#     user_id = request.args.get("user_id")
#
#     order_handler = Order()
#     code, message, orders = order_handler.get_paid_order_history(user_id)
#     return jsonify({"message": message, "orders": orders}), code
#
# @bp_order.route("/get_unpaid_orders", methods=["GET"])
# def get_unpaid_orders():
#     user_id = request.args.get("user_id")
#
#     order_handler = Order()
#     code, message, orders = order_handler.get_unpaid_order_history(user_id)
#     return jsonify({"message": message, "orders": orders}), code
