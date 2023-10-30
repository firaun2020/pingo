from flask import Flask, request, jsonify
import sqlite3
import datetime
import time
from sqlite3 import IntegrityError
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SQLite Database Setup
conn = sqlite3.connect("pingo.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pingo_data (
        id INTEGER PRIMARY KEY,
        status TEXT,
        timestamp DATETIME
    )
""")
conn.commit()

conn_player = sqlite3.connect("players.db")
cursor2 = conn_player.cursor()
cursor2.execute("""
    CREATE TABLE IF NOT EXISTS players_data (
        emp_id TEXT PRIMARY KEY,
        name TEXT,
        emp_dept TEXT,
        emp_status TEXT,
        emp_wins INTEGER,
        emp_loss INTEGER,
        no_result INTEGER,
        regd_at DATETIME
    )
""")

conn_player.commit()


conn_games = sqlite3.connect("games.db")
cursor3 = conn_games.cursor()
cursor3.execute("""
    CREATE TABLE IF NOT EXISTS games_data (
        game_id TEXT PRIMARY KEY,
        player_1 TEXT,
        player_1_emp_id TEXT,
        player_1_color TEXT,
        player_2 TEXT,
        player_2_emp_id TEXT,
        player_2_color TEXT,
        winner_player TEXT,
        winner_colour TEXT,
        loser_player TEXT,
        loser_color TEXT,
        game_result TEXT,
        played_at DATETIME
    )
""")

conn_player.commit()


conn = sqlite3.connect("queue.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS queue_data (
        id INTEGER PRIMARY KEY,
        booker TEXT,
        waiting INTEGER,
        timestamp DATETIME
    )
""")
conn.commit()


@app.route("/", methods=["GET"])
def api_status():
        status = 200
        if 1:
            status = 200
        else:
            status = 400
            
        response = {"status_code": status,
                "content": "Pingo is Up & running!"}
        return jsonify(response)

# Route for writing data to the database
@app.route('/bordStatus', methods=['POST'])
def write_table_status():
    data = request.get_json()
    status = data.get('status')
    timestamp = datetime.datetime.now()
    conn = sqlite3.connect('pingo.db')
    c = conn.cursor()
    # Insert the data into the database
    c.execute("INSERT INTO pingo_data (status, timestamp) VALUES (?, ?)", (status, timestamp))
    conn.commit()
    conn.close()
    return 'Table Status Written to DB!'



@app.route('/bordStatus', methods=['GET'])
def get_table_status():
    conn2 = sqlite3.connect('pingo.db')
    c = conn2.cursor()
    c.execute("SELECT status from pingo_data ORDER BY timestamp DESC LIMIT 1")
    lateststatus =  c.fetchone()
    conn2.close
    return jsonify({'status': lateststatus}) 



@app.route('/signup', methods=['POST'])
def create_player():
    data2 = request.get_json()
    player_name = data2.get('name')
    player_emp_id = data2.get('emp_id')
    player_dept = data2.get('emp_dept')
    player_regd_at = datetime.datetime.now()
    conn4 = sqlite3.connect('players.db')
    c = conn4.cursor()
    # Insert the data into the database
    try:
        c.execute("INSERT INTO players_data (name, emp_id, emp_dept, regd_at) VALUES (?, ?, ?, ?)", 
        (player_name, player_emp_id, player_dept, player_regd_at))
        conn4.commit()
        return 'Players has been registered!'
    except IntegrityError as e:
        return str(e)
    finally:
        conn4.close()



@app.route('/allplayers', methods=['GET'])
def get_all_players():
    conn5 = sqlite3.connect('players.db')
    c = conn5.cursor()
    c.execute("SELECT name, emp_dept, regd_at from players_data")
    all_players =  c.fetchall()
    conn5.close
    return jsonify(all_players) 


@app.route('/iamavailable/<user>/<status>', methods=['PUT'])
def make_me_available(user, status):
    conn6 = sqlite3.connect('players.db')
    c = conn6.cursor()
    newstatus = status
    empid = user
    c.execute("UPDATE players_data SET emp_status = ? WHERE emp_id = ?", (newstatus, empid))   
    conn6.commit()
    return "Your status updated" 

@app.route('/availableplayers', methods=['GET'])
def get_available_players():
    conn7 = sqlite3.connect('players.db')
    c = conn7.cursor()
    c.execute("SELECT name, emp_dept from players_data WHERE emp_status = 'Available'")
    available_players =  c.fetchall()
    conn7.close
    return jsonify(available_players) 



# Gameplay Functions
@app.route('/cardsin', methods=['POST'])
def card_in_game_start():
    card_one = "Alberto"
    card_two = "Daniel"
    gameon_status = "Busy"
    timestamp = datetime.datetime.now()
    conn8 = sqlite3.connect("pingo.db")
    c = conn8.cursor()
    c.execute("INSERT INTO pingo_data (status, timestamp) VALUES (?, ?)", (gameon_status, timestamp))
    conn8.commit()
    return jsonify({"status": gameon_status, "player1": card_one, "player2": card_two })


@app.route('/cardsout', methods=['POST'])
def card_out_game_end():
    card_one = "Alberto"
    card_one_id = "9089"
    card_two_id = "1234"
    card_two = "Daniel"
    winner = "Alberto"
    winner_colour = random.choice(["Yellow", "Red"]) 
    gameon_status = "Ledig"
    timestamp = datetime.datetime.now()
    conn9 = sqlite3.connect("pingo.db")
    c = conn9.cursor()
    c.execute("INSERT INTO pingo_data (status, timestamp) VALUES (?, ?)", (gameon_status, timestamp))
    conn9.commit()
    # Write to game board
    conn10 = sqlite3.connect("games.db")
    c = conn10.cursor()
    c.execute("INSERT INTO games_data (player_1_emp_id, player_1, player_1_color, player_2_emp_id, player_2, player_2_color, winner_player, winner_colour, loser_player, loser_color, game_result, played_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (card_one_id, card_one, "Red", card_two_id, card_two, "Yellow", winner, winner_colour, card_two, "Red", "Completed", timestamp))
    conn10.commit()
    return jsonify({"Reuslt": "Completed", "winner": winner, "winner_color": winner_colour })


@app.route('/allgames', methods=['GET'])
def get_all_games():
    conn11 = sqlite3.connect('games.db')
    c = conn11.cursor()
    c.execute("SELECT * FROM games_data")
    all_games =  c.fetchall()
    conn11.close
    return jsonify(all_games) 


# Queue Handling
@app.route('/book', methods=['POST'])
def add_to_q():
    data = request.get_json()
    booker = data.get('booker')
    waiting = 1
    timestamp = datetime.datetime.now()
    conn12 = sqlite3.connect('queue.db')
    c = conn12.cursor()
    # Insert the data into the database
    c.execute("INSERT INTO queue_data (booker, waiting, timestamp) VALUES (?, ?, ?)", (booker, waiting, timestamp))
    conn12.commit()
    conn12.close()
    return 'Added to Queue!'

@app.route('/book', methods=['GET'])
def show_me_q():
    conn13 = sqlite3.connect('queue.db')
    c = conn13.cursor()
    c.execute("SELECT COUNT(booker) FROM queue_data WHERE waiting = 1")
    counted =  c.fetchone()
    conn13.close()
    return jsonify(counted) 

@app.route('/removebooking', methods=['PUT'])
def remove_booking():
    conn14 = sqlite3.connect('queue.db')
    c = conn14.cursor()
    c.execute("UPDATE queue_data SET waiting = 0 WHERE waiting = 1 AND timestamp = (SELECT MIN(timestamp) FROM queue_data WHERE waiting = 1);")   
    conn14.commit()
    return "Oldest booking deleted" 

if __name__ == "__main__":
    app.run(debug=True)
