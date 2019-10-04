import logging
import os

from flask import request, flash, send_file
from werkzeug.utils import redirect, secure_filename

from core import parser
from server import app
from utils import utils

log = logging.getLogger()


@app.route('/')
def hello_world():
    return app.send_static_file('upload.html')


@app.route('/', methods=['POST'])
def parse_data():
    # check if the post request has the file part
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file choosed :/', category="error")
        log.debug("File not in request")
        return redirect(request.url)  # Return to HTML page [GET]
    log.debug("File in request")
    file = request.files['file']
    fileName = os.path.join("/tmp/", secure_filename(file.filename))
    file.save(fileName)
    extract_file = parser.unzip_file(fileName)
    tmp_name = "/tmp/{}".format(file.filename.replace(".zip", ".txt")) #TODO: Remove
    parser.parse(extract_file, tmp_name)
    utils.remove(file.filename)
    return send_file(tmp_name, as_attachment=True)


@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
    return app.send_static_file('404.html')


@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
    return app.send_static_file('500.html')


@app.after_request
def secure_headers(response):
    """
    Apply securiy headers to the response call
    :return:
    """
    return utils.secure_request(response)
