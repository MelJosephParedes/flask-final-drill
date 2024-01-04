from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

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
    

@app.route("/")
def hello_world():
    return "<h1>Hello, World!</h1>"

# READ
@app.route("/api/data/customers", methods=["GET"])
def get_customers():
    data = data_execute("""select * from customers """)
    return make_response(jsonify(data), 200)


@app.route("/api/data/customers/<int:id>", methods=["GET"])
def get_customers_by_id(id):
    data = data_execute("""SELECT * FROM customers INNER JOIN address ON customers.customer_id = address.address_id 
                      WHERE customers.customer_id = {}""".format(id))
    return make_response(jsonify(data), 200)


@app.route("/actors/<int:id>/movies", methods=["GET"])
def get_movies_by_actor(id):
    data = data_execute(
        """
        SELECT film.title, film.release_year 
        FROM actor 
        INNER JOIN film_actor
        ON actor.actor_id = film_actor.actor_id 
        INNER JOIN film
        ON film_actor.film_id = film.film_id 
        WHERE actor.actor_id = {}
    """.format(
            id
        )
    )
    return make_response(
        jsonify({"actor_id": id, "count": len(data), "movies": data}), 200
    )


@app.route("/actors", methods=["POST"])
def add_actor():
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ INSERT INTO actor (first_name, last_name) VALUE (%s, %s)""",
        (first_name, last_name),
    )
    mysql.connection.commit()
    print("row(s) affected :{}".format(cur.rowcount))
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor added successfully", "rows_affected": rows_affected}
        ),
        201,
    )


@app.route("/actors/<int:id>", methods=["PUT"])
def update_actor(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ UPDATE actor SET first_name = %s, last_name = %s WHERE actor_id = %s """,
        (first_name, last_name, id),
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor updated successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/actors/<int:id>", methods=["DELETE"])
def delete_actor(id):
    cur = mysql.connection.cursor()
    cur.execute(""" DELETE FROM actor where actor_id = %s """, (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor deleted successfully", "rows_affected": rows_affected}
        ),
        200,
    )

@app.route("/actors/format", methods=["GET"])
def get_params():
    fmt = request.args.get('id')
    foo = request.args.get('aaaa')
    return make_response(jsonify({"format":fmt, "foo":foo}),200)


if __name__ == "__main__":
    app.run(debug=True)
