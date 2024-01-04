from flask import Flask, make_response, jsonify, request, render_template
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "lonelyheart05"
app.config["MYSQL_DB"] = "csedb"
app.config["JWT_SECRET_KEY"] = "testing321"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
jwt = JWTManager(app)


def data_execute(query, data=None, fetch_one=False):
    cur = mysql.connection.cursor()
    if data:
        cur.execute(query, data)
    else: 
        cur.execute(query)
    if fetch_one:
        result = cur.fetchone()
    else:
        result = cur.fetchall()   
    cur.close()
    return result

@app.route("/api/auth", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        user = data_execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password), fetch_one=True)

        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"Error": "Invalid Credentials"}), 401
    except Exception as e:
        return jsonify({"Error": "Internal Server Error"}), 500

@app.route("/api/data/protected", methods=['GET'])
@jwt_required()
def protected_route():
    try:
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401
# Read
@app.route("/", methods=['GET', 'POST'])
def search():
    try:
        if request.method == 'POST':
            search_item = request.form['search_item']
            cur = mysql.connection.cursor()
            query = " SELECT * FROM customers INNER JOIN address ON customers.customer_id = address.address_id WHERE customer_name LIKE %s"
            data = ('%' + search_item + '%',)
            results = data_execute(query, data=data)
            return render_template('search_results.html', results=results, search_item=search_item)
        return render_template('search.html')
    except Exception as e:
        return make_response(
            jsonify(
                {"Error": str(e)}),
            500,
        )

@app.route("/api/data/customers", methods=["GET"])
def get_customers():
    data = data_execute("""select * from customers """)
    return make_response(jsonify(data), 200)


@app.route("/api/data/customers/<int:id>", methods=["GET"])
def get_customers_by_id(id):
    data = data_execute("""SELECT * FROM customers INNER JOIN address ON customers.customer_id = address.address_id 
                      WHERE customers.customer_id = {}""".format(id))
    return make_response(jsonify(data), 200)

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Create
@app.route("/api/data/customers", methods=["POST"])
def add_customer():
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()
        customer_name = info["customer_name"]
        date_became_customer = info["date_became_customer"]
        line_1 = info["line_1"]
        line_2 = info["line_2"]
        line_3 = info["line_3"]
        city = info["city"]
        province = info["county_province"]
        zip_postcode = info["zip_or_postcode"]
        country = info["country"]

        if not validate_date(date_became_customer):
            return make_response(
                jsonify({"Error": "Invalid date format for date became customer. USE YYYY-MM-DD."}),
                400,
            )
        cur.execute(
            """ INSERT INTO customers (customer_name, date_became_customer) VALUE (%s, %s)""",
            (customer_name, date_became_customer),
        )
        cur.execute(
            """ INSERT INTO address (line_1, line_2, line_3, city, county_province, zip_or_postcode, country) VALUE (%s, %s, %s, %s, %s, %s, %s)""",
            (line_1, line_2, line_3, city, province, zip_postcode, country),
        )
    
        mysql.connection.commit()
        print("row(s) affected :{}".format(cur.rowcount))
        rows_affected = cur.rowcount
        cur.close()
        return make_response(
            jsonify(
                {"message": "customer added successfully", "rows_affected": rows_affected}
            ),
            201,
        )
    except Exception as e:
        return make_response(
            jsonify(
                {"Error": str(e)}),
            500,
        )


@app.route("/api/data/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()
        customer_name = info["customer_name"]
        date_became_customer = info["date_became_customer"]
        line_1 = info["line_1"]
        line_2 = info["line_2"]
        line_3 = info["line_3"]
        city = info["city"]
        province = info["county_province"]
        zip_postcode = info["zip_or_postcode"]
        country = info["country"]
        cur.execute(
            """ UPDATE customers SET customer_name = %s, date_became_customer = %s WHERE customer_id = %s """,
            (customer_name, date_became_customer, id),
        )
        cur.execute(
            """ UPDATE address SET line_1 = %s, line_2 = %s, line_3 = %s, city = %s, county_province = %s, zip_or_postcode = %s, country = %s WHERE address_id = %s """,
            (line_1, line_2, line_3, city, province, zip_postcode, country, id),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return make_response(
            jsonify(
                {"message": "customer updated successfully", "rows_affected": rows_affected}
            ),
            200,
        )
    except Exception as e:
        return make_response(
            jsonify(
            {"Error": str(e)}), 
            500, 
        )

@app.route("/api/data/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" DELETE FROM customers where customer_id = %s """, (id,))
        cur.execute(""" DELETE FROM address where address_id = %s """, (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()
        return make_response(
            jsonify(
                {"message": "customer deleted successfully", "rows_affected": rows_affected}
            ),
            200,
        )
    except Exception as e:
        return make_response(
            jsonify()
        )

@app.route("/api/data/format", methods=["GET"])
def get_params():
    output_format = request.args.get("format", 'json')
    if output_format.lower() == 'xml':
        return {'Content-Type': 'application/xml'}, 200
    elif output_format.lower() == 'json':
        return jsonify(), 200
    else:
        return jsonify({"Error": "Invalid format specified"}), 400

if __name__ == "__main__":
    app.run(debug=True)
