"""
This code has been adapted from the following source:

flask-starter-app
Retrieved on: 02/08/2025
URL: https://github.com/osu-cs340-ecampus/flask-starter-app
"""

import database.db_connector as db
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, json
from flask_mysqldb import MySQL
import os

# Configuration

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Set application variables
APP_MYSQL_HOST = os.getenv("APP_MYSQL_HOST")
APP_MYSQL_USER = os.getenv("APP_MYSQL_USER")
APP_MYSQL_PASSWORD = os.getenv("APP_MYSQL_PASSWORD")
APP_MYSQL_DB_NAME = os.getenv("APP_MYSQL_DB_NAME")
APP_PORT = int(os.getenv("PORT", 4282))


def connect():
    # Connect to the database
    db_connection = db.connect_to_database(APP_MYSQL_HOST, APP_MYSQL_USER, APP_MYSQL_PASSWORD, APP_MYSQL_DB_NAME)
    return db_connection


# Routes

@app.route('/')
def root():
    return render_template("main.j2")


@app.route('/users', methods=["GET"])
def users():
    # Get the Users data for display
    if request.method == "GET":
        users_get_query = 'SELECT userID AS "User ID", username AS Username, password AS Password, email AS Email, neighborhoodID AS "Neighborhood ID" FROM Users;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=users_get_query)
            query_results = cursor.fetchall()
            return render_template("users.j2", users=query_results)


@app.route('/items', methods=["POST", "GET"])
def items():
    # Create a new Item
    if request.method == "POST":
        if request.form.get("add_item"):
            # Get user form inputs
            item_name = request.form["item_name"]
            category_name = request.form["category_name"]
            item_add_query = 'INSERT INTO Items (itemName, categoryID) VALUES (%s, (SELECT categoryID FROM ItemCategories WHERE categoryName = %s));'
            print(item_add_query)
            with connect() as db_connection:
                db.execute_query(db_connection=db_connection, query=item_add_query, query_params=(item_name, category_name, ))

        return redirect('/items')

    # Get the Items data for display
    if request.method == "GET":
        items_get_query = 'SELECT Items.itemID AS "Item ID", Items.itemName AS "Item Name", ItemCategories.categoryName AS "Category Name" FROM Items JOIN ItemCategories ON Items.categoryID = ItemCategories.categoryID;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=items_get_query)
            query_results = cursor.fetchall()
            return render_template("items.j2", items=query_results)

# Route for updating the selected Item
@app.route('/edit_items/<int:id>', methods=["POST", "GET"])
def edit_items(id):
    print(f"Received request for id: {id}")

    # Get data for the Item with the specified id
    if request.method == "GET":
        items_get_query = 'SELECT Items.itemID AS "Item ID", Items.itemName AS "Item Name", ItemCategories.categoryName AS "Category Name" FROM Items JOIN ItemCategories ON Items.categoryID = ItemCategories.categoryID WHERE itemID = %s;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=items_get_query, query_params=(id,))
            query_results = cursor.fetchall()
            print(f"Query results: {query_results}")
            return render_template("edit_items.j2", item=query_results)

    # Update the Item with the specified id
    if request.method == "POST":
        # Get form input
        item_name = request.form["item_name"]
        category_name = request.form["category_name"]

        # Execute the query to update the Item
        item_update_query = 'UPDATE Items SET itemName = %s, categoryID = (SELECT categoryID FROM ItemCategories WHERE categoryName = %s) WHERE itemID = %s;'
        with connect() as db_connection:
            db.execute_query(db_connection=db_connection, query=item_update_query, query_params=(item_name, category_name, id,))

        return redirect('/items')

# Route for deleting the selected Item
@app.route('/delete_items/<int:id>')
def delete_items(id):
    # Delete the Item with the specified id
    items_delete_query = 'DELETE FROM Items WHERE itemID = %s;'
    with connect() as db_connection:
        db.execute_query(db_connection=db_connection, query=items_delete_query, query_params=(id,))

    return redirect('/items')


@app.route('/user_items', methods=["GET"])
def user_items():
    # Get the User Items data for display
    if request.method == "GET":
        user_items_get_query = 'SELECT userID AS "User ID", itemID AS "Item ID" FROM UserItems;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=user_items_get_query)
            query_results = cursor.fetchall()
            return render_template("user_items.j2", user_items=query_results)


@app.route('/transfers', methods=["GET"])
def transfers():
    # Get the Transfers data for display
    if request.method == "GET":
        transfers_get_query = 'SELECT transferID AS "Transfer ID", transferDateTime AS "Transfer Date and Time", lendingUserID AS "Lending User ID", borrowingUserID AS "Borrowing User ID" FROM Transfers;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=transfers_get_query)
            query_results = cursor.fetchall()
            return render_template("transfers.j2", transfers=query_results)


@app.route('/transfer_items', methods=["GET"])
def transfer_items():
    # Get the Transfer Items data for display
    if request.method == "GET":
        transfer_items_get_query = 'SELECT transferItemID AS "Transfer Item ID", itemID AS "Item ID", transferID AS "Transfer ID", quantity AS Quantity, milliliters AS Milliliters, pounds AS Pounds FROM TransferItems;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=transfer_items_get_query)
            query_results = cursor.fetchall()
            return render_template("transfer_items.j2", transfer_items=query_results)

@app.route('/neighborhoods', methods=["GET"])
def neighborhoods():
    # Get the Neighborhoods data for display
    if request.method == "GET":
        neighborhoods_get_query = 'SELECT neighborhoodID AS "Neighborhood ID", neighborhoodName AS "Neighborhood Name" FROM Neighborhoods;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=neighborhoods_get_query)
            query_results = cursor.fetchall()
            return render_template("neighborhoods.j2", neighborhoods=query_results)

@app.route('/item_categories', methods=["POST", "GET"])
def item_categories():
    # Create a new Item Category
    if request.method == "POST":
        if request.form.get("add_item_category"):
            # Get user form inputs
            item_category_name = request.form["category_name"]
            item_category_add_query = 'INSERT INTO ItemCategories (categoryName) VALUES (%s);'
            with connect() as db_connection:
                db.execute_query(db_connection=db_connection, query=item_category_add_query, query_params=(item_category_name, ))

        return redirect('/item_categories')
    
    # Retrieve the Item Categories data for display
    if request.method == "GET":
        item_categories_get_query = 'SELECT categoryID AS "Category ID", categoryName AS "Category Name" FROM ItemCategories;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=item_categories_get_query)
            query_results = cursor.fetchall()
            return render_template("item_categories.j2", item_categories=query_results)


# Route for updating the selected Item Category
@app.route('/edit_item_categories/<int:id>', methods=["POST", "GET"])
def edit_item_categories(id):
    print(f"Received request for id: {id}")
    
    # Get data for the Item Category with the specified id
    if request.method == "GET":
        item_category_get_query = 'SELECT categoryID AS "Category ID", categoryName AS "Category Name" FROM ItemCategories WHERE categoryID = %s;'
        with connect() as db_connection:
            cursor = db.execute_query(db_connection=db_connection, query=item_category_get_query, query_params=(id, ))
            query_results = cursor.fetchall()
            print(f"Query results: {query_results}")
            return render_template("edit_item_categories.j2", item_category=query_results)
    
    # Update the Item Category with the specified id
    if request.method == "POST":
        # Get form input
        category_name = request.form["category_name"]
        
        # Execute the query to update the Item Category
        item_category_update_query = 'UPDATE ItemCategories SET categoryName = %s WHERE categoryID = %s;'
        with connect() as db_connection:
            db.execute_query(db_connection=db_connection, query=item_category_update_query, query_params=(category_name, id, ))
    
        return redirect('/item_categories')
    

# Route for deleting the selected Item Category
@app.route('/delete_item_categories/<int:id>')
def delete_item_categories(id):
    # Delete the Item Category with the specified id
    item_categories_delete_query = 'DELETE FROM ItemCategories WHERE categoryID = %s;'
    with connect() as db_connection:
        db.execute_query(db_connection=db_connection, query=item_categories_delete_query, query_params=(id, ))
    
    return redirect('/item_categories')


# Listener

if __name__ == "__main__":
    port = APP_PORT

    app.run(port=port)