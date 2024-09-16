from flask import Flask, render_template, jsonify
import sqlite3
import random
import time
from threading import Thread
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('sensor_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar o banco de dados se ele não existir
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temperatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Função para simular o sensor de temperatura e inserir dados no banco
def simulate_sensor():
    conn = get_db_connection()
    cursor = conn.cursor()
    while True:
        temp = round(random.uniform(20.0, 30.0), 2)  # Simular uma temperatura entre 20°C e 30°C
        cursor.execute('INSERT INTO temperatures (temperature) VALUES (?)', (temp,))
        conn.commit()
        print(f'Temperatura {temp} registrada no banco de dados.')
        time.sleep(5)  # Simular coleta de dados a cada 5 segundos


@app.route('/api/temperatures')
def get_temperatures():
    conn = get_db_connection()
    temperatures = conn.execute('SELECT * FROM temperatures ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    
    data = [{"timestamp": row['timestamp'], "temperature": row['temperature']} for row in temperatures]
    return jsonify(data)

# Rota para exibir o gráfico
@app.route('/')
def index():
    conn = get_db_connection()
    temperatures = conn.execute('SELECT * FROM temperatures').fetchall()
    conn.close()
    
    # Extraindo dados de temperatura e timestamps
    temps = [row['temperature'] for row in temperatures]
    timestamps = [row['timestamp'] for row in temperatures]
    
    # Criar gráfico Plotly
    graph = go.Figure(data=[go.Scatter(x=timestamps, y=temps, mode='lines', name='Temperatura')])
    graph.update_layout(title='Monitoramento de Temperatura', xaxis_title='Horário', yaxis_title='Temperatura (°C)')
    
    # Converter o gráfico para JSON
    graph_json = pio.to_json(graph)
    
    return render_template('index.html', graph_json=graph_json)

if __name__ == '__main__':
    print("Iniciando a aplicação...")
    init_db()
    print("Banco de dados inicializado.")

    print("Iniciando thread do sensor...")
    sensor_thread = Thread(target=simulate_sensor)
    sensor_thread.daemon = True
    sensor_thread.start()
    print("Thread do sensor iniciada.")

    print("Iniciando o servidor Flask...")
    app.run(debug=True)
