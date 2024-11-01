import jwt
import os
import random

from flask import Blueprint, request, jsonify, session
from functools import wraps
# from .models import User
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# from app import db

# User Container
users = {}
# Crumbs Container
crumbs = {}
# Inventories Container 
inventories = {}
# user_ID 
user_id_counter = 1
# crumb_id
crumb_id_counter = 1
# inventory_item id 
inventory_id_counter = 1




crumbl_blueprint = Blueprint("crumbl_blueprint", __name__)

@crumbl_blueprint.route("/", methods=["GET"])
def home():
    return jsonify("Crumbl Backend Online!")


# -------------------------------------------------------------#
# TODO: User Authentication With Sessions and Cookies: - KYLE
# - User Login (SHANTANU) :  Implement user login functionality where
# a user can log in by providing credentials (username and
# password). Use sessions and cookies to track and maintain login states.
# - User Registration (KYLE): Allow new users to register by
# providing a username, password, and email.
# - Session Management (KYLE): Use Flask's session management to store user
# session data securely
# - Logout (SHANTANU): Implement logout functionality that clears the session and
# removes authentication cookies
# -------------------------------------------------------------#


# NOTE: Middleware for login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "You must be logged in to access this route"}), 403

        # Check if session has expired
        if 'last_activity' in session:
            last_activity = datetime.fromtimestamp(session['last_activity'])
            if datetime.now() - last_activity > timedelta(hours=24):
                session.clear()  # Fixed typo: was session.clears()
                return jsonify({"error": "Session expired, please login again"}), 401
        
        # Update last_activity timestamp
        session['last_activity'] = datetime.now().timestamp()
        return f(*args, **kwargs)
    return decorated_function


@crumbl_blueprint.route("/register", methods=["POST"])
def register():
    global user_id_counter

    # PERF: for frontend, no need yet
    #
    # if request.method == "OPTIONS":
    #     return _build_cors_prelight_response()

    try:
        # Get User Input
        email = request.json.get("email")
        firstName = request.json.get("firstName")
        lastName = request.json.get("lastName")
        homeAddress = request.json.get("homeAddress")
        password = request.json.get("password")


        # NOTE: For Part 2
        #
        # --------------------------------------------------------------#
        # checking if the user is already existing
        # existing_user = User.query.filter_by(email=email).first()
        # if existing_user:
        #     return jsonify({"error": "User with this email already existed"}), 401
        # --------------------------------------------------------------#

        # Validate required fields 
        if not all([email, homeAddress, password]):
            return jsonify({
                "error":"Missing required fields"
            }), 400

        # Check if user already exists
        if email in users:
            return jsonify({"error": "User's email is already existed"}), 400

        # generate User ID 
        user_id = f"User_{user_id_counter}"
        user_id_counter += 1 

        # Secure hash password
        password_hash = generate_password_hash(password)

        

        users[email] = {
            "user_id": user_id,
            "email": email,
            "firstName": firstName,
            "lastName" : lastName,
            "homeAddress": homeAddress,
            "password": password_hash,
        }


        # separate index of user_ids and email for quick look up 
        if not hasattr(crumbl_blueprint, 'user_id_index'):
            crumbl_blueprint.user_id_index = {}
        crumbl_blueprint.user_id_index[user_id] = email

        return jsonify({
            "message": "New user Created Successfully",
            "user":{
                "user_id" : user_id, 
                "email" : email,
                "homeAddress" : homeAddress, 
            }
        }), 201

        # NOTE: For part 2
        #
        # --------------------------------------------------------------#
        # new_user = User(
        #     email=email,
        #     password=password,
        #     homeAddress=homeAddress,
        # )
        #
        # db.session.add(new_user)
        # db.session.commit()
        # --------------------------------------------------------------#

        # return (jsonify({"message": "New User Created Successfully !"}), 202)
    except Exception as e:
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

@crumbl_blueprint.route("/users" , methods=["GET"])
def list_users():
    return jsonify({"user":users}), 200


# NOTE: Login route 
@crumbl_blueprint.route("/login", methods=["POST"])
def login():
    try:
        email = request.json.get("email")
        password = request.json.get("password")

        # Check if user exist 
        if email not in users:
            return jsonify({"error" : "Invalid email or password "}),401
        
        user = users[email]

        # verify password 
        if not check_password_hash(user["password"] , password):
            return jsonify({"error" : "Invalid email or password"}),401 

        # create session
        session["user_id"] = user["user_id"] 
        session["logged_in"] = True
        session["last_activity"] = datetime.now().timestamp()

        # Set session to expire after 24 hours 
        session.permanent = True
        
        return jsonify({
            "message":"Login successfully",
            "user":{
                "email":user["email"],
            }
        }),200
    except Exception as e:
        return jsonify({"error":f"Login failed : {str(e)}"}),500


@crumbl_blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        # Clear all session data
        session.clear()
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

# -------------------------------------------------------------#
# TODO: CRUD Operations for Inventory: - BETTY
# - Create Inventory Item: Allow the creation of new inventory
# items with fields like item name, description, quantity, and
# price. With auto creation of ID Read Inventory Items: Provide
# APIs to list all inventory items or fetch a single item based on
# its ID.
# - Update Inventory Item: Allow the modification of an inventory
# item's details (name, quantity, price, etc.).by id
# - Delete Inventory Item: Enable deletion of an inventory item by ID
# -------------------------------------------------------------#



# -------------------------------------------------------------#
# # compares and finds cookie
# def findCrumbl(cid):
#     for crum in crumbls:
#         if crum["ID"] == cid:
#             return crum
#     return None
#
# #assigns a ranom ID number to cookie and ensures it isnt a repeat
# def newID():
#     while True:
#         nid = random.randint(1, 100)
#         if findCrumbl(nid) is None:
#             return nid
#
# #lists full list of cookies
# @crumbl_blueprint.route("/crumbls", methods=["GET"])
# def listCookies():
#     return jsonify(crumbls)
#
# #find specific cookie by ID number
# @crumbl_blueprint.route("/crumbls/<int:cid>", methods=["GET"])
# def findCrum(cid):
#     foundC = findCrumbl(cid)
#     if foundC is None:
#         return jsonify("error: Crumbl Cookie not found"), 404
#     return jsonify(foundC)
#
# #creates new crumbl cookie
# @crumbl_blueprint.route("/crumbls", methods=["POST"])
# def makeCrum():
#     if (
#         not request.json
#         or "name" not in request.json
#         or "description" not in request.json
#         or "quantity" not in request.json
#         or "price" not in request.json
#     ):
#         return jsonify("error missing information"),400
#     newCID = newID()
#     newCrumbl = {
#         "name": request.json["name"],
#         "description": request.json["description"],
#         "quantity": request.json["quantity"],
#         "price": request.json["price"],
#         "ID": newCID,
#     }
#     crumbls.append(newCrumbl)
#     return jsonify(newCrumbl), 201
#
# #updates existing cookie
# @crumbl_blueprint.route("/crumbls/<int:cid>", methods=["PUT"])
# def updateCrum(cid):
#     crum = findCrumbl(cid)
#     if crum is None:
#         jsonify('could not find cookie to update'), 404
#     if not request.json:
#         jsonify('please use proper json standards'), 400
#     crum['name']= request.json.get('name',crum['name'])
#     crum['description']= request.json.get('description',crum['description'])
#     crum['quantity']= request.json.get('quantity',crum['quantity'])
#     crum['price']= request.json.get('price',crum['price'])
#     return jsonify(crum)
#
# #deletes crumbl cookie
# @crumbl_blueprint.route("/crumbls/<int:cid>", methods=["DELETE"])
# def deleteCrum(cid):
#     global crumbls
#     crum = findCrum(cid)
#     if crum is None:
#         return jsonify('Crumble cookie could not be found'), 404
#     crumbls = [c for c in crumbls if c['ID']!=cid]
#     return '', 204
#
# -------------------------------------------------------------#



# Sample structure for creating a new crumb
def create_crumb(cookie_name, description):
    global crumb_id_counter
    crumb_id = f"CRUMB_{crumb_id_counter}"
    crumb_id_counter += 1
    
    crumbs[crumb_id] = {
        "crumb_id": crumb_id,
        "cookie_name": cookie_name,
        "description": description
    }
    return crumb_id

# Structure for managing inventory
def add_to_inventory(user_id, crumb_id, quantity, price):
    global inventory_id_counter
    
    if user_id not in users:
        return False, "User not found"
    
    if crumb_id not in crumbs:
        return False, "Cookie not found"
    
    # Generate unique inventory ID
    inventory_id = f"INV_{inventory_id_counter}"
    inventory_id_counter += 1
    
    inventories[inventory_id] = {
        "inventory_id": inventory_id,
        "user_id": user_id,
        "crumb_id": crumb_id,
        "quantity": quantity,
        "price": price
    }
    return True, inventory_id

# Helper function to get user's inventory
def get_user_inventory(user_id):
    if user_id not in users:
        return []
    
    user_inventory = []
    for inv_id, inv_data in inventories.items():
        if inv_data["user_id"] == user_id:
            # Combine inventory data with cookie details
            crumb_data = crumbs[inv_data["crumb_id"]]
            inventory_item = {
                "inventory_id": inv_data["inventory_id"],
                "crumb_id": inv_data["crumb_id"],
                "cookie_name": crumb_data["cookie_name"],
                "description": crumb_data["description"],
                "quantity": inv_data["quantity"],
                "price": inv_data["price"]
            }
            user_inventory.append(inventory_item)
    
    return user_inventory

# Get all inventory entries for a specific user and cookie
def get_user_cookie_inventories(user_id, crumb_id):
    return [
        inv_data for inv_data in inventories.values()
        if inv_data["user_id"] == user_id and inv_data["crumb_id"] == crumb_id
    ]


# -------------------------------------------------------------#
# TODO: USER-Specific Inventory Management: - PHONG
# - Each Logged-in user will have their own inventory items, ensuring
# that users can only access and modify their own data.
# - Use sessions to ensure that only authenticated users can access
# inventory-related CRUD Operations
# -------------------------------------------------------------#


# -------------------------------------------------------------#
# NOTE:
# Using mock users and mock login to add user_id to session
# Update new mock crumbls data
# RuntimeError: The session is unavailable because no secret key was set.
# TODO:
# - Add: `app.secret_key="YOUR_SECRET_KEY"` in __init__.py. 
# -------------------------------------------------------------#

# -------------------------------------------------------------#
# # Mocking users and Login 
# users = [
#     {
#         "id": 1,
#         "email": "john.doe@example.com",
#         "homeAddress": "123 Main St, Springfield, IL",
#         "password": generate_password_hash("jd"),
#     },
#     {
#         "id": 2,
#         "email": "jane.smith@example.com",
#         "homeAddress": "456 Oak St, Springfield, IL",
#         "password": generate_password_hash("js"),
#         "firstName": "Jane",
#         "lastName": "Smith",
#     },
#     {
#         "id": 3,
#         "email": "michael.jordan@example.com",
#         "homeAddress": "789 Maple Ave, Chicago, IL",
#         "password": generate_password_hash("mj"),
#         "firstName": "Michael",
#         "lastName": "Jordan",
#     },
#     {
#         "id": 4,
#         "email": "susan.williams@example.com",
#         "homeAddress": "321 Elm St, Aurora, IL",
#         "password": generate_password_hash("sw"),
#         "firstName": "Susan",
#         "lastName": "Williams",
#     },
# ]
#
# #-----------------------------------------------------------------------------------------#
# # @crumbl_blueprint.route("/login", methods=["POST"])
# # def login():
# #     # Example code - assumes you are authenticating a user and retrieving their `user_id`
# #     email = request.json.get("email")
# #     password = request.json.get("password")
# #     user = {}
# #
# #     # Find user based on email
# #     for u in users: 
# #         if u["email"] == email: user = u
# #
# #     if user and check_password_hash(user["password"], password):
# #         # Store the `user_id` in the session after successful login
# #         session["user_id"] = user["id"]
# #         return jsonify({"message": "Login successful"}), 200
# #     else:
# #         return jsonify({"error": "Invalid email or password"}), 401
# #
# #-----------------------------------------------------------------------------------------#
# # Crumble with users_id containers
# crumbls = [
#     {
#         "name": "Chocolate Chip",
#         "description": "The classic chocolate chip cookie",
#         "quantity": 65,
#         "price": 4.99,
#         "ID": 20,
#         "user_id": 1,
#     },
#     {
#         "name": "Confetti Milk Shake",
#         "description": "A confetti sugar cookie rolled in rainbow sprinkles and topped with cake-flavored buttercream and a dollop of whipped cream",
#         "quantity": 23,
#         "price": 4.99,
#         "ID": 46,
#         "user_id": 2,
#     },
#     {
#         "name": "Kentucky Butter Cake",
#         "description": "A yellow butter cake cookie smothered with a melt-in-your-mouth buttery glaze.",
#         "quantity": 12,
#         "price": 4.99,
#         "ID": 26,
#         "user_id": 3,
#     },
#     {
#         "name": "Pink Velvet Cake Cookie",
#         "description": "A velvety cake batter cookie topped with a layer of vanilla cream cheese frosting and pink velvet cookie crumbs.",
#         "quantity": 7,
#         "price": 4.99,
#         "ID": 63,
#         "user_id": 4,
#     },
# ]
#
# @crumbl_blueprint.route("/mycrumbls", methods=["GET"])
# @login_required
# def myListCookies():
#     user_id = session.get("user_id")
#     user_crumbls = [crum for crum in crumbls if crum["user_id"] == user_id]
#     return jsonify(user_crumbls)
#
# @crumbl_blueprint.route("/mycrumbls/<int:cid>", methods=["GET"])
# @login_required
# def findMyCrum(cid):
#     user_id = session.get("user_id")
#     foundC = next((crum for crum in crumbls if crum["ID"] == cid and crum["user_id"] == user_id), None)
#     if foundC is None:
#         return jsonify({"error": "Crumbl Cookie not found"}), 404
#     return jsonify(foundC)
#
# @crumbl_blueprint.route("/mycrumbls", methods=["POST"])
# @login_required
# def makeMyCrum():
#     user_id = session.get("user_id")
#     if (
#         not request.json
#         or "name" not in request.json
#         or "description" not in request.json
#         or "quantity" not in request.json
#         or "price" not in request.json
#     ):
#         return jsonify({"error": "Missing information"}), 400
#     newCID = newID()
#     newCrumbl = {
#         "name": request.json["name"],
#         "description": request.json["description"],
#         "quantity": request.json["quantity"],
#         "price": request.json["price"],
#         "ID": newCID,
#         "user_id": user_id  # Associate new item with the logged-in user
#     }
#     crumbls.append(newCrumbl)
#     return jsonify(newCrumbl), 201
#
# @crumbl_blueprint.route("/mycrumbls/<int:cid>", methods=["PUT"])
# @login_required
# def updateMyCrum(cid):
#     user_id = session.get("user_id")
#     crum = next((crum for crum in crumbls if crum["ID"] == cid and crum["user_id"] == user_id), None)
#     if crum is None:
#         return jsonify({"error": "Crumbl Cookie not found or unauthorized"}), 404
#     if not request.json:
#         return jsonify({"error": "Invalid JSON format"}), 400
#
#     # Update fields if provided in request
#     crum["name"] = request.json.get("name", crum["name"])
#     crum["description"] = request.json.get("description", crum["description"])
#     crum["quantity"] = request.json.get("quantity", crum["quantity"])
#     crum["price"] = request.json.get("price", crum["price"])
#     return jsonify(crum)
#
# @crumbl_blueprint.route("/mycrumbls/<int:cid>", methods=["DELETE"])
# @login_required
# def deleteMyCrum(cid):
#     global crumbls
#     user_id = session.get("user_id")
#     crum = next((crum for crum in crumbls if crum["ID"] == cid and crum["user_id"] == user_id), None)
#     if crum is None:
#         return jsonify({"error": "Crumbl Cookie not found or unauthorized"}), 404
#     crumbls = [c for c in crumbls if not (c["ID"] == cid and c["user_id"] == user_id)]
#     return jsonify({"message": "Item deleted successfully."}), 200
#
#----------------------------------------------------------------------------------------#

# Example routes for CRUD operations
@crumbl_blueprint.route("/inventory", methods=["POST"])
@login_required
def add_inventory():
    try:
        # getting user_id from session
        user_id = session["user_id"]  
        # extract crumb_id quantity and price from request 
        crumb_id = request.json.get("crumb_id")
        quantity = request.json.get("quantity")
        price = request.json.get("price")
        
        if not all([crumb_id, quantity, price]):
            return jsonify({"error": "Missing required fields"}), 400
            
        success, inventory_id = add_to_inventory(user_id, crumb_id, quantity, price)
        
        if not success:
            return jsonify({"error": inventory_id}), 400
            
        return jsonify({
            "message": "Inventory added successfully",
            "inventory": inventories[inventory_id]
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to add inventory: {str(e)}"}), 500

# Example: Get all inventory entries for a specific cookie
@crumbl_blueprint.route("/inventory/cookie/<crumb_id>", methods=["GET"])
@login_required
def get_cookie_inventories(crumb_id):
    try:
        user_id = session["user_id"]
        inventories_list = get_user_cookie_inventories(user_id, crumb_id)
        
        return jsonify({
            "inventories": inventories_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get inventories: {str(e)}"}), 500

# Update inventory entry
@crumbl_blueprint.route("/inventory/<inventory_id>", methods=["PUT"])
@login_required
def update_inventory(inventory_id):
    try:
        user_id = session["user_id"]
        
        if inventory_id not in inventories:
            return jsonify({"error": "Inventory not found"}), 404
            
        inventory = inventories[inventory_id]
        if inventory["user_id"] != user_id:
            return jsonify({"error": "Unauthorized access"}), 403
            
        # Update quantity and/or price
        if "quantity" in request.json:
            inventory["quantity"] = request.json["quantity"]
        if "price" in request.json:
            inventory["price"] = request.json["price"]
            
        return jsonify({
            "message": "Inventory updated successfully",
            "inventory": inventory
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update inventory: {str(e)}"}), 500

# Cookie CRUD Operations
@crumbl_blueprint.route("/cookies", methods=["POST"])
@login_required
def create_cookie():
    try:
        # Extract cookie details from request
        cookie_name = request.json.get("cookie_name")
        description = request.json.get("description")
        
        # Validate required fields
        if not all([cookie_name, description]):
            return jsonify({
                "error": "Missing required fields. Cookie name and description are required."
            }), 400
            
        # Create new cookie
        crumb_id = create_crumb(cookie_name, description)
        
        return jsonify({
            "message": "Cookie created successfully",
            "cookie": crumbs[crumb_id]
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Failed to create cookie: {str(e)}"}), 500

# Get all cookies (public catalog)
@crumbl_blueprint.route("/cookies", methods=["GET"])
def get_all_cookies():
    try:
        return jsonify({
            "cookies": list(crumbs.values())
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch cookies: {str(e)}"}), 500

# Get specific cookie
@crumbl_blueprint.route("/cookies/<crumb_id>", methods=["GET"])
def get_cookie(crumb_id):
    try:
        if crumb_id not in crumbs:
            return jsonify({"error": "Cookie not found"}), 404
            
        return jsonify(crumbs[crumb_id]), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch cookie: {str(e)}"}), 500

# Update cookie details
@crumbl_blueprint.route("/cookies/<crumb_id>", methods=["PUT"])
@login_required
def update_cookie(crumb_id):
    try:
        if crumb_id not in crumbs:
            return jsonify({"error": "Cookie not found"}), 404
            
        cookie = crumbs[crumb_id]
        
        # Update fields if provided
        if "cookie_name" in request.json:
            cookie["cookie_name"] = request.json["cookie_name"]
        if "description" in request.json:
            cookie["description"] = request.json["description"]
            
        return jsonify({
            "message": "Cookie updated successfully",
            "cookie": cookie
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update cookie: {str(e)}"}), 500

# Delete cookie
@crumbl_blueprint.route("/cookies/<crumb_id>", methods=["DELETE"])
@login_required
def delete_cookie(crumb_id):
    try:
        if crumb_id not in crumbs:
            return jsonify({"error": "Cookie not found"}), 404
            
        # Check if cookie is being used in any inventory
        for inventory in inventories.values():
            if inventory["crumb_id"] == crumb_id:
                return jsonify({
                    "error": "Cannot delete cookie that exists in inventories"
                }), 400
                
        # Delete the cookie
        del crumbs[crumb_id]
        
        return jsonify({
            "message": "Cookie deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete cookie: {str(e)}"}), 500
# -------------------------------------------------------------#
# TODO: Session and Cookie Security: - MATHEW
# - Secure user sessions with encryption (Flask Security key)
# - Implement proper session expiration handing to automatically
# log out.
# -------------------------------------------------------------#









# crumbls = [
#     {
#         "name": "Chocolate Chip",
#         "description": "The classic chocolate chip cookie",
#         "quantity": 65,
#         "price": 4.99,
#         "ID": 20,
#     },
#     {
#         "name": "Confetti Milk Shake",
#         "description": "A confetti sugar cookie rolled in rainbow sprinkles and topped with cake-flavored buttercream and a dollop of whipped cream",
#         "quantity": 23,
#         "price": 4.99,
#         "ID": 46,
#     },
#     {
#         "name": "Kentucky Butter Cake",
#         "description": "A yellow butter cake cookie smothered with a melt-in-your-mouth buttery glaze.",
#         "quantity": 12,
#         "price": 4.99,
#         "ID": 26,
#     },
#     {
#         "name": "Pink Velvet Cake Cookie",
#         "description": "A velvety cake batter cookie topped with a layer of vanilla cream cheese frosting and pink velvet cookie crumbs.",
#         "quantity": 7,
#         "price": 4.99,
#         "ID": 63,
#     },
# ]
