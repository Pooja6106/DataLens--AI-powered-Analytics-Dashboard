from groq import Groq
import os
import json

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
        dept    = kpis.get("department","sales")
        persona = DEPT_PERSONAS.get(dept, DEPT_PERSONAS["sales"])

        system = f"""You are DataLens AI, a smart {persona}.
You are analyzing: {filename} ({dept.upper()} data)

Key metrics:
- Primary Total: {kpis.get('total_revenue',0):,.2f}
- Total Records: {kpis.get('total_rows',0):,}
- Total Transactions: {kpis.get('total_orders',0):,}
- Average Value: {kpis.get('avg_order_value',0):,.2f}
- Defect/Issue Rate: {kpis.get('defect_rate',0):.2f}%
- Efficiency: {kpis.get('avg_efficiency',0):.2f}
- Top Categories: {json.dumps(kpis.get('category_breakdown',[])[:3])}
- Top Regions: {json.dumps(kpis.get('region_breakdown',[])[:3])}
- Top Items: {json.dumps(kpis.get('top_products',[])[:3])}

Rules:
- Answer concisely with specific numbers
- Max 3 sentences unless asked for detail
- Always relate answer to {dept} context
- End every reply with one suggestion
  starting with 'Try asking:'"""

        messages = [{"role":"system","content":system}]
        for h in history[-6:]:
            messages.append({
                "role":    h["role"],
                "content": h["content"]
            })
        messages.append({"role":"user","content":message})

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = messages,
            max_tokens  = 500,
            temperature = 0.7,
        )
        return response.choices[0].message.content.strip()