import flask
import flask_cors
import os
import json

app = flask.Flask(__name__)
flask_cors.CORS(app)  # разрешаем CORS для любого домена

UPLOAD_DIR = "upload"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    form_json = flask.request.form.get("json")
    if not form_json:
        return "no json", 400

    data = json.loads(form_json)
    date = str(data.get("date", ""))
    subject = str(data.get("subject", ""))

    if not date or not subject:
        return "missing fields", 400

    if "to_upload" not in flask.request.files:
        return "no file part 'to_upload'", 400

    to_upload = flask.request.files["to_upload"]
    if to_upload.filename == "":
        return "no filename", 400

    folder = os.path.join(UPLOAD_DIR, date, subject)
    os.makedirs(folder, exist_ok=True)

    to_upload.save(os.path.join(folder, to_upload.filename))
    return "file saved", 200

@app.route("/get", methods=["POST"])
def get_files():
    data = flask.request.get_json()
    date = data.get("date")
    subject = data.get("subject")

    folder = os.path.join(UPLOAD_DIR, date, subject)
    if not os.path.exists(folder):
        return flask.jsonify([])

    files = []
    for name in os.listdir(folder):
        ext = name.lower()
        if ext.endswith(IMAGE_EXTS):
            files.append({"type": "image", "url": f"/files/{date}/{subject}/{name}"})
        else:
            files.append({"type": "file", "name": name, "url": f"/files/{date}/{subject}/{name}"})
    return flask.jsonify(files)

@app.route("/upload/<date>/<subject>/<filename>")
def serve_file(date, subject, filename):
    return flask.send_from_directory(os.path.join(UPLOAD_DIR, date, subject), filename)

@app.route("/tree")
def get_tree():
    def build_tree(path):
        result = {"name": os.path.basename(path), "type": "folder", "children": []}
        try:
            for item in sorted(os.listdir(path)):
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    result["children"].append(build_tree(full))
                else:
                    result["children"].append({
                        "name": item,
                        "type": "file",
                        "url": "/" + full.replace(os.getcwd(), "").replace("\\", "/")
                    })
        except Exception:
            pass
        return result

    tree = build_tree(UPLOAD_DIR)
    return flask.jsonify(tree)

@app.route("/mkdir", methods=["POST"])
def mkdir():
    data = flask.request.get_json()
    path = data.get("path")
    name = data.get("name")
    if not path or not name:
        return "missing path or name", 400
    folder_path = os.path.join(UPLOAD_DIR, path, name)
    try:
        os.makedirs(folder_path, exist_ok=False)
    except FileExistsError:
        return "folder exists", 400
    return "folder created", 200

@app.route("/upload_to_folder", methods=["POST"])
def upload_to_folder():
    folder = flask.request.form.get("folder")
    if "to_upload" not in flask.request.files or not folder:
        return "missing file or folder", 400
    file = flask.request.files["to_upload"]
    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)
    file.save(os.path.join(UPLOAD_DIR, folder, file.filename))
    return "file uploaded", 200


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
