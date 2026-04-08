from groq import Groq
import os
import json

DEPT_CONTEXTS = {
    "sales":      "sales and revenue performance, customer behavior and product trends",
    "hr":         "HR workforce analytics, employee performance, attendance and salary insights",
    "production": "manufacturing output, machine efficiency, defect rates and production trends",
    "quality":    "quality control metrics, defect analysis, pass/fail rates and inspection data",
    "finance":    "financial performance, budget variance, expense categories and profit trends",
    "inventory":  "inventory levels, stock movement, supplier performance and supply chain gaps",
}

class StoryEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, kpis, filename="your dataset", dept=None):
        active_dept = dept or kpis.get("department","sales")
        context     = DEPT_CONTEXTS.get(
            active_dept, DEPT_CONTEXTS["sales"])
        products    = kpis.get("top_products",      [])
        cats        = kpis.get("category_breakdown", [])
        regions     = kpis.get("region_breakdown",   [])

        prompt = f"""You are a senior business analyst
specializing in {context}.

Analyze this {active_dept.upper()} department data
and write professional business insights.

Dataset: {filename}
Department: {active_dept.upper()}
Primary Metric Total: {kpis.get('total_revenue',0):,.2f}
Total Records: {kpis.get('total_rows',0):,}
Total Transactions/Batches: {kpis.get('total_orders',0):,}
Average Value: {kpis.get('avg_order_value',0):,.2f}
Defect/Issue Rate: {kpis.get('defect_rate',0):.2f}%
Efficiency Score: {kpis.get('avg_efficiency',0):.2f}
Net Profit/Value: {kpis.get('net_profit',0):,.2f}
Top Categories: {json.dumps(cats[:4])}
Top Regions/Locations: {json.dumps(regions[:4])}
Top Items/Products: {json.dumps(products[:3])}

Respond with ONLY this JSON, no markdown, no extra text:
{{
  "headline": "One powerful sentence summarizing {active_dept} performance",
  "summary": "2-3 sentences on overall performance, key driver, trend",
  "highlights": [
    "Specific positive insight with exact numbers",
    "Another key finding with numbers",
    "Third growth or efficiency insight"
  ],
  "risks": [
    "One risk or underperforming area with numbers",
    "Second concern or bottleneck"
  ],
  "recommendation": "One clear actionable recommendation for management"
}}"""

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role":"user","content":prompt}],
            max_tokens  = 1000,
            temperature = 0.7,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)