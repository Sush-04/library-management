from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'library'
}

# Function to connect to MySQL database
def connect_to_database():
    try:
        cnx = mysql.connector.connect(**mysql_config)
        print("Connected to mysql")
        return cnx
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

@app.route('/')
def index():
   return render_template('index.html')



# Route to insert employee data into MySQL
@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.get_json()
        print(data)
        if data:
            conn = connect_to_database()
            print("connected to db")
            if conn:
                print("enters")
                cursor = conn.cursor()
                print("cursor connected")
                query = "INSERT INTO book (title, author, subject, date) VALUES (%s, %s, %s, %s)"
                employee_values = (
                    data['title'], data['author'], data['subject'], data['date']
                )
                print(employee_values)
                cursor.execute(query, employee_values)
                print("inserted")

                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'message': 'Employee details added successfully'})
            else:
                print("Failed")
                return jsonify({'error': 'Failed to connect to the database'})
        else:
            return jsonify({'error': 'No data provided'})
    except Exception as e:
        return jsonify({'error': str(e)})
    
# Route to fetch paginated data from the database
@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        offset = (page - 1) * per_page

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT title, author, subject, date FROM book LIMIT %s OFFSET %s", (per_page, offset))
            data = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) AS total_count FROM book")
            total_count = cursor.fetchone()['total_count']
            cursor.close()
            conn.close()
            return jsonify({'data': data, 'total_count': total_count})
        else:
            return jsonify({'error': 'Failed to connect to the database'})
    except Exception as e:
        return jsonify({'error': str(e)})
@app.route('/search_books')
def search_books():
    try:
        query = request.args.get('query', '')
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Use LIKE operator to search for books containing the query in title, author, or subject
            cursor.execute("SELECT title, author, subject, date FROM book WHERE title LIKE %s OR author LIKE %s OR subject LIKE %s",
                           ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(data)
        else:
            return jsonify({'error': 'Failed to connect to the database'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
