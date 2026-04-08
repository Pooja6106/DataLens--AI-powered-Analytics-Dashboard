from groq import Groq
import os
import json

class AIChat:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, message, history, kpis, filename="dataset"):
        system = f"""You are DataLens AI, a smart business data analyst assistant.
You are analyzing: {filename}

Key metrics:
- Total Revenue: ${kpis.get('total_revenue', 0):,.2f}
- Total Orders: {kpis.get('total_orders', 0):,}
- Total Customers: {kpis.get('total_customers', 0):,}
- Avg Order Value: ${kpis.get('avg_order_value', 0):,.2f}
- Top Categories: {json.dumps(kpis.get('category_breakdown', [])[:3])}
- Top Regions: {json.dumps(kpis.get('region_breakdown', [])[:3])}
- Top Products: {json.dumps(kpis.get('top_products', [])[:3])}

Answer concisely with specific numbers. Max 3 sentences.
End every reply with one suggestion starting with 'Try asking:'"""

        messages = [{"role": "system", "content": system}]
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = messages,
            max_tokens  = 500,
            temperature = 0.7,
        )

        return response.choices[0].message.content.strip()