from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from tqdm import tqdm

app = Flask(__name__)

class Encryption:
    def __init__(self, filename):
        self.filename = filename

    def encrypt_file(self):
        try:
            original_information = open(self.filename, 'rb')
        except (IOError, FileNotFoundError):
            print(f'File with name {self.filename} is not found.')
            return None

        try:
            secure_filename_str = secure_filename(self.filename)
            encrypted_file_name = 'cipher_' + secure_filename_str
            encrypted_file_object = open(encrypted_file_name, 'wb')
            content = original_information.read()
            key = 192
            print('Encryption Process is in progress...!')
            for val in tqdm(content):
                encrypted_file_object.write(bytes([val ^ key]))
        except Exception as e:
            print(f'Something went wrong with {self.filename}: {e}')
        finally:
            encrypted_file_object.close()
            original_information.close()
        return encrypted_file_name

class Decryption:
    def __init__(self, filename):
        self.filename = filename

    def decrypt_file(self):
        try:
            encrypted_file_object = open(self.filename, 'rb')
        except (FileNotFoundError, IOError):
            print(f'File with name {self.filename} is not found')
            return None

        try:
            secure_filename_str = secure_filename(self.filename)
            decrypted_file = 'decrypted_' + secure_filename_str
            decrypted_file_object = open(decrypted_file, 'wb')
            cipher_text = encrypted_file_object.read()
            key = 192
            print('Decryption Process is in progress...!')
            for val in tqdm(cipher_text):
                decrypted_file_object.write(bytes([val ^ key]))
        except Exception as e:
            print(f'Some problem with Ciphertext unable to handle: {e}')
        finally:
            encrypted_file_object.close()
            decrypted_file_object.close()
        return decrypted_file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    try:
        secure_filename_str = secure_filename(file.filename)
        file.save(secure_filename_str)  # Save the file with a secure filename

        action = request.form.get('action')

        if action == 'encrypt':
            encryption = Encryption(secure_filename_str)
            encrypted_filename = encryption.encrypt_file()

            if encrypted_filename:
                return send_file(encrypted_filename, as_attachment=True)
            else:
                return jsonify({"error": "Error during encryption"})
        elif action == 'decrypt':
            decryption = Decryption(secure_filename_str)
            decrypted_filename = decryption.decrypt_file()

            if decrypted_filename:
                return send_file(decrypted_filename, as_attachment=True)
            else:
                return jsonify({"error": "Error during decryption"})
        else:
            return jsonify({"error": "Invalid action"})
    except Exception as e:
        return jsonify({"error": f"Error during processing: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
