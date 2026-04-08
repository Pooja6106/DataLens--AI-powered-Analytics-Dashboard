from groq import Groq
import os
import json
import re

DEPT_PERSONAS = {
    "sales":      "sales analyst who understands revenue, customers and products",
    "hr":         "HR specialist who understands workforce, salaries and performance",
    "production": "manufacturing analyst who understands output, efficiency and machines",
    "quality":    "quality analyst who understands defects, inspection and rejection rates",
    "finance":    "financial analyst who understands budgets, expenses and profit",
    "inventory":  "supply chain analyst who understands stock levels and demand",
}

class AIChat:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, message, history, kpis, filename="dataset"):
        dept    = kpis.get("department", "sales")
        persona = DEPT_PERSONAS.get(dept, DEPT_PERSONAS["sales"])

        intent  = self._detect_intent(message)

        system  = f"""You are DataLens AI, a professional and formal {persona}.
You are analyzing: {filename} ({dept.upper()} department data)

Key metrics from the data:
- Primary Total:     {kpis.get('total_revenue',    0):,.2f}
- Total Records:     {kpis.get('total_rows',        0):,}
- Total Transactions:{kpis.get('total_orders',      0):,}
- Average Value:     {kpis.get('avg_order_value',   0):,.2f}
- Defect/Issue Rate: {kpis.get('defect_rate',       0):.2f}%
- Efficiency Score:  {kpis.get('avg_efficiency',    0):.2f}
- Net Profit/Value:  {kpis.get('net_profit',        0):,.2f}
- Top Categories:    {json.dumps(kpis.get('category_breakdown', [])[:4])}
- Top Regions:       {json.dumps(kpis.get('region_breakdown',   [])[:4])}
- Top Items:         {json.dumps(kpis.get('top_products',       [])[:5])}

Communication guidelines:
- Use formal, professional language at all times
- Always reference specific numbers from the data
- Structure responses clearly with key points
- Be concise — max 4 sentences unless detail is requested
- End every response with one actionable follow-up suggestion
  starting with 'Suggested next step:'
- For chart suggestions, recommend specific chart types
- For predictions, base them on visible trends in the data
- For insights, highlight anomalies and opportunities"""

        messages = [{"role": "system", "content": system}]

        if intent == "chart_suggestion":
            messages.append({
                "role": "system",
                "content": self._chart_suggestion_prompt(kpis)
            })
        elif intent == "prediction":
            messages.append({
                "role": "system",
                "content": self._prediction_prompt(kpis)
            })
        elif intent == "insight":
            messages.append({
                "role": "system",
                "content": self._insight_prompt(kpis)
            })

        for h in history[-6:]:
            messages.append({
                "role":    h["role"],
                "content": h["content"]
            })
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = messages,
            max_tokens  = 600,
            temperature = 0.4,
        )
        return response.choices[0].message.content.strip()

    def generate_auto_insights(self, kpis, filename="dataset"):
        dept    = kpis.get("department", "sales")
        persona = DEPT_PERSONAS.get(dept, DEPT_PERSONAS["sales"])

        prompt = f"""You are DataLens AI, a professional {persona}.
Analyze this {dept.upper()} dataset and generate 4 key auto-insights.

Dataset: {filename}
Primary Total:      {kpis.get('total_revenue',    0):,.2f}
Total Records:      {kpis.get('total_rows',        0):,}
Total Transactions: {kpis.get('total_orders',      0):,}
Average Value:      {kpis.get('avg_order_value',   0):,.2f}
Defect Rate:        {kpis.get('defect_rate',       0):.2f}%
Efficiency:         {kpis.get('avg_efficiency',    0):.2f}
Top Categories:     {json.dumps(kpis.get('category_breakdown', [])[:4])}
Top Regions:        {json.dumps(kpis.get('region_breakdown',   [])[:4])}
Top Items:          {json.dumps(kpis.get('top_products',       [])[:5])}

Generate exactly 4 insights in this JSON format (no markdown):
{{
  "insights": [
    {{
      "type":    "performance",
      "icon":    "📈",
      "title":   "Short insight title",
      "message": "One clear insight sentence with specific numbers",
      "action":  "One recommended action"
    }},
    {{
      "type":    "opportunity",
      "icon":    "💡",
      "title":   "Short insight title",
      "message": "One clear insight sentence with specific numbers",
      "action":  "One recommended action"
    }},
    {{
      "type":    "risk",
      "icon":    "⚠️",
      "title":   "Short insight title",
      "message": "One clear insight sentence with specific numbers",
      "action":  "One recommended action"
    }},
    {{
      "type":    "trend",
      "icon":    "🔍",
      "title":   "Short insight title",
      "message": "One clear insight sentence with specific numbers",
      "action":  "One recommended action"
    }}
  ]
}}"""

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 800,
            temperature = 0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def suggest_charts(self, kpis):
        dept = kpis.get("department", "sales")

        prompt = f"""You are a professional data visualization expert.
Based on this {dept.upper()} dataset, suggest the best charts.

Available data:
- Has date/time column:     {bool(kpis.get('monthly_trend'))}
- Has category column:      {bool(kpis.get('category_breakdown'))}
- Has region column:        {bool(kpis.get('region_breakdown'))}
- Has product/item column:  {bool(kpis.get('top_products'))}
- Has defect data:          {kpis.get('defect_rate', 0) > 0}
- Total records:            {kpis.get('total_rows', 0)}

Suggest exactly 4 charts in this JSON format (no markdown):
{{
  "suggestions": [
    {{
      "chart_type": "area",
      "title":      "Chart title",
      "reason":     "Why this chart fits the data",
      "priority":   1
    }}
  ]
}}"""

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 500,
            temperature = 0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def predict_trends(self, kpis):
        dept  = kpis.get("department", "sales")
        trend = kpis.get("monthly_trend", [])

        prompt = f"""You are a professional {dept} data analyst.
Predict future trends based on this historical data.

Department:     {dept.upper()}
Monthly Trend:  {json.dumps(trend[-6:])}
Total Value:    {kpis.get('total_revenue', 0):,.2f}
Avg Value:      {kpis.get('avg_order_value', 0):,.2f}
Total Records:  {kpis.get('total_rows', 0)}

Generate predictions in this JSON format (no markdown):
{{
  "predictions": [
    {{
      "metric":     "Metric name",
      "current":    "Current value",
      "predicted":  "Predicted value",
      "direction":  "up or down",
      "confidence": "High/Medium/Low",
      "reasoning":  "Brief reasoning based on data"
    }}
  ],
  "summary": "One overall trend summary sentence"
}}"""

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 600,
            temperature = 0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def _detect_intent(self, message):
        msg = message.lower()
        if any(k in msg for k in [
            "chart","graph","visual","plot","diagram",
            "show","display","recommend chart"
        ]):
            return "chart_suggestion"
        if any(k in msg for k in [
            "predict","forecast","future","next","trend",
            "estimate","projection","will","expect"
        ]):
            return "prediction"
        if any(k in msg for k in [
            "insight","analysis","analyze","opportunity",
            "risk","suggest","recommend","improve"
        ]):
            return "insight"
        return "general"

    def _chart_suggestion_prompt(self, kpis):
        return f"""The user is asking about chart recommendations.
Based on available data columns, suggest the most
appropriate chart types. Be specific about which
chart type (area, bar, doughnut, scatter, heatmap)
works best for each data dimension available."""

    def _prediction_prompt(self, kpis):
        trend = kpis.get("monthly_trend", [])
        return f"""The user wants trend predictions.
Historical trend data: {json.dumps(trend[-6:])}.
Provide data-driven predictions with confidence levels.
Base all predictions strictly on the visible trend patterns."""

    def _insight_prompt(self, kpis):
        return f"""The user wants business insights.
Focus on: anomalies, top performers, underperformers,
growth opportunities, and risk areas.
Always quantify insights with specific numbers from the data."""