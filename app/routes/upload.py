import os
import json
import uuid
from flask import (
    Blueprint, render_template, request,
    jsonify, session, current_app
)
from werkzeug.utils        import secure_filename
from app.models.db         import db
from app.models.dataset    import Dataset
from app.services.data_cleaner import DataCleaner
from app.utils.validators  import allowed_file

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/")
def index():
    return render_template("upload.html")

@upload_bp.route("/upload")
def upload_page():
    return render_template("upload.html")

@upload_bp.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({
            "error": "File type not allowed. Use CSV, XLSX or JSON"
        }), 400

    try:
        original_name = secure_filename(file.filename)
        unique_name   = f"{uuid.uuid4().hex}_{original_name}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        filepath      = os.path.join(upload_folder, unique_name)
        file.save(filepath)

        cleaner    = DataCleaner()
        df, report = cleaner.clean(filepath)

        # Save cleaned version as CSV
        clean_name = f"clean_{uuid.uuid4().hex}.csv"
        clean_path = os.path.join(upload_folder, clean_name)
        df.to_csv(clean_path, index=False)

        dataset = Dataset(
            filename     = clean_name,
            original     = original_name,
            row_count    = report["final_rows"],
            col_count    = report["final_cols"],
            columns      = json.dumps(list(df.columns)),
            clean_report = json.dumps(report),
        )
        db.session.add(dataset)
        db.session.commit()

        session["dataset_id"]   = dataset.id
        session["dataset_file"] = clean_path
        session["columns"]      = list(df.columns)

        # Add department info to report
        extra = {}
        if report.get("is_multi_dept"):
            extra["is_multi_dept"] = True
            extra["departments"]   = report.get("departments",[])

        return jsonify({
            "success":    True,
            "dataset_id": dataset.id,
            "report":     {**report, **extra},
            "columns":    list(df.columns),
            "redirect":   "/dashboard"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500