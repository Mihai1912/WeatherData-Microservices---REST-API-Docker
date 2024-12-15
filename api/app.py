from flask import Flask, jsonify, request
import psycopg2
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host='db',
        database='mydb',
        user='user',
        password='password'
    )
    return conn

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/countries', methods=['POST'])
def add_country():

    data = request.get_json()
    
    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400
    
    nume = data['nume']
    lat = data['lat']
    lon = data['lon']

    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id FROM tari WHERE nume = %s', (nume,))
    existing_country = cursor.fetchone()
    
    if existing_country:
        cursor.close()
        connection.close()
        return jsonify({"error": "Conflict: Country already exists"}), 409

    cursor.execute('''
        INSERT INTO tari (nume, lat, lon) 
        VALUES (%s, %s, %s) RETURNING id
    ''', (nume, lat, lon))
    new_country_id = cursor.fetchone()[0]
    
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"id": new_country_id}), 201

@app.route('/api/countries', methods=['GET'])
def get_all_country():
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, nume, lat, lon FROM tari')
    countries = cursor.fetchall()
    
    countries_list = []
    for country in countries:
        country_data = {
            'id': country[0],
            'nume': country[1],
            'lat': country[2],
            'lon': country[3]
        }
        countries_list.append(country_data)
    
    cursor.close()
    connection.close()

    return jsonify(countries_list), 200

@app.route('/api/countries/<int:id>', methods=['PUT'])
def update_country(id):

    data = request.get_json()

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume = data['nume']
    lat = data['lat']
    lon = data['lon']

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT id FROM tari WHERE id = %s', (id,))
        country = cursor.fetchone()
        if not country:
            return jsonify({"error": "Country not found"}), 404

        cursor.execute('''
            UPDATE tari SET nume = %s, lat = %s, lon = %s
            WHERE id = %s
        ''', (nume, lat, lon, id))
        connection.commit()

    except psycopg2.errors.UniqueViolation as e:
        connection.rollback()
        return jsonify({"error": "Unique constraint violation: another country already has this name"}), 409

    except Exception as e:
        connection.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Country updated successfully"}), 200

@app.route('/api/countries/<int:id>', methods=['DELETE'])
def delete_country(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM tari WHERE id = %s', (id,))
    country = cursor.fetchone()

    if not country:
        return jsonify({"error": "Country not found"}), 404

    cursor.execute('DELETE FROM tari WHERE id = %s', (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Country deleted successfully"}), 200

@app.route('/api/cities', methods=['POST'])
def add_city():
    data = request.get_json()

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data or 'idTara' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume = data['nume']
    lat = data['lat']
    lon = data['lon']
    idTara = data['idTara']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM orase WHERE nume = %s', (nume,))
    existing_city = cursor.fetchone()

    if existing_city:
        cursor.close()
        connection.close()
        return jsonify({"error": "Conflict: City already exists"}), 409

    cursor.execute('SELECT id FROM tari WHERE id = %s', (idTara,))
    country = cursor.fetchone()

    if not country:
        cursor.close()
        connection.close()
        return jsonify({"error": "Country not found"}), 404

    cursor.execute('''
        INSERT INTO orase (nume, lat, lon, idTara)
        VALUES (%s, %s, %s, %s) RETURNING id
    ''', (nume, lat, lon, idTara))
    new_city_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"id": new_city_id}), 201

@app.route('/api/cities', methods=['GET'])
def get_all_city():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id, nume, lat, lon, idTara FROM orase')
    cities = cursor.fetchall()

    cities_list = []
    for city in cities:
        city_data = {
            'id': city[0],
            'nume': city[1],
            'lat': city[2],
            'lon': city[3],
            'idTara': city[4]
        }
        cities_list.append(city_data)

    cursor.close()
    connection.close()

    return jsonify(cities_list), 200

@app.route('/api/cities/country/<int:id>', methods=['GET'])
def get_city_by_country(id):

    connection = get_db_connection()
    cursor = connection.cursor()

    if id:
        cursor.execute('SELECT id, nume, lat, lon, idTara FROM orase WHERE idTara = %s', (id,))
    else:
        cursor.execute('SELECT id, nume, lat, lon, idTara FROM orase')

    cities = cursor.fetchall()

    cities_list = []
    for city in cities:
        city_data = {
            'id': city[0],
            'nume': city[1],
            'lat': city[2],
            'lon': city[3],
            'idTara': city[4]
        }
        cities_list.append(city_data)

    cursor.close()
    connection.close()

    return jsonify(cities_list), 200

@app.route('/api/cities/<int:id>', methods=['PUT'])
def update_city(id):
    data = request.get_json()

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data or 'idTara' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume = data['nume']
    lat = data['lat']
    lon = data['lon']
    idTara = data['idTara']

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT id FROM orase WHERE id = %s', (id,))
        city = cursor.fetchone()
        if not city:
            return jsonify({"error": "City not found"}), 404
        
        cursor.execute('SELECT id FROM tari WHERE id = %s', (idTara,))
        country = cursor.fetchone()
        if not country:
            return jsonify({"error": "Country not found"}), 404

        cursor.execute('''
            UPDATE orase SET nume = %s, lat = %s, lon = %s, idTara = %s
            WHERE id = %s
        ''', (nume, lat, lon, idTara, id))
        connection.commit()

    except psycopg2.errors.UniqueViolation as e:
        connection.rollback()
        return jsonify({"error": "Unique constraint violation: another city already has this name"}), 409
    
    except Exception as e:
        connection.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "City updated successfully"}), 200

@app.route('/api/cities/<int:id>', methods=['DELETE'])
def delete_city(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM orase WHERE id = %s', (id,))
    city = cursor.fetchone()

    if not city:
        cursor.close()
        connection.close()
        return jsonify({"error": "City not found"}), 404

    cursor.execute('DELETE FROM orase WHERE id = %s', (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "City deleted successfully"}), 200

@app.route('/api/temperatures', methods=['POST'])
def add_temperature():
    data = request.get_json()

    if not data or 'idOras' not in data or 'valoare' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    idOras = data['idOras']
    valoare = data['valoare']

    if not isinstance(valoare, float):
        return jsonify({"error": "Bad request, invalid value"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM orase WHERE id = %s', (idOras,))
    city = cursor.fetchone()

    if not city:
        cursor.close()
        connection.close()
        return jsonify({"error": "City not found"}), 404

    cursor.execute('''
        INSERT INTO temperaturi (idOras, valoare, timestamp)
        VALUES (%s, %s, NOW()) RETURNING id
    ''', (idOras, valoare))
    new_temperature_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"id": new_temperature_id}), 201

@app.route('/api/temperatures', methods=['GET'])
def get_temperature_by_date():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
                    SELECT temperaturi.id, valoare, timestamp, lat, lon FROM temperaturi
                    JOIN orase ON temperaturi.idOras = orase.id''')
    temperatures = cursor.fetchall()

    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    from_date = request.args.get('from', type=str)
    until_date = request.args.get('until', type=str)

    if from_date is not None:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if until_date is not None:
        until_date = datetime.strptime(until_date, "%Y-%m-%d")

    filtered_temperatures = []
    for temperature in temperatures:
        temp_id, valoare, temp_timestamp, temp_lat, temp_lon = temperature

        if lat is not None and temp_lat != lat:
            continue
        if lon is not None and temp_lon != lon:
            continue
        if from_date is not None and temp_timestamp < from_date:
            continue
        if until_date is not None and temp_timestamp > until_date:
            continue

        filtered_temperatures.append({
            'id': temp_id,
            'valoare': valoare,
            'timestamp': temp_timestamp.strftime("%Y-%m-%d"),
        })

    cursor.close()
    connection.close()

    return jsonify(filtered_temperatures), 200

@app.route('/api/temperatures/cities/<int:idOras>', methods=['GET'])
def get_temperature_by_city(idOras):
    connection = get_db_connection()
    cursor = connection.cursor()

    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cursor.execute('SELECT id, valoare, timestamp, idOras FROM temperaturi WHERE idOras = %s', (idOras,))
    temperatures = cursor.fetchall()

    new_temperatures = temperatures

    if from_date is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[2] >= from_date]
    if until_date is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[2] <= until_date]

    temperatures_list = []
    for temperature in new_temperatures:
        temperature_data = {
            'id': temperature[0],
            'valoare': temperature[1],
            'timestamp': temperature[2],
        }
        temperatures_list.append(temperature_data)

    cursor.close()
    connection.close()

    return jsonify(temperatures_list), 200

@app.route('/api/temperatures/countries/<int:idTara>', methods=['GET'])
def get_temperature_by_country(idTara):
    connection = get_db_connection()
    cursor = connection.cursor()

    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cursor.execute('''
        SELECT temperaturi.id, temperaturi.valoare, temperaturi.timestamp, orase.idTara
        FROM temperaturi
        JOIN orase ON temperaturi.idOras = orase.id
        WHERE orase.idTara = %s
    ''', (idTara,))
    temperatures = cursor.fetchall()

    new_temperatures = temperatures

    if from_date is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[2] >= from_date]
    if until_date is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[2] <= until_date]

    temperatures_list = []
    for temperature in new_temperatures:
        temperature_data = {
            'id': temperature[0],
            'valoare': temperature[1],
            'timestamp': temperature[2],
        }
        temperatures_list.append(temperature_data)

    cursor.close()
    connection.close()

    return jsonify(temperatures_list), 200

@app.route('/api/temperatures/<int:id>', methods=['PUT'])
def update_temperature(id):
    data = request.get_json()

    if not data or 'valoare' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    valoare = data['valoare']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM temperaturi WHERE id = %s', (id,))
    temperature = cursor.fetchone()

    if not temperature:
        cursor.close()
        connection.close()
        return jsonify({"error": "Temperature not found"}), 404

    cursor.execute('''
        UPDATE temperaturi SET valoare = %s
        WHERE id = %s
    ''', (valoare, id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Temperature updated successfully"}), 200

@app.route('/api/temperatures/<int:id>', methods=['DELETE'])
def delete_temperature(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM temperaturi WHERE id = %s', (id,))
    temperature = cursor.fetchone()

    if not temperature:
        cursor.close()
        connection.close()
        return jsonify({"error": "Temperature not found"}), 404

    cursor.execute('DELETE FROM temperaturi WHERE id = %s', (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Temperature deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
