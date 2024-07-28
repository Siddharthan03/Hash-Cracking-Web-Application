import os
import re
import concurrent.futures
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from api_handlers import alpha, beta, gamma, delta, theta, crackstation, hashes_org
import time
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['GENERATED_HASH_FOLDER'] = 'generated_hash'

md5 = [gamma, alpha, beta, theta, delta, crackstation, hashes_org]
sha1 = [alpha, beta, theta, delta, crackstation, hashes_org]
sha256 = [alpha, beta, theta, crackstation, hashes_org]
sha384 = [alpha, beta, theta, crackstation, hashes_org]
sha512 = [alpha, beta, theta, crackstation, hashes_org]

def crack(hashvalue):
    length_to_funcs = {
        32: ('MD5', md5),
        40: ('SHA1', sha1),
        64: ('SHA-256', sha256),
        96: ('SHA-384', sha384),
        128: ('SHA-512', sha512)
    }
    hash_length = len(hashvalue)
    if hash_length in length_to_funcs:
        for api in length_to_funcs[hash_length][1]:
            r = api(hashvalue, length_to_funcs[hash_length][0].lower())
            if r:  # Check if r is not None or not an error indicator
                return r, length_to_funcs[hash_length][0]
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crack', methods=['POST'])
def crack_hash():
    hashvalue = request.form['hashvalue']
    result, algo = crack(hashvalue)
    if result:
        return jsonify({'original': result, 'algorithm': algo})
    else:
        return jsonify({'error': 'Hash not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            return jsonify({'filename': filename}), 200
        except Exception as e:
            return jsonify({'error': f'File upload failed: {str(e)}'}), 500
    return jsonify({'error': 'File upload failed'}), 400

@app.route('/process_file', methods=['POST'])
def process_file():
    start_time = time.time()  # Start time for debugging
    filename = request.json['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thread_count = request.json.get('thread_count', 4)

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return jsonify({'error': 'File not found'}), 404

    try:
        found = set()
        with open(filepath, 'r') as f:
            lines = [line.strip('\n') for line in f]
        for line in lines:
            matches = re.findall(
                r'[a-f0-9]{128}|[a-f0-9]{96}|[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32}', line)
            found.update(matches)

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            future_to_hash = {executor.submit(crack, hashvalue): hashvalue for hashvalue in found}
            for future in concurrent.futures.as_completed(future_to_hash):
                hashvalue = future_to_hash[future]
                try:
                    original, algo = future.result()
                    if original:
                        results[hashvalue] = {'original': original, 'algorithm': algo}
                except Exception as exc:
                    print(f'Hash {hashvalue} generated an exception: {exc}')

        csv_filename = os.path.splitext(filename)[0] + '_processed.csv'
        csv_filepath = os.path.join(app.config['PROCESSED_FOLDER'], csv_filename)
        os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

        # Debugging output
        print(f'Attempting to create CSV file at: {csv_filepath}')
        
        with open(csv_filepath, 'w') as csv_file:
            csv_file.write('hashvalue,original,algorithm\n')
            for hashvalue, data in results.items():
                csv_file.write(f'{hashvalue},{data["original"]},{data["algorithm"]}\n')

        end_time = time.time()  # End time for debugging
        print(f'Processing time: {end_time - start_time} seconds')  # Debugging output
        print(f'CSV file created at: {csv_filepath}')  # Debugging output

        return jsonify({'results': results, 'csv_filename': csv_filename}), 200
    except Exception as e:
        print(f'Error during file processing: {str(e)}')  # Debugging output
        return jsonify({'error': f'File processing failed: {str(e)}'}), 500

@app.route('/generate_hashed_words', methods=['POST'])
def generate_hashed_words():
    try:
        result = subprocess.run(['python3', 'generate_hashed_words.py'], capture_output=True, text=True, check=True)
        if result.returncode != 0:
            return jsonify({'error': 'Failed to generate hashed words', 'details': result.stderr}), 500
        return send_file(os.path.join(app.config['GENERATED_HASH_FOLDER'], 'hashed_words.csv'), as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to generate hashed words: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_HASH_FOLDER'], exist_ok=True)
    app.run(debug=True)