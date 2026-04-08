import pandas as pd

DEPARTMENT_CONFIGS = {
    "sales": {
        "name":    "Sales & Revenue",
        "icon":    "💰",
        "color":   "#6366f1",
        "keywords": [
            "revenue","sales","amount","total","price","income",
            "gross","order","customer","product","discount",
            "invoice","region","category","quantity","profit","margin"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Revenue",   "color":"purple","icon":"💰"},
            {"id":"kpi2","label":"Total Orders",    "color":"green", "icon":"📦"},
            {"id":"kpi3","label":"Avg Order Value", "color":"amber", "icon":"🛒"},
            {"id":"kpi4","label":"Total Customers", "color":"blue",  "icon":"👥"},
        ],
        "charts":        ["area_trend","bar_category","donut_region",
                          "scatter","heatmap","top_products","data_table"],
        "story_context": "sales and revenue performance",
        "chat_persona":  "sales analyst who understands revenue, customers and products",
        "suggestions": [
            "What is our best selling product?",
            "Which region has highest revenue?",
            "What is the monthly revenue trend?"
        ]
    },
    "hr": {
        "name":    "Human Resources",
        "icon":    "👥",
        "color":   "#10b981",
        "keywords": [
            "employee","staff","salary","wage","attendance","leave",
            "department","designation","hire","joining","gender",
            "performance","rating","training","headcount","turnover",
            "absent","present","overtime","bonus","appraisal","emp_id"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Employees",  "color":"green", "icon":"👥"},
            {"id":"kpi2","label":"Avg Salary",        "color":"purple","icon":"💵"},
            {"id":"kpi3","label":"Attendance Rate",   "color":"blue",  "icon":"📋"},
            {"id":"kpi4","label":"Avg Performance",   "color":"amber", "icon":"⭐"},
        ],
        "charts":        ["bar_department","donut_gender","area_hiring",
                          "bar_salary","heatmap","data_table"],
        "story_context": "HR workforce and people analytics",
        "chat_persona":  "HR analytics specialist who understands workforce, salaries and performance",
        "suggestions": [
            "Which department has most employees?",
            "What is the average salary?",
            "What is the attendance rate?"
        ]
    },
    "production": {
        "name":    "Production & Manufacturing",
        "icon":    "🏭",
        "color":   "#f59e0b",
        "keywords": [
            "production","output","machine","shift","batch","line",
            "manufactured","units","assembly","plant","operator",
            "throughput","cycle_time","downtime","efficiency","oee",
            "work_order","job","run","process","station","cell"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Output",    "color":"amber", "icon":"🏭"},
            {"id":"kpi2","label":"Total Batches",   "color":"purple","icon":"📦"},
            {"id":"kpi3","label":"Avg Efficiency",  "color":"green", "icon":"⚡"},
            {"id":"kpi4","label":"Downtime Hours",  "color":"red",   "icon":"⏱"},
        ],
        "charts":        ["area_trend","bar_machine","donut_shift",
                          "scatter","heatmap","top_products","data_table"],
        "story_context": "production output and manufacturing efficiency",
        "chat_persona":  "manufacturing analyst who understands output, efficiency and machine performance",
        "suggestions": [
            "Which machine has highest output?",
            "What is the efficiency rate?",
            "Which shift performs best?"
        ]
    },
    "quality": {
        "name":    "Quality Control",
        "icon":    "✅",
        "color":   "#06b6d4",
        "keywords": [
            "defect","reject","scrap","inspection","quality","pass",
            "fail","rework","ncr","deviation","tolerance","spec",
            "sample","test","check","audit","complaint","return",
            "yield","acceptance","rejection","flaw","nonconformance"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Inspected", "color":"blue",  "icon":"🔍"},
            {"id":"kpi2","label":"Defect Rate %",   "color":"red",   "icon":"❌"},
            {"id":"kpi3","label":"Pass Rate %",     "color":"green", "icon":"✅"},
            {"id":"kpi4","label":"Total Rejected",  "color":"amber", "icon":"⚠️"},
        ],
        "charts":        ["area_trend","bar_defect_type","donut_pass_fail",
                          "scatter","heatmap","data_table"],
        "story_context": "quality control and defect analysis",
        "chat_persona":  "quality analyst who understands defects, inspection and rejection rates",
        "suggestions": [
            "What is the defect rate?",
            "Which product has most defects?",
            "What is the pass rate trend?"
        ]
    },
    "finance": {
        "name":    "Finance & Accounting",
        "icon":    "📊",
        "color":   "#8b5cf6",
        "keywords": [
            "budget","expense","cost","profit","loss","revenue",
            "income","expenditure","balance","asset","liability",
            "cash","flow","forecast","variance","actual","planned",
            "account","ledger","invoice","payment","tax","margin"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Revenue",   "color":"purple","icon":"💹"},
            {"id":"kpi2","label":"Total Expenses",  "color":"red",   "icon":"💸"},
            {"id":"kpi3","label":"Net Profit",      "color":"green", "icon":"📈"},
            {"id":"kpi4","label":"Budget Variance", "color":"amber", "icon":"🎯"},
        ],
        "charts":        ["area_trend","bar_category","donut_expense",
                          "scatter","heatmap","data_table"],
        "story_context": "financial performance and budget analysis",
        "chat_persona":  "financial analyst who understands budgets, expenses and profit margins",
        "suggestions": [
            "What is the net profit?",
            "Which expense category is highest?",
            "How is revenue trending?"
        ]
    },
    "inventory": {
        "name":    "Inventory & Supply Chain",
        "icon":    "📦",
        "color":   "#ec4899",
        "keywords": [
            "stock","inventory","warehouse","supplier","sku",
            "item","reorder","storage","bin","shelf","incoming",
            "outgoing","transfer","receipt","dispatch","lead_time",
            "safety_stock","demand","supply","order_qty","expiry",
            "batch_no","location","zone","rack"
        ],
        "kpis": [
            {"id":"kpi1","label":"Total Stock Value","color":"pink",  "icon":"📦"},
            {"id":"kpi2","label":"Total SKUs",        "color":"purple","icon":"🏷"},
            {"id":"kpi3","label":"Avg Item Value",    "color":"amber", "icon":"💰"},
            {"id":"kpi4","label":"Low Stock Items",   "color":"red",   "icon":"⚠️"},
        ],
        "charts":        ["area_trend","bar_category","donut_region",
                          "scatter","heatmap","top_products","data_table"],
        "story_context": "inventory levels and supply chain performance",
        "chat_persona":  "supply chain analyst who understands stock levels, suppliers and demand",
        "suggestions": [
            "Which items are low in stock?",
            "Who is our top supplier?",
            "What is the stock value trend?"
        ]
    },
}

class DepartmentEngine:
    def __init__(self, df):
        self.df = df

    def detect(self):
        cols_text = " ".join(self.df.columns.str.lower().tolist())
        scores    = {}

        for dept, config in DEPARTMENT_CONFIGS.items():
            score = sum(
                1 for kw in config["keywords"]
                if kw in cols_text
            )
            scores[dept] = score

        best  = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = round(
            scores[best] / total * 100, 1
        ) if total > 0 else 0

        return {
            "detected":   best,
            "confidence": confidence,
            "scores":     scores,
            "config":     DEPARTMENT_CONFIGS[best],
            "all_depts": {
                k: {"name": v["name"], "icon": v["icon"]}
                for k, v in DEPARTMENT_CONFIGS.items()
            }
        }

    def get_config(self, dept=None):
        if dept and dept in DEPARTMENT_CONFIGS:
            return DEPARTMENT_CONFIGS[dept]
        return self.detect()["config"]

    def get_suggestions(self, dept=None):
        config = self.get_config(dept)
        return config.get("suggestions", [
            "What are the top items?",
            "Show me the trend",
            "Any risks in the data?"
        ])