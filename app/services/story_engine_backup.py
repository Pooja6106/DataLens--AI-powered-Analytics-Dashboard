from groq import Groq
import os
import json

class StoryEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, kpis, filename="your dataset"):
        categories = kpis.get("category_breakdown", [])
        regions    = kpis.get("region_breakdown", [])
        products   = kpis.get("top_products", [])

        prompt = f"""You are a senior business analyst. Analyze this data and write business insights.

Dataset: {filename}
Total Revenue: ${kpis.get('total_revenue', 0):,.2f}
Total Orders: {kpis.get('total_orders', 0):,}
Total Customers: {kpis.get('total_customers', 0):,}
Avg Order Value: ${kpis.get('avg_order_value', 0):,.2f}
Top Categories: {json.dumps(categories[:4])}
Top Regions: {json.dumps(regions[:4])}
Top Products: {json.dumps(products[:3])}

Respond with ONLY this JSON, no markdown, no extra text:
{{
  "headline": "One powerful sentence summarizing performance",
  "summary": "2-3 sentences on overall performance and key driver",
  "highlights": [
    "Specific positive insight with numbers",
    "Another key finding with numbers",
    "Third growth insight"
  ],
  "risks": [
    "One risk or underperforming area",
    "Second risk area"
  ],
  "recommendation": "One clear actionable recommendation"
}}"""

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 1000,
            temperature = 0.7,
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)