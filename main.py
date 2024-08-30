from flask import Flask, render_template, request, send_file, abort, jsonify
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import fitz  # 

app = Flask(__name__)

# Define directories for file storage and downloading
UPLOAD_FOLDER = 'file_storage'
DOWNLOAD_FOLDER = 'files_to_download'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    files = request.files.getlist('files')
    if not files:
        return jsonify({'success': False, 'message': 'No files selected'})

    uploaded_files = []
    invalid_files = []
    
    for file in files:
        if file.filename == '':
            continue
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            uploaded_files.append(file.filename)
        else:
            invalid_files.append(file.filename)

    if uploaded_files:
        message = f'Files uploaded successfully: {", ".join(uploaded_files)}'
    else:
        message = 'No valid files uploaded.'

    if invalid_files:
        message += f' Invalid files: {", ".join(invalid_files)}'

    return jsonify({'success': True, 'message': message})

@app.route('/list_pdfs', methods=['GET'])
def list_pdfs():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    return jsonify({'pdfs': files})

@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    data = request.get_json()
    pdf_files = data.get('pdfs')

    if not pdf_files or len(pdf_files) < 2:
        return jsonify({'success': False, 'message': 'At least two PDF files are required for merging'})

    merger = PdfMerger()

    for filename in pdf_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            merger.append(file_path)
        else:
            return jsonify({'success': False, 'message': f'File not found: {filename}'})

    merged_filename = 'merged_output.pdf'
    merged_file_path = os.path.join(DOWNLOAD_FOLDER, merged_filename)
    merger.write(merged_file_path)
    merger.close()

    return jsonify({'success': True, 'filename': merged_filename})

@app.route('/split_pdf', methods=['POST'])
def split_pdf():
    data = request.get_json()
    filename = data.get('filename')
    start_page = data.get('start_page')
    end_page = data.get('end_page')

    if not filename or start_page is None or end_page is None:
        return jsonify({'success': False, 'message': 'Invalid input'})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found'})

    pdf_reader = PdfReader(file_path)
    pdf_writer = PdfWriter()

    if start_page < 0 or end_page >= len(pdf_reader.pages) or start_page > end_page:
        return jsonify({'success': False, 'message': 'Invalid page range'})

    for page_num in range(start_page, end_page + 1):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    split_filename = f'split_{start_page}_{end_page}.pdf'
    split_file_path = os.path.join(DOWNLOAD_FOLDER, split_filename)
    with open(split_file_path, 'wb') as out_file:
        pdf_writer.write(out_file)

    return jsonify({'success': True, 'filename': split_filename})

@app.route('/compress_pdf', methods=['POST'])
def compress_pdf():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({'success': False, 'message': 'Invalid input'})

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found'})

    pdf_document = fitz.open(file_path)
    compressed_filename = f'compressed_{filename}'
    compressed_file_path = os.path.join(DOWNLOAD_FOLDER, compressed_filename)
    
    pdf_document.save(compressed_file_path, deflate=True)
    pdf_document.close()

    return jsonify({'success': True, 'filename': compressed_filename})

@app.route('/download/<filename>', methods=['GET'])
def download_to_client(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
