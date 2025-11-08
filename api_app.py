import flask, flask_cors, os, json, shutil

app = flask.Flask(__name__)
flask_cors.CORS(app)

UPLOAD_DIR = "upload"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/tree")
def get_tree():
    def build_tree(path):
        result = {"name": os.path.basename(path), "type":"folder", "children":[]}
        try:
            for item in sorted(os.listdir(path)):
                full = os.path.join(path, item)
                if os.path.isdir(full):
                    result["children"].append(build_tree(full))
                else:
                    result["children"].append({
                        "name": item,
                        "type":"file",
                        "url": full.replace(os.getcwd(),"").replace("\\","/")
                    })
        except Exception: pass
        return result
    tree = build_tree(UPLOAD_DIR)
    return flask.jsonify(tree)

@app.route("/mkdir", methods=["POST"])
def mkdir():
    data = flask.request.get_json()
    path = data.get("path")
    name = data.get("name")
    if not path or not name: return "missing",400
    if path == "":
        folder_path = os.path.join(UPLOAD_DIR, name)
    else:
        folder_path = os.path.join(UPLOAD_DIR, path, name)
    os.makedirs(folder_path, exist_ok=False)
    return "created",200

@app.route("/upload_to_folder", methods=["POST"])
def upload_to_folder():
    folder = flask.request.form.get("folder")
    if "to_upload" not in flask.request.files or not folder: return "missing",400
    file = flask.request.files["to_upload"]
    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)
    file.save(os.path.join(UPLOAD_DIR, folder, file.filename))
    return "uploaded",200

@app.route("/delete", methods=["POST"])
def delete():
    data = flask.request.get_json()
    path = data.get("path")
    full_path = os.path.join(UPLOAD_DIR, path)
    if not os.path.exists(full_path): return "not found",404
    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return "deleted",200
    except Exception as e:
        return str(e),500

@app.route("/files/<path:filename>")
def serve_file(filename):
    dirpath = os.path.dirname(os.path.join(UPLOAD_DIR, filename))
    fname = os.path.basename(filename)
    return flask.send_from_directory(dirpath, fname)

if __name__=="__main__":
    app.run("0.0.0.0",5000,debug=True)
