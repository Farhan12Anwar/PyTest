from flask import Flask, render_template, request, redirect, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Accept all file types (optional: restrict to PDF/DOC/DOCX if needed)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files')
        for file in files:
            if file.filename == '':
                continue
            filename = file.filename.replace("\\", "/")  # Normalize Windows paths
            if allowed_file(filename):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
        return redirect('/')
    
from flask import jsonify

@app.route('/delete_all', methods=['DELETE'])
def delete_all_files():
    folder = app.config['UPLOAD_FOLDER']
    deleted_files = []

    for root, dirs, files in os.walk(folder, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
        for dir in dirs:
            try:
                os.rmdir(os.path.join(root, dir))
            except OSError:
                pass  # Skip non-empty dirs

    return jsonify({'status': 'success', 'deleted': deleted_files})

    
    # Show all uploaded files
    uploaded_files = []
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), app.config['UPLOAD_FOLDER'])
            uploaded_files.append(rel_path.replace("\\", "/"))
    return render_template('index.html', files=uploaded_files)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
