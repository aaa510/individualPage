from pathlib import Path
from flask import Flask, Response, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
PROFILE_MD_PATH = BASE_DIR / "source" / "overall" / "overall_merged.md"

app = Flask(__name__, static_folder=None)


@app.get("/")
def root():
    return send_from_directory(str(BASE_DIR), "index.html")


@app.get("/report")
def report_page():
    return send_from_directory(str(BASE_DIR), "report.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    file_path = BASE_DIR / filename
    if file_path.suffix.lower() == ".svg":
        return Response(file_path.read_text(encoding="utf-8"), mimetype="image/svg+xml")
    return send_from_directory(str(BASE_DIR), filename)


@app.post("/api/job-report")
def create_job_report():
    try:
        payload = request.get_json(silent=True) or {}
        position = (payload.get("position") or "").strip()
        company = (payload.get("company") or "").strip()

        if not position or not company:
            return jsonify({"error": "position 和 company 不能为空"}), 400
        if not PROFILE_MD_PATH.exists():
            return jsonify({"error": f"资料文件不存在: {PROFILE_MD_PATH}"}), 500

        from util.glmModel import generate_job_match_report_package

        profile_markdown = PROFILE_MD_PATH.read_text(encoding="utf-8")
        report_package = generate_job_match_report_package(position, company, profile_markdown)
        return jsonify(
            {
                "position": position,
                "company": company,
                **report_package,
            }
        )
    except Exception as exc:
        app.logger.exception("Failed to generate job report")
        return jsonify({"error": f"报告生成失败: {str(exc)}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
