from flask import Flask, request, jsonify, send_file, render_template_string
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import os
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

app = Flask(__name__)

# Simpan skor dalam list dictionary
scores = []

# Template HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Scoreboard Manager</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            text-decoration: none;
            display: inline-block;
        }
        .button:hover {
            background-color: #45a049;
        }
        .download-btn {
            background-color: #008CBA;
        }
        .download-btn:hover {
            background-color: #007399;
        }
        .refresh-btn {
            background-color: #555555;
        }
        .refresh-btn:hover {
            background-color: #333333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        .button-container {
            text-align: center;
            margin: 20px 0;
        }
        .no-scores {
            text-align: center;
            color: #666;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Quiz Game AR Scoreboard</h1>
        
        <div class="button-container">
            <button class="button refresh-btn" onclick="location.reload()">Refresh Scores</button>
            <a href="/download-csv" class="button download-btn">Download CSV</a>
        </div>

        {% if scores %}
        <table>
            <tr>
                <th>No</th>
                <th>Player Name</th>
                <th>Score</th>
                <th>Timestamp</th>
            </tr>
            {% for score in scores %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ score.player_name }}</td>
                <td>{{ score.score }}</td>
                <td>{{ score.timestamp }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <div class="no-scores">
            <p>No scores have been submitted yet.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    # Urutkan skor dari tertinggi ke terendah
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return render_template_string(HTML_TEMPLATE, scores=sorted_scores)

@app.route('/submit-score', methods=['POST'])
def submit_score():
    try:
        data = request.json
        if not all(key in data for key in ['player_name', 'score']):
            return jsonify({'error': 'Missing required fields'}), 200
        
        score_entry = {
            'player_name': data['player_name'],
            'score': data['score'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        scores.append(score_entry)
        return jsonify({'message': 'Score submitted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 200

@app.route('/get-scores', methods=['GET'])
def get_scores():
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_scores)

@app.route('/download-csv', methods=['GET'])
def download_csv():
    try:
        if not scores:
            return "No scores available to download", 404
            
        df = pd.DataFrame(scores)
        csv_filename = 'scoreboard.csv'
        df.to_csv(csv_filename, index=False)
        
        return send_file(
            csv_filename,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'scoreboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    finally:
        if os.path.exists(csv_filename):
            os.remove(csv_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
