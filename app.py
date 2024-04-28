from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'review'
mysql = MySQL(app)

def create_response(data, status_code, message):
    response = {
        'timestamp': datetime.now().isoformat(),
        'status': status_code,
        'message': message,
        'data': data
    }
    return jsonify(response)

@app.route('/ulasan', methods=['GET', 'POST'])
def ulasan():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM ulasan")

        column_names = [i[0] for i in cursor.description]

        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))

        cursor.close()
        return create_response(data, 200, 'Success')

    elif request.method == 'POST':
        try:
            # get data from request
            id_dokter = request.json['idDokter']
            id_user = request.json['idUser']
            nama_user = request.json['namaUser']
            nama_dokter = request.json['namaDokter']
            poli = request.json['poli']
            ulasan_text = request.json['ulasan']

            # Open connection and insert to db
            cursor = mysql.connection.cursor()
            sql = "INSERT INTO ulasan (idDokter, idUser, namaUser, namaDokter, poli, ulasan) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (id_dokter, id_user, nama_user, nama_dokter, poli, ulasan_text)
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()

            return create_response(None, 201, 'Ulasan berhasil ditambahkan')
        except KeyError:
            return create_response(None, 400, 'Permintaan tidak valid: Kolom yang dibutuhkan tidak ada')
        
@app.route('/detailulasan')
def detailulasan():
    # Mendapatkan semua parameter dari query string
    parameters = request.args.to_dict()

    if parameters:
        cursor = mysql.connection.cursor()

        # Membangun query SQL berdasarkan parameter yang diberikan
        sql = 'SELECT * FROM ULASAN WHERE '
        conditions = []
        values = []

        for key, value in parameters.items():
            conditions.append(f"{key} = %s")
            values.append(value)

        sql += ' AND '.join(conditions)

        cursor.execute(sql, tuple(values))

        column_names = [i[0] for i in cursor.description]

        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))

        cursor.close()

        if data:
            return create_response(data, 200, 'Success')
        else:
            return create_response(None, 404, 'Not Found: Studio not found')
    else:
        return create_response(None, 400, 'Bad Request: No parameters provided')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)