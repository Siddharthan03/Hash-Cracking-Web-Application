# Hash-Cracking-Web-Application

INTRODUCTION

This project is a web application for hash cracking. It allows users to upload files containing hashes, attempts to crack these hashes using various APIs, and then processes the results. Users can also generate hashed words and download the results.

TECHNOLOGIES USED
- [ ] Python
- [ ] Flask
- [ ] HTML
- [ ] Concurrent Futures
- [ ] Regular Expressions
- [ ] Subprocess

API ENDPOINTS
* GET /
    * Renders the main page.
* POST /crack
    * Cracks a single hash value.
    * Request Data: hashvalue (string)
    * Response: Original value and algorithm if found, otherwise an error message.
* POST /upload
    * Uploads a file containing hashes.
    * Request Data: file (file)
    * Response: Filename of the uploaded file or an error message.
* POST /process_file
    * Processes the uploaded file to crack the hashes.
    * Request Data: filename (string), thread_count (integer, optional)
    * Response: JSON containing the results and the CSV filename or an error message.
* POST /generate_hashed_words
    * Generates hashed words using an external script.
    * Response: Sends the generated CSV file for download or an error message.
* GET /download/<filename>
    * Downloads the specified processed file.
    * Response: Sends the requested file or an error message.
 
USAGE

1. Upload a File:
    * Go to the main page.
    * Upload a file containing hashes.
2. Crack Hashes:
    * Use the /crack endpoint to crack individual hashes.
    * Use the /process_file endpoint to process and crack hashes from an uploaded file.
3. Generate Hashed Words:
    * Use the /generate_hashed_words endpoint to generate a CSV file of hashed words.
4. Download Processed Files:
    * Use the /download/<filename> endpoint to download the processed files.

NOTES

* Ensure that the UPLOAD_FOLDER, PROCESSED_FOLDER, and GENERATED_HASH_FOLDER directories exist before running the application.
* Adjust the thread count for processing files based on your system's capabilities.
* The application currently supports cracking MD5, SHA1, SHA256, SHA384, and SHA512 hashes using multiple APIs. Ensure you have the appropriate API handlers configured in api_handlers.py.
