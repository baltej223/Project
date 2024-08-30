from flask import Flask, render_template, request, send_file, abort,redirect
import os

app = Flask(__name__)

# Define directories for file storage and downloading
UPLOAD_FOLDER = 'file_storage'
DOWNLOAD_FOLDER = 'files_to_download'

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        pdf_file = request.files['file']
        
        if pdf_file.filename == '':
            return 'No selected file'
        
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Save uploaded files to the file_storage directory
            file_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
            pdf_file.save(file_path)
            return f'File uploaded and saved to {file_path}'
        else:
            return 'Invalid file format. Please upload a PDF file.'
    else:
        return "Invalid method"

@app.route('/download/<filename>', methods=['GET'])
def download_to_client(filename):
    # Construct the file path in the files_to_download directory
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    # Check if the file exists
    if os.path.isfile(file_path):
        # Send the file to the client
        return send_file(file_path, as_attachment=True)
    else:
        # If the file does not exist, return a 404 error
        abort(404)

@app.route("/l")
def l():
    return redirect("/download/Coping Strategies Activity.......pdf")

if __name__ == '__main__':
    app.run(debug=True)
