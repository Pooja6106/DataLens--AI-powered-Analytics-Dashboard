import os
import json
from flask              import Blueprint, render_template, jsonify, session, request
from app.models.dataset import Dataset
from app.services.kpi_engine   import KPIEngine
from app.services.story_engine import StoryEngine
from app.services.ai_chat      import AIChat

dashboard_bp = Blueprint("dashboard", __name__)

def get_dataset():
    dataset_id = session.get("dataset_id")
    if not dataset_id:
        return None, None
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return None, None
    filepath = os.path.join("uploads", dataset.filename)
    if not os.path.exists(filepath):
        return None, None
    return dataset, filepath

@dashboard_bp.route("/dashboard")
def dashboard():
    dataset, filepath = get_dataset()
    if not dataset:
        from flask import redirect, url_for
        return redirect(url_for("upload.upload_page"))
    return render_template("dashboard.html", dataset=dataset)

@dashboard_bp.route("/api/kpis")
def api_kpis():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset found. Please upload a file."}), 404
    try:
        date_from = request.args.get("date_from")
        date_to   = request.args.get("date_to")
        engine    = KPIEngine(filepath)
        kpis      = engine.compute(date_from=date_from, date_to=date_to)
        safe      = json.loads(json.dumps(kpis, default=str))

        session["kpis_summary"] = {
            "total_revenue":      safe.get("total_revenue", 0),
            "total_orders":       safe.get("total_orders", 0),
            "total_customers":    safe.get("total_customers", 0),
            "avg_order_value":    safe.get("avg_order_value", 0),
            "total_rows":         safe.get("total_rows", 0),
            "category_breakdown": safe.get("category_breakdown", [])[:4],
            "region_breakdown":   safe.get("region_breakdown", [])[:4],
            "top_products":       safe.get("top_products", [])[:3],
            "week_vs_last_week":  safe.get("week_vs_last_week", {}),
        }
        return jsonify(safe)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@dashboard_bp.route("/api/period-data")
def api_period_data():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset found"}), 404
    try:
        period    = request.args.get("period", "month")
        date_from = request.args.get("date_from")
        date_to   = request.args.get("date_to")
        engine    = KPIEngine(filepath)
        data      = engine.compute_period(period, date_from, date_to)
        safe      = json.loads(json.dumps(data, default=str))
        return jsonify(safe)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/viz-config")
def api_viz_config():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset found"}), 404
    try:
        engine = KPIEngine(filepath)
        config = engine.detect_visualizations()
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/story")
def api_story():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset loaded"}), 404
    try:
        kpis   = session.get("kpis") or KPIEngine(filepath).compute()
        engine = StoryEngine()
        story  = engine.generate(kpis, dataset.original)
        return jsonify(story)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/chat", methods=["POST"])
def api_chat():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset loaded"}), 404
    try:
        data    = request.get_json()
        message = data.get("message", "")
        history = data.get("history", [])
        kpis    = session.get("kpis") or KPIEngine(filepath).compute()
        chat    = AIChat()
        reply   = chat.chat(message, history, kpis, dataset.original)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@dashboard_bp.route("/api/auto-insights")
def api_auto_insights():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset loaded"}), 404
    try:
        kpis    = session.get("kpis_summary")
        if not kpis:
            kpis = KPIEngine(filepath).compute()
        chat    = AIChat()
        insights = chat.generate_auto_insights(
            kpis, dataset.original)
        return jsonify(insights)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/chart-suggestions")
def api_chart_suggestions():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset loaded"}), 404
    try:
        kpis        = session.get("kpis_summary")
        if not kpis:
            kpis = KPIEngine(filepath).compute()
        chat        = AIChat()
        suggestions = chat.suggest_charts(kpis)
        return jsonify(suggestions)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/predictions")
def api_predictions():
    dataset, filepath = get_dataset()
    if not dataset:
        return jsonify({"error": "No dataset loaded"}), 404
    try:
        kpis        = session.get("kpis_summary")
        if not kpis:
            kpis = KPIEngine(filepath).compute()
        chat        = AIChat()
        predictions = chat.predict_trends(kpis)
        return jsonify(predictions)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500