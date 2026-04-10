import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from app.services.department_engine import (
    DepartmentEngine, DEPARTMENT_CONFIGS
)

class KPIEngine:
    def __init__(self, filepath):
        self.df   = pd.read_csv(filepath)
        self.dept = DepartmentEngine(self.df)
        self._detect_columns()

    @staticmethod
    def from_excel_dept(filepath, dept_name):
        """
        Creates KPIEngine from a specific department
        in a multi-department Excel file
        """
        from app.services.excel_parser import ExcelParser
        parser   = ExcelParser(filepath)
        _, depts = parser.parse()

        dept_key = dept_name.upper()
        if dept_key not in depts:
            available = list(depts.keys())
            dept_key  = available[0] if available else None

        if dept_key and dept_key in depts:
            df = depts[dept_key]
            import tempfile, os
            tmp = tempfile.NamedTemporaryFile(
                suffix=".csv", delete=False)
            df.to_csv(tmp.name, index=False)
            tmp.close()
            engine = KPIEngine(tmp.name)
            os.unlink(tmp.name)
            return engine
        return None

    # ─────────────────────────────────────────
    # DETECT COLUMNS
    # ─────────────────────────────────────────
    def _detect_columns(self):
        cols = list(self.df.columns)

        def find(keywords):
            return next((
                c for c in cols
                if any(k in c.lower() for k in keywords)
            ), None)

        self.date_col = find([
            "date","time","month","year","period","timestamp",
            "datetime","day","created","recorded","joining",
            "hire_date","production_date","shift_date","log_date"
        ])
        self.revenue_col = find([
            "revenue","sales","amount","total","price","income",
            "gross","cost","value","production_cost","salary",
            "wage","budget","expense","spend","profit",
            "stock_value","output_value","billing","earning",
            "na_sales","eu_sales","global_sales","amount_of",
            "approved","exemption","claims","tax"
        ])
        self.qty_col = find([
            "quantity","qty","units","count","volume","output",
            "produced","manufactured","pieces","parts","items",
            "throughput","yield","total_units","completed",
            "headcount","stock","inventory","attendance","inspected"
        ])
        self.order_col = find([
            "order","transaction","invoice","batch","job",
            "batch_id","job_id","work_order","serial","lot",
            "ticket","ref","employee_id","emp_id","sku",
            "item_code","po_number","order_id","taxpayer",
            "claim_id","record_id"
        ])
        self.customer_col = find([
            "customer","client","user","buyer","operator",
            "worker","employee","staff","technician","supplier",
            "vendor","machine","equipment","asset","inspector",
            "taxpayer_name","company","organization","entity"
        ])
        self.category_col = find([
            "category","type","segment","department","group",
            "genre","shift","process","operation","stage",
            "designation","role","gender","grade","level",
            "defect_type","fault_type","expense_type","item_type",
            "industry","sector","class","classification","nature"
        ])
        self.region_col = find([
            "region","country","city","location","area","state",
            "plant","factory","facility","site","floor","zone",
            "line","station","machine","warehouse","bin","rack",
            "branch","division","territory","cluster","platform",
            "district","province","municipality","town","zone_code"
        ])
        self.product_col = find([
            "product","item","name","sku","description","title",
            "part","component","material","model","variant","code",
            "part_name","item_name","product_name","material_name",
            "employee_name","machine_name","supplier_name","game",
            "town_code","region_code","project","scheme","program"
        ])
        self.defect_col = find([
            "defect","reject","scrap","waste","error","fault",
            "failure","rework","return","ncr","complaint",
            "absent","leave","downtime","idle","loss","shortage"
        ])
        self.efficiency_col = find([
            "efficiency","performance","utilization","oee",
            "productivity","rate","yield_pct","quality_rate",
            "attendance_rate","rating","score","availability"
        ])
        self.expense_col = find([
            "expense","cost","expenditure","spending","outflow",
            "debit","payment","budget_used","actual_cost"
        ])

        if not self.revenue_col and self.qty_col:
            self.revenue_col = self.qty_col

        if self.date_col:
            sample = self.df[self.date_col].dropna()
            if len(sample) > 0:
                try:
                    nv = float(str(sample.iloc[0]))
                    if 1900 < nv < 2100:
                        self.df["_date_parsed"] = pd.to_datetime(
                            self.df[self.date_col].astype(str).str[:4] + "-01-01",
                            errors="coerce"
                        )
                    else:
                        self.df["_date_parsed"] = pd.to_datetime(
                            self.df[self.date_col], errors="coerce"
                        )
                except:
                    self.df["_date_parsed"] = pd.to_datetime(
                        self.df[self.date_col], errors="coerce"
                    )
                self.date_col = "_date_parsed"