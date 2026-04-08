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

    # ─────────────────────────────────────────
    # SAFE LABEL
    # ─────────────────────────────────────────
    def _safe_label(self, series):
        try:
            if pd.api.types.is_numeric_dtype(series):
                unique_count = series.nunique()
                if unique_count <= 50:
                    return series.fillna(0).astype(int).astype(str)
                return series.astype(str)
            return series.fillna("Unknown").astype(str)
        except:
            return series.astype(str)

    # ─────────────────────────────────────────
    # COMPUTE MAIN KPIs
    # ─────────────────────────────────────────
    def compute(self, date_from=None, date_to=None, dept=None):
        df = self.df.copy()

        if self.date_col and date_from:
            df = df[df[self.date_col] >= pd.to_datetime(date_from)]
        if self.date_col and date_to:
            df = df[df[self.date_col] <= pd.to_datetime(date_to)]

        detection   = self.dept.detect()
        active_dept = dept if dept and dept != "auto" \
                      else detection["detected"]
        config      = self.dept.get_config(active_dept)
        suggestions = self.dept.get_suggestions(active_dept)

        kpis = {}
        kpis["department"]  = active_dept
        kpis["dept_name"]   = config["name"]
        kpis["dept_icon"]   = config["icon"]
        kpis["dept_color"]  = config["color"]
        kpis["suggestions"] = suggestions
        kpis["detection"]   = {
            "detected":   detection["detected"],
            "confidence": detection["confidence"],
            "all_depts":  detection["all_depts"],
        }

        # ── Revenue / Main metric ──
        if self.revenue_col:
            rev = pd.to_numeric(
                df[self.revenue_col], errors="coerce")
            kpis["total_revenue"]   = round(float(rev.sum()),  2)
            kpis["avg_order_value"] = round(float(rev.mean()), 2)
            kpis["max_sale"]        = round(float(rev.max()),  2)
            kpis["min_sale"]        = round(float(rev.min()),  2)
        else:
            kpis["total_revenue"]   = 0
            kpis["avg_order_value"] = 0
            kpis["max_sale"]        = 0
            kpis["min_sale"]        = 0

        # ── Quantity / Output ──
        if self.qty_col and self.qty_col != self.revenue_col:
            qty = pd.to_numeric(
                df[self.qty_col], errors="coerce")
            kpis["total_output"] = round(float(qty.sum()),  2)
            kpis["avg_output"]   = round(float(qty.mean()), 2)
        else:
            kpis["total_output"] = kpis["total_revenue"]
            kpis["avg_output"]   = kpis["avg_order_value"]

        # ── Defects / Quality ──
        if self.defect_col:
            d   = pd.to_numeric(
                df[self.defect_col], errors="coerce")
            tot = pd.to_numeric(
                df[self.qty_col], errors="coerce"
            ).sum() if self.qty_col else len(df)
            kpis["total_defects"] = round(float(d.sum()), 2)
            kpis["defect_rate"]   = round(
                float(d.sum() / tot * 100), 2
            ) if tot > 0 else 0
            kpis["pass_rate"]     = round(
                100 - kpis["defect_rate"], 2)
        else:
            kpis["total_defects"] = 0
            kpis["defect_rate"]   = 0
            kpis["pass_rate"]     = 100

        # ── Efficiency ──
        if self.efficiency_col:
            eff = pd.to_numeric(
                df[self.efficiency_col], errors="coerce")
            kpis["avg_efficiency"] = round(float(eff.mean()), 2)
        else:
            kpis["avg_efficiency"] = 0

        # ── Expenses / Finance ──
        if self.expense_col:
            exp = pd.to_numeric(
                df[self.expense_col], errors="coerce")
            kpis["total_expenses"] = round(float(exp.sum()), 2)
            kpis["net_profit"]     = round(
                kpis["total_revenue"] - kpis["total_expenses"], 2)
        else:
            kpis["total_expenses"] = 0
            kpis["net_profit"]     = kpis["total_revenue"]

        # ── Counts ──
        kpis["total_rows"]      = len(df)
        kpis["total_orders"]    = len(
            df[self.order_col].dropna()
        ) if self.order_col else len(df)
        kpis["total_customers"] = df[self.customer_col].nunique() \
                                  if self.customer_col else 0

        # ── KPI Cards ──
        kpis["kpi_cards"] = self._build_kpi_cards(
            kpis, active_dept)

        # ── Time series ──
        if self.revenue_col and self.date_col:
            kpis["monthly_trend"]     = self._monthly_trend(df)
            kpis["daily_revenue"]     = self._daily_revenue(df)
            kpis["daily_orders"]      = self._daily_orders(df)
            kpis["week_vs_last_week"] = self._week_vs_last_week(df)
        else:
            kpis["monthly_trend"]     = []
            kpis["daily_revenue"]     = []
            kpis["daily_orders"]      = []
            kpis["week_vs_last_week"] = {}

        # ── Breakdowns ──
        kpis["peak_hours"]         = self._peak_hours(df)
        kpis["category_breakdown"] = self._category_breakdown(df)
        kpis["region_breakdown"]   = self._region_breakdown(df)
        kpis["top_products"]       = self._top_products(df)
        kpis["trending_today"]     = self._trending_products(df)

        # ── Detected columns info ──
        kpis["detected_columns"] = {
            "revenue":    self.revenue_col,
            "date":       self.date_col,
            "order":      self.order_col,
            "customer":   self.customer_col,
            "region":     self.region_col,
            "category":   self.category_col,
            "product":    self.product_col,
            "quantity":   self.qty_col,
            "defect":     self.defect_col,
            "efficiency": self.efficiency_col,
            "expense":    self.expense_col,
        }

        return kpis

    # ─────────────────────────────────────────
    # KPI CARDS BUILDER
    # ─────────────────────────────────────────
    def _build_kpi_cards(self, kpis, dept):
        def money(n):
            n = float(n or 0)
            if n >= 1_000_000_000:
                return f"${n/1_000_000_000:.2f}B"
            if n >= 1_000_000:
                return f"${n/1_000_000:.2f}M"
            if n >= 1_000:
                return f"${n/1_000:.1f}K"
            return f"${n:.2f}"

        cards = {
            "sales": [
                {
                    "label": "Total Revenue",
                    "value": money(kpis["total_revenue"]),
                    "color": "purple",
                    "trend": "▲ All time"
                },
                {
                    "label": "Total Orders",
                    "value": f"{int(kpis['total_orders']):,}",
                    "color": "green",
                    "trend": "Records"
                },
                {
                    "label": "Avg Order Value",
                    "value": money(kpis["avg_order_value"]),
                    "color": "amber",
                    "trend": "Per order"
                },
                {
                    "label": "Total Customers",
                    "value": f"{int(kpis['total_customers']):,}",
                    "color": "blue",
                    "trend": "Unique"
                },
            ],
            "hr": [
                {
                    "label": "Total Employees",
                    "value": f"{int(kpis['total_customers'] or kpis['total_rows']):,}",
                    "color": "green",
                    "trend": "Headcount"
                },
                {
                    "label": "Avg Salary",
                    "value": money(kpis["avg_order_value"]),
                    "color": "purple",
                    "trend": "Per employee"
                },
                {
                    "label": "Attendance Rate",
                    "value": f"{kpis['pass_rate']:.1f}%",
                    "color": "blue",
                    "trend": "Present"
                },
                {
                    "label": "Avg Performance",
                    "value": f"{kpis['avg_efficiency']:.1f}" \
                             if kpis["avg_efficiency"] > 0 else "N/A",
                    "color": "amber",
                    "trend": "Rating"
                },
            ],
            "production": [
                {
                    "label": "Total Output",
                    "value": f"{kpis['total_output']:,.0f} units",
                    "color": "amber",
                    "trend": "Units produced"
                },
                {
                    "label": "Total Batches",
                    "value": f"{int(kpis['total_orders']):,}",
                    "color": "purple",
                    "trend": "Batch runs"
                },
                {
                    "label": "Avg Efficiency",
                    "value": f"{kpis['avg_efficiency']:.1f}%" \
                             if kpis["avg_efficiency"] > 0 else "N/A",
                    "color": "green",
                    "trend": "OEE"
                },
                {
                    "label": "Defect Rate",
                    "value": f"{kpis['defect_rate']:.2f}%",
                    "color": "red",
                    "trend": "Rejection rate"
                },
            ],
            "quality": [
                {
                    "label": "Total Inspected",
                    "value": f"{int(kpis['total_rows']):,}",
                    "color": "blue",
                    "trend": "Units checked"
                },
                {
                    "label": "Defect Rate",
                    "value": f"{kpis['defect_rate']:.2f}%",
                    "color": "red",
                    "trend": "Rejection %"
                },
                {
                    "label": "Pass Rate",
                    "value": f"{kpis['pass_rate']:.1f}%",
                    "color": "green",
                    "trend": "Acceptance %"
                },
                {
                    "label": "Total Defects",
                    "value": f"{kpis['total_defects']:,.0f}",
                    "color": "amber",
                    "trend": "Rejected units"
                },
            ],
            "finance": [
                {
                    "label": "Total Revenue",
                    "value": money(kpis["total_revenue"]),
                    "color": "purple",
                    "trend": "Income"
                },
                {
                    "label": "Total Expenses",
                    "value": money(kpis["total_expenses"]),
                    "color": "red",
                    "trend": "Outflow"
                },
                {
                    "label": "Net Profit",
                    "value": money(kpis["net_profit"]),
                    "color": "green",
                    "trend": "Bottom line"
                },
                {
                    "label": "Avg Transaction",
                    "value": money(kpis["avg_order_value"]),
                    "color": "amber",
                    "trend": "Per entry"
                },
            ],
            "inventory": [
                {
                    "label": "Total Stock Value",
                    "value": money(kpis["total_revenue"]),
                    "color": "purple",
                    "trend": "Asset value"
                },
                {
                    "label": "Total SKUs",
                    "value": f"{int(kpis['total_customers'] or kpis['total_rows']):,}",
                    "color": "blue",
                    "trend": "Unique items"
                },
                {
                    "label": "Avg Item Value",
                    "value": money(kpis["avg_order_value"]),
                    "color": "amber",
                    "trend": "Per SKU"
                },
                {
                    "label": "Low Stock Alert",
                    "value": f"{int(kpis['total_defects']):,}",
                    "color": "red",
                    "trend": "Below reorder"
                },
            ],
        }
        return cards.get(dept, cards["sales"])

    # ─────────────────────────────────────────
    # TIME SERIES METHODS
    # ─────────────────────────────────────────
    def _monthly_trend(self, df):
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        d = d.dropna()
        d["month"] = pd.to_datetime(
            d[self.date_col]).dt.to_period("M")
        g = d.groupby("month")[
            self.revenue_col].sum().reset_index()
        g["month"] = g["month"].astype(str)
        return g.rename(
            columns={self.revenue_col: "revenue"}
        ).to_dict("records")

    def _daily_revenue(self, df):
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        d = d.dropna()
        d["day"] = pd.to_datetime(
            d[self.date_col]).dt.strftime("%Y-%m-%d")
        g = d.groupby("day")[
            self.revenue_col].sum().reset_index()
        g = g.sort_values("day").tail(30)
        return g.rename(
            columns={self.revenue_col: "revenue"}
        ).to_dict("records")

    def _daily_orders(self, df):
        if not self.date_col:
            return []
        d = df[[self.date_col]].copy().dropna()
        d["day"] = pd.to_datetime(
            d[self.date_col]).dt.strftime("%Y-%m-%d")
        g = d.groupby("day").size().reset_index(name="orders")
        return g.sort_values("day").tail(30).to_dict("records")

    def _week_vs_last_week(self, df):
        if not self.date_col or not self.revenue_col:
            return {}
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        d["_dt"] = pd.to_datetime(
            d[self.date_col], errors="coerce")
        d = d.dropna()
        if d.empty:
            return {}
        latest    = d["_dt"].max()
        this_week = d[
            d["_dt"] >= latest - timedelta(days=7)
        ][self.revenue_col].sum()
        last_week = d[
            (d["_dt"] >= latest - timedelta(days=14)) &
            (d["_dt"] <  latest - timedelta(days=7))
        ][self.revenue_col].sum()
        change = round(
            (this_week - last_week) / last_week * 100, 1
        ) if last_week > 0 else 0
        return {
            "this_week": round(float(this_week), 2),
            "last_week": round(float(last_week), 2),
            "change":    change,
            "direction": "up" if change >= 0 else "down"
        }

    def _peak_hours(self, df):
        if self.date_col:
            d = df[[self.date_col]].copy().dropna()
            d["hour"] = pd.to_datetime(
                d[self.date_col], errors="coerce").dt.hour
            d = d.dropna()
            if not d.empty and d["hour"].nunique() > 1:
                return d.groupby("hour").size().reset_index(
                    name="orders").to_dict("records")
        return [
            {"hour": h, "orders": v}
            for h, v in zip(
                range(8, 22),
                [12,18,25,30,45,40,35,38,42,50,48,35,28,20]
            )
        ]

    # ─────────────────────────────────────────
    # BREAKDOWN METHODS
    # ─────────────────────────────────────────
    def _category_breakdown(self, df):
        if not self.category_col or not self.revenue_col:
            return []
        d = df[[self.category_col, self.revenue_col]].copy()
        d[self.category_col] = self._safe_label(
            d[self.category_col])
        d[self.revenue_col]  = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        g = d.groupby(self.category_col)[
            self.revenue_col].sum().reset_index()
        g = g.sort_values(
            self.revenue_col, ascending=False).head(8)
        return g.rename(columns={
            self.category_col: "category",
            self.revenue_col:  "revenue"
        }).to_dict("records")

    def _region_breakdown(self, df):
        if not self.region_col or not self.revenue_col:
            return []
        d = df[[self.region_col, self.revenue_col]].copy()
        d[self.region_col]  = self._safe_label(
            d[self.region_col])
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        g = d.groupby(self.region_col)[
            self.revenue_col].sum().reset_index()
        g = g.sort_values(self.revenue_col, ascending=False)
        return g.rename(columns={
            self.region_col:  "region",
            self.revenue_col: "revenue"
        }).to_dict("records")

    def _top_products(self, df):
        if not self.product_col or not self.revenue_col:
            return []
        d = df[[self.product_col, self.revenue_col]].copy()
        d[self.product_col] = self._safe_label(
            d[self.product_col])
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        g = d.groupby(self.product_col)[
            self.revenue_col].sum().reset_index()
        g = g.sort_values(
            self.revenue_col, ascending=False).head(5)
        return g.rename(columns={
            self.product_col:  "product",
            self.revenue_col:  "revenue"
        }).to_dict("records")

    def _trending_products(self, df):
        if not self.product_col or not self.revenue_col:
            return []
        d = df[[self.product_col, self.revenue_col]].copy()
        d[self.product_col] = self._safe_label(
            d[self.product_col])
        d[self.revenue_col] = pd.to_numeric(
            d[self.revenue_col], errors="coerce")
        if self.date_col:
            d["_dt"] = pd.to_datetime(
                df[self.date_col], errors="coerce")
            latest = d["_dt"].max()
            d = d[d["_dt"] >= latest - timedelta(days=30)]
        g = d.groupby(self.product_col)[
            self.revenue_col].sum().reset_index()
        g = g.sort_values(
            self.revenue_col, ascending=False).head(5)
        return g.rename(columns={
            self.product_col:  "product",
            self.revenue_col:  "revenue"
        }).to_dict("records")

    # ─────────────────────────────────────────
    # PERIOD DATA
    # ─────────────────────────────────────────
    def compute_period(self, period="month",
                       date_from=None, date_to=None,
                       dept=None):
        df = self.df.copy()
        if self.date_col and date_from:
            df = df[
                df[self.date_col] >= pd.to_datetime(date_from)]
        if self.date_col and date_to:
            df = df[
                df[self.date_col] <= pd.to_datetime(date_to)]

        result = {}

        if self.revenue_col and self.date_col:
            d = df[[self.date_col, self.revenue_col]].copy()
            d[self.revenue_col] = pd.to_numeric(
                d[self.revenue_col], errors="coerce")
            d["_dt"] = pd.to_datetime(
                d[self.date_col], errors="coerce")
            d = d.dropna()

            fmt = {
                "day":   "%Y-%m-%d",
                "week":  "%Y-W%U",
                "month": "%Y-%m",
                "year":  "%Y"
            }
            d["period"] = d["_dt"].dt.strftime(
                fmt.get(period, "%Y-%m"))
            g = d.groupby("period")[
                self.revenue_col
            ].agg(["sum","mean","count"]).reset_index()
            g.columns = [
                "period","total_revenue",
                "avg_revenue","order_count"
            ]
            result["trend"] = g.sort_values(
                "period").round(2).to_dict("records")

        result["top_products"]       = self._top_products(df)
        result["region_breakdown"]   = self._region_breakdown(df)
        result["category_breakdown"] = self._category_breakdown(df)
        result["period"]             = period
        result["total_rows"]         = len(df)

        if self.date_col and self.revenue_col:
            d2 = df[[self.date_col, self.revenue_col]].copy()
            d2[self.revenue_col] = pd.to_numeric(
                d2[self.revenue_col], errors="coerce")
            d2["_dt"]  = pd.to_datetime(
                d2[self.date_col], errors="coerce")
            d2["hour"] = d2["_dt"].dt.hour
            d2["dow"]  = d2["_dt"].dt.day_name()
            d2 = d2.dropna(subset=["hour","dow"])
            if not d2.empty and d2["hour"].nunique() > 1:
                pivot = d2.pivot_table(
                    values     = self.revenue_col,
                    index      = "dow",
                    columns    = "hour",
                    aggfunc    = "sum",
                    fill_value = 0
                )
                days  = [
                    "Monday","Tuesday","Wednesday",
                    "Thursday","Friday","Saturday","Sunday"
                ]
                pivot = pivot.reindex(
                    [d for d in days if d in pivot.index])
                result["heatmap"] = {
                    "days":  list(pivot.index),
                    "hours": [str(c) for c in pivot.columns],
                    "data":  pivot.round(2).values.tolist()
                }

        if (self.revenue_col and self.qty_col and
                self.revenue_col != self.qty_col):
            sc = df[[self.revenue_col, self.qty_col]].copy()
            sc[self.revenue_col] = pd.to_numeric(
                sc[self.revenue_col], errors="coerce")
            sc[self.qty_col] = pd.to_numeric(
                sc[self.qty_col], errors="coerce")
            sc = sc.dropna().head(200)
            result["scatter"] = sc.rename(columns={
                self.revenue_col: "x",
                self.qty_col:     "y"
            }).round(2).to_dict("records")

        return result

    # ─────────────────────────────────────────
    # VIZ CONFIG
    # ─────────────────────────────────────────
    def detect_visualizations(self):
        detection = self.dept.detect()
        dept      = detection["detected"]
        config    = detection["config"]
        return {
            "recommended": [
                {
                    "id":          "area_trend",
                    "type":        "area",
                    "title":       f"{config['name']} trend",
                    "description": "Performance over time",
                    "priority":    1
                },
                {
                    "id":          "bar_category",
                    "type":        "bar",
                    "title":       "Breakdown by type",
                    "description": "Category comparison",
                    "priority":    2
                },
                {
                    "id":          "donut_region",
                    "type":        "donut",
                    "title":       "Distribution",
                    "description": "Share by location/type",
                    "priority":    3
                },
                {
                    "id":          "heatmap",
                    "type":        "heatmap",
                    "title":       "Activity heatmap",
                    "description": "Time pattern analysis",
                    "priority":    4
                },
                {
                    "id":          "scatter",
                    "type":        "scatter",
                    "title":       "Correlation analysis",
                    "description": "Variable relationship",
                    "priority":    5
                },
            ],
            "available": [
                {"id":"area",      "type":"area",
                 "title":"Area chart",     "icon":"📈"},
                {"id":"bar",       "type":"bar",
                 "title":"Bar chart",      "icon":"📊"},
                {"id":"donut",     "type":"donut",
                 "title":"Doughnut chart", "icon":"🍩"},
                {"id":"heatmap",   "type":"heatmap",
                 "title":"Heatmap",        "icon":"🔥"},
                {"id":"scatter",   "type":"scatter",
                 "title":"Scatter plot",   "icon":"✦"},
                {"id":"sparkline", "type":"sparkline",
                 "title":"KPI sparklines", "icon":"⚡"},
                {"id":"table",     "type":"table",
                 "title":"Data table",     "icon":"📋"},
            ],
            "department":  dept,
            "dept_config": config,
            "all_depts":   detection["all_depts"],
        }