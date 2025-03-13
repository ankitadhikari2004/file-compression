import os
import time
import glob
from flask import Flask, redirect, render_template, request, send_file

# Initialize the Flask application
app = Flask(__name__)

# Global variables for filename and file type
global filename
global ftype

@app.route("/")
def home():
    """
    This route is for the home page.
    It also deletes old files from the 'uploads' and 'downloads' directories
    to keep storage clean before rendering the home page.
    """

    # Delete all files in the 'uploads' directory
    filelist = glob.glob('uploads/*')
    for f in filelist:
        os.remove(f)

    # Delete all files in the 'downloads' directory
    filelist = glob.glob('downloads/*')
    for f in filelist:
        os.remove(f)

    # Render the home page template
    return render_template("home.html")

# Set the directory for file uploads
app.config["FILE_UPLOADS"] = "/Users/ankitadhikari/Downloads/Huffman_Coding-main/uploads"

@app.route("/compress", methods=["GET", "POST"])
def compress():
    """
    This route handles file compression.
    - On GET request: Displays the compression page.
    - On POST request: Uploads a file, runs the compression binary, and moves the compressed file to downloads.
    """

    if request.method == "GET":
        # Render the compression page with default check value (0)
        return render_template("compress.html", check=0)
    else:
        # Get the uploaded file
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            # Store the filename globally
            global filename
            global ftype
            filename = up_file.filename
            print(up_file.filename)

            # Save the uploaded file to the configured uploads directory
            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))

            # Execute the compression program (C binary file)
            os.system('./huffcompress uploads/{}'.format(filename))

            # Extract filename without extension
            filename = filename[:filename.index(".", 1)]
            ftype = "-compressed.bin"

            # Wait for the compressed file to appear in the uploads folder
            while True:
                if 'uploads/{}-compressed.bin'.format(filename) in glob.glob('uploads/*-compressed.bin'):
                    # Move the compressed file to the downloads directory
                    os.system('mv uploads/{}-compressed.bin downloads/'.format(filename))
                    break

            # Render the compression page with success check (1)
            return render_template("compress.html", check=1)

        else:
            print("ERROR: No file uploaded.")
            return render_template("compress.html", check=-1)  # Error state

@app.route("/decompress", methods=["GET", "POST"])
def decompress():
    """
    This route handles file decompression.
    - On GET request: Displays the decompression page.
    - On POST request: Uploads a file, runs the decompression binary, and moves the decompressed file to downloads.
    """

    if request.method == "GET":
        # Render the decompression page with default check value (0)
        return render_template("decompress.html", check=0)
    else:
        # Get the uploaded file
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            # Store the filename globally
            global filename
            global ftype
            filename = up_file.filename
            print(up_file.filename)

            # Save the uploaded file to the configured uploads directory
            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))

            # Execute the decompression program (C binary file)
            os.system('./huffdecompress uploads/{}'.format(filename))

            # Open the uploaded file in binary mode
            f = open('uploads/{}'.format(filename), 'rb')

            # Read the first byte to get the length of the file extension
            ext_length = int(f.read(1))

            # Read the actual file extension and decode it
            ftype = "-decompressed." + f.read(ext_length).decode("utf-8")

            # Extract filename without "-compressed" suffix
            filename = filename[:filename.index("-", 1)]

            # Wait for the decompressed file to appear in the uploads folder
            while True:
                if 'uploads/{}{}'.format(filename, ftype) in glob.glob('uploads/*-decompressed.*'):
                    # Move the decompressed file to the downloads directory
                    os.system('mv uploads/{}{} downloads/'.format(filename, ftype))
                    break

            # Render the decompression page with success check (1)
            return render_template("decompress.html", check=1)

        else:
            print("ERROR: No file uploaded.")
            return render_template("decompress.html", check=-1)  # Error state

@app.route("/download")
def download_file():
    """
    This route handles file downloads.
    - It constructs the file path from the 'downloads' folder and sends it to the user.
    """

    global filename
    global ftype

    # Construct the full path of the file to be downloaded
    path = "/Users/ankitadhikari/Downloads/Huffman_Coding-main/downloads/" + filename + ftype

    # Send the file as an attachment to the user
    return send_file(path, as_attachment=True)

# Restart application whenever changes are made
if __name__ == "__main__":
    app.run(debug=True)
