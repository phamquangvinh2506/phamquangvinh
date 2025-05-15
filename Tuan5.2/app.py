from flask import Flask, render_template, request, send_file, redirect, flash
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # cần thiết để flash thông báo
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def des_encrypt(file_path, key, output_path):
    cipher = DES.new(key.encode('utf-8'), DES.MODE_ECB)
    with open(file_path, 'rb') as f:
        data = f.read()
    padded_data = pad(data, DES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
        print("Saving file to:", output_path)

def des_decrypt(file_path, key, output_path):
    cipher = DES.new(key.encode('utf-8'), DES.MODE_ECB)
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    try:
        unpadded_data = unpad(decrypted_data, DES.block_size)
    except ValueError:
        raise ValueError("Invalid key or corrupted file.")
    with open(output_path, 'wb') as f:
        f.write(unpadded_data)
        print("Saving file to:", output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        key = request.form.get('key')
        operation = request.form.get('operation')

        if not file or not key or len(key) != 8:
            flash('Please upload a file and enter an 8-character DES key.')
            return redirect(request.url)

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_path)

        output_filename = f"{operation}ed_{file.filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        try:
            if operation == 'encrypt':
                des_encrypt(input_path, key, output_path)
            elif operation == 'decrypt':
                des_decrypt(input_path, key, output_path)
        except Exception as e:
            flash(str(e))
            return redirect(request.url)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    return render_template('index.html')
    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
