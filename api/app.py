from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Conectarea la baza de date PostgreSQL
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

    # Obtinem datele din body-ul cererii
    data = request.get_json()
    
    # Validam inputul
    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400
    
    nume_tara = data['nume']
    latitudine = data['lat']
    longitudine = data['lon']

    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Verificam daca tara exista deja (prin nume)
    cursor.execute('SELECT id FROM tari WHERE nume_tara = %s', (nume_tara,))
    existing_country = cursor.fetchone()
    
    if existing_country:
        cursor.close()
        connection.close()
        return jsonify({"error": "Conflict: Country already exists"}), 409

    # Adaugam tara in baza de date
    cursor.execute('''
        INSERT INTO tari (nume_tara, latitudine, longitudine) 
        VALUES (%s, %s, %s) RETURNING id
    ''', (nume_tara, latitudine, longitudine))
    new_country_id = cursor.fetchone()[0]
    
    connection.commit()  # Confirmam tranzactia
    cursor.close()
    connection.close()

    # Returnam raspunsul de succes cu ID-ul tarii
    return jsonify({"id": new_country_id}), 201

@app.route('/api/countries', methods=['GET'])
def get_all_country():
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Interogăm baza de date pentru a obține toate țările
    cursor.execute('SELECT id, nume_tara, latitudine, longitudine FROM tari')
    countries = cursor.fetchall()
    
    # Creăm un listă de dicționare pentru a structura răspunsul
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

    # Returnăm răspunsul în format JSON
    return jsonify(countries_list), 200

@app.route('/api/countries/', methods=['PUT'])
def update_country():

    data = request.get_json()

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume_tara = data['nume']
    latitudine = data['lat']
    longitudine = data['lon']

    connection = get_db_connection()
    cursor = connection.cursor()

    id = request.args.get('id')

    try:
        # Check if the country exists
        cursor.execute('SELECT id FROM tari WHERE id = %s', (id,))
        country = cursor.fetchone()
        if not country:
            return jsonify({"error": "Country not found"}), 404

        # Attempt to update the record
        cursor.execute('''
            UPDATE tari SET nume_tara = %s, latitudine = %s, longitudine = %s
            WHERE id = %s
        ''', (nume_tara, latitudine, longitudine, id))
        connection.commit()

    except psycopg2.errors.UniqueViolation as e:
        # Handle unique constraint violations
        connection.rollback()
        return jsonify({"error": "Unique constraint violation: another country already has this name"}), 409

    except Exception as e:
        # Handle other unexpected exceptions
        connection.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    finally:
        # Ensure resources are always closed
        cursor.close()
        connection.close()

    return jsonify({"message": "Country updated successfully"}), 200

@app.route('/api/countries/', methods=['DELETE'])
def delete_country():
    connection = get_db_connection()
    cursor = connection.cursor()

    id = request.args.get('id')

    country = cursor.execute('SELECT id FROM tari WHERE id = %s', (id,))
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

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data or 'tara_id' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume_oras = data['nume']
    latitudine = data['lat']
    longitudine = data['lon']
    tara_id = data['tara_id']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM tari WHERE id = %s', (tara_id,))
    country = cursor.fetchone()

    if not country:
        cursor.close()
        connection.close()
        return jsonify({"error": "Country not found"}), 404

    cursor.execute('''
        INSERT INTO orase (nume_oras, latitudine, longitudine, tara_id)
        VALUES (%s, %s, %s, %s) RETURNING id
    ''', (nume_oras, latitudine, longitudine, tara_id))
    new_city_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"id": new_city_id}), 201

@app.route('/api/cities', methods=['GET'])
def get_all_city():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id, nume_oras, latitudine, longitudine, id_tara FROM orase')
    cities = cursor.fetchall()

    cities_list = []
    for city in cities:
        city_data = {
            'id': city[0],
            'nume': city[1],
            'lat': city[2],
            'lon': city[3],
            'id_tara': city[4]
        }
        cities_list.append(city_data)

    cursor.close()
    connection.close()

    return jsonify(cities_list), 200

@app.route('/api/cities/country/', methods=['GET'])
def get_city_by_country():

    connection = get_db_connection()
    cursor = connection.cursor()

    id = request.args.get('id')

    if id:
        cursor.execute('SELECT id, nume_oras, latitudine, longitudine, id_tara FROM orase WHERE id_tara = %s', (id,))
    else:
        cursor.execute('SELECT id, nume_oras, latitudine, longitudine, id_tara FROM orase')

    cities = cursor.fetchall()

    cities_list = []
    for city in cities:
        city_data = {
            'id': city[0],
            'nume': city[1],
            'lat': city[2],
            'lon': city[3],
            'id_tara': city[4]
        }
        cities_list.append(city_data)

    cursor.close()
    connection.close()

    return jsonify(cities_list), 200

@app.route('/api/cities/', methods=['PUT'])
def update_city():
    data = request.get_json()

    if not data or 'nume' not in data or 'lat' not in data or 'lon' not in data or 'tara_id' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    nume_oras = data['nume']
    latitudine = data['lat']
    longitudine = data['lon']
    tara_id = data['tara_id']

    connection = get_db_connection()
    cursor = connection.cursor()

    id = request.args.get('id')

    cursor.execute('SELECT id FROM orase WHERE id = %s', (id,))
    city = cursor.fetchone()

    if not city:
        cursor.close()
        connection.close()
        return jsonify({"error": "City not found"}), 404

    cursor.execute('''
        UPDATE orase SET nume_oras = %s, latitudine = %s, longitudine = %s, tara_id = %s
        WHERE id = %s
    ''', (nume_oras, latitudine, longitudine, tara_id, id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "City updated successfully"}), 200

@app.route('/api/cities/', methods=['DELETE'])
def delete_city():
    connection = get_db_connection()
    cursor = connection.cursor()

    id = request.args.get('id')

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

    if not data or 'id_oras' not in data or 'valoare' not in data:
        return jsonify({"error": "Bad request, missing fields"}), 400

    id_oras = data['id_oras']
    valoare = data['valoare']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM orase WHERE id = %s', (id_oras,))
    city = cursor.fetchone()

    if not city:
        cursor.close()
        connection.close()
        return jsonify({"error": "City not found"}), 404

    cursor.execute('''
        INSERT INTO temperaturi (id_oras, valoare)
        VALUES (%s, %s) RETURNING id
    ''', (id_oras, valoare))
    new_temperature_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"id": new_temperature_id}), 201

@app.route('/api/temperatures', methods=['GET'])
def get_temperature_by_date():
    connection = get_db_connection()
    cursor = connection.cursor()

    lat = request.args.get('lat')
    lon = request.args.get('lon')
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cursor.execute('SELECT id, valoare, timestamp, id_oras FROM temperaturi')
    temperatures = cursor.fetchall()

    new_temperatures = temperatures

    if lat is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[3] == lat]
    if lon is not None:
        new_temperatures = [temperature for temperature in new_temperatures if temperature[3] == lon]
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

@app.route('/api/temperatures/cities/', methods=['GET'])
def get_temperature_by_city():
    connection = get_db_connection()
    cursor = connection.cursor()

    id_oras = request.args.get('id_oras')
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cursor.execute('SELECT id, valoare, timestamp, id_oras FROM temperaturi WHERE id_oras = %s', (id_oras,))
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

@app.route('/api/temperatures/countries/', methods=['GET'])
def get_temperature_by_country():
    connection = get_db_connection()
    cursor = connection.cursor()

    id_tara = request.args.get('id_tara')
    from_date = request.args.get('from')
    until_date = request.args.get('until')

    cursor.execute('''
        SELECT temperaturi.id, temperaturi.valoare, temperaturi.timestamp, orase.id_tara
        FROM temperaturi
        JOIN orase ON temperaturi.id_oras = orase.id
        WHERE orase.id_tara = %s
    ''', (id_tara,))
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

@app.route('/api/temperatures/', methods=['PUT'])
def update_temperature():
    data = request.get_json()

    id = request.args.get('id')

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

@app.route('/api/temperatures/', methods=['DELETE'])
def delete_temperature():

    id = request.args.get('id')

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
