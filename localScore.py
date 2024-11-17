from flask import Flask, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Simpan skor dalam list dictionary
scores = []

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/submit-score', methods=['POST'])
def submit_score():
    try:
        data = request.json
        # Pastikan data yang diperlukan ada
        if not all(key in data for key in ['player_name', 'score']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Tambahkan timestamp
        score_entry = {
            'player_name': data['player_name'],
            'score': data['score'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        scores.append(score_entry)
        return jsonify({'message': 'Score submitted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get-scores', methods=['GET'])
def get_scores():
    # Urutkan skor dari tertinggi ke terendah
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_scores)


@app.route('/download-csv', methods=['GET'])
def download_csv():
    try:
        # Buat DataFrame dari scores
        df = pd.DataFrame(scores)

        # Simpan ke CSV
        csv_filename = 'scoreboard.csv'
        df.to_csv(csv_filename, index=False)

        # Kirim file
        return send_file(
            csv_filename,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'scoreboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    finally:
        # Hapus file setelah dikirim
        if os.path.exists(csv_filename):
            os.remove(csv_filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)