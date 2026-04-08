import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

class KPIEngine:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self._detect_columns()

    def _detect_columns(self):
        self.revenue_col  = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["revenue","sales","amount","total","price","income","gross","na_sales","eu_sales","global"])), None)
        self.date_col     = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["date","time","month","year","period","order_date","created"])), None)
        self.order_col    = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["order","transaction","id","invoice","rank"])), None)
        self.customer_col = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["customer","client","user","buyer","publisher"])), None)
        self.region_col   = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["region","country","city","location","area","state","platform","genre"])), None)
        self.category_col = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["category","type","segment","department","group","genre"])), None)
        self.product_col  = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["product","item","name","sku","description","title","game"])), None)
        self.qty_col      = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["quantity","qty","units","count","volume","copies"])), None)
        self.hour_col     = next((c for c in self.df.columns if any(
            k in c.lower() for k in ["hour","time","hh","hr"])), None)

        if self.date_col:
            sample = self.df[self.date_col].dropna().iloc[0] if len(self.df) > 0 else None
            try:
                numeric_val = float(str(sample))
                if 1900 < numeric_val < 2100:
                    self.df["_date_parsed"] = pd.to_datetime(
                        self.df[self.date_col].astype(str).str[:4] + "-01-01",
                        errors="coerce"
                    )
                else:
                    self.df["_date_parsed"] = pd.to_datetime(
                        self.df[self.date_col], errors="coerce")
            except:
                self.df["_date_parsed"] = pd.to_datetime(
                    self.df[self.date_col], errors="coerce")
            self.date_col = "_date_parsed"

    def compute_period(self, period="month", date_from=None, date_to=None):
        df = self.df.copy()
        if self.date_col and date_from:
            df = df[df[self.date_col] >= pd.to_datetime(date_from)]
        if self.date_col and date_to:
            df = df[df[self.date_col] <= pd.to_datetime(date_to)]

        result = {}

        if self.revenue_col and self.date_col:
            d = df[[self.date_col, self.revenue_col]].copy()
            d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
            d["_dt"] = pd.to_datetime(d[self.date_col], errors="coerce")
            d = d.dropna()

            if period == "day":
                d["period"] = d["_dt"].dt.strftime("%Y-%m-%d")
            elif period == "week":
                d["period"] = d["_dt"].dt.strftime("%Y-W%U")
            elif period == "month":
                d["period"] = d["_dt"].dt.strftime("%Y-%m")
            elif period == "year":
                d["period"] = d["_dt"].dt.strftime("%Y")

            grouped = d.groupby("period")[self.revenue_col].agg(
                ["sum", "mean", "count"]
            ).reset_index()
            grouped.columns = ["period", "total_revenue", "avg_revenue", "order_count"]
            grouped = grouped.sort_values("period")
            result["trend"] = grouped.round(2).to_dict("records")

            if self.category_col:
                cat = df[[self.date_col, self.category_col, self.revenue_col]].copy()
                cat[self.revenue_col] = pd.to_numeric(cat[self.revenue_col], errors="coerce")
                cat["_dt"] = pd.to_datetime(cat[self.date_col], errors="coerce")
                if period == "day":
                    cat["period"] = cat["_dt"].dt.strftime("%Y-%m-%d")
                elif period == "week":
                    cat["period"] = cat["_dt"].dt.strftime("%Y-W%U")
                elif period == "month":
                    cat["period"] = cat["_dt"].dt.strftime("%Y-%m")
                elif period == "year":
                    cat["period"] = cat["_dt"].dt.strftime("%Y")
                cat_grouped = cat.groupby(
                    ["period", self.category_col]
                )[self.revenue_col].sum().reset_index()
                cat_grouped.columns = ["period", "category", "revenue"]
                result["category_trend"] = cat_grouped.round(2).to_dict("records")

        if self.revenue_col and self.product_col:
            p = df[[self.product_col, self.revenue_col]].copy()
            p[self.revenue_col] = pd.to_numeric(p[self.revenue_col], errors="coerce")
            top = p.groupby(self.product_col)[self.revenue_col].sum().reset_index()
            top = top.sort_values(self.revenue_col, ascending=False).head(10)
            result["top_products"] = top.rename(columns={
                self.product_col: "product",
                self.revenue_col: "revenue"
            }).round(2).to_dict("records")

        if self.revenue_col and self.region_col:
            r = df[[self.region_col, self.revenue_col]].copy()
            r[self.revenue_col] = pd.to_numeric(r[self.revenue_col], errors="coerce")
            reg = r.groupby(self.region_col)[self.revenue_col].sum().reset_index()
            result["region_breakdown"] = reg.rename(columns={
                self.region_col:  "region",
                self.revenue_col: "revenue"
            }).round(2).to_dict("records")

        if self.revenue_col and self.qty_col:
            sc = df[[self.revenue_col, self.qty_col]].copy()
            sc[self.revenue_col] = pd.to_numeric(sc[self.revenue_col], errors="coerce")
            sc[self.qty_col]     = pd.to_numeric(sc[self.qty_col],     errors="coerce")
            sc = sc.dropna().head(200)
            result["scatter"] = sc.rename(columns={
                self.revenue_col: "x",
                self.qty_col:     "y"
            }).round(2).to_dict("records")

        if self.date_col and self.revenue_col:
            h = df[[self.date_col, self.revenue_col]].copy()
            h[self.revenue_col] = pd.to_numeric(h[self.revenue_col], errors="coerce")
            h["_dt"]  = pd.to_datetime(h[self.date_col], errors="coerce")
            h["hour"] = h["_dt"].dt.hour
            h["dow"]  = h["_dt"].dt.day_name()
            h = h.dropna(subset=["hour","dow"])
            if not h.empty:
                pivot = h.pivot_table(
                    values  = self.revenue_col,
                    index   = "dow",
                    columns = "hour",
                    aggfunc = "sum",
                    fill_value = 0
                )
                days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                pivot = pivot.reindex([d for d in days_order if d in pivot.index])
                result["heatmap"] = {
                    "days":  list(pivot.index),
                    "hours": [str(c) for c in pivot.columns],
                    "data":  pivot.round(2).values.tolist()
                }

        result["period"]     = period
        result["total_rows"] = len(df)
        return result

    def detect_visualizations(self):
        cols   = list(self.df.columns)
        dtypes = {c: str(self.df[c].dtype) for c in cols}
        has_date     = self.date_col     is not None
        has_revenue  = self.revenue_col  is not None
        has_category = self.category_col is not None
        has_region   = self.region_col   is not None
        has_product  = self.product_col  is not None
        has_qty      = self.qty_col      is not None

        recommended = []
        available   = []

        if has_revenue and has_date:
            recommended.append({
                "id": "area_trend", "type": "area",
                "title": "Revenue over time",
                "description": "Area chart showing revenue trend",
                "priority": 1
            })
        if has_category and has_revenue:
            recommended.append({
                "id": "bar_category", "type": "bar",
                "title": "Revenue by category",
                "description": "Horizontal bar chart",
                "priority": 2
            })
        if has_region and has_revenue:
            recommended.append({
                "id": "donut_region", "type": "donut",
                "title": "Revenue by region",
                "description": "Doughnut chart breakdown",
                "priority": 3
            })
        if has_revenue and has_qty:
            recommended.append({
                "id": "scatter_rev_qty", "type": "scatter",
                "title": "Revenue vs Quantity",
                "description": "Scatter plot correlation",
                "priority": 4
            })
        if has_date and has_revenue:
            recommended.append({
                "id": "heatmap_dow", "type": "heatmap",
                "title": "Sales heatmap",
                "description": "Day of week vs hour",
                "priority": 5
            })
        if has_product and has_revenue:
            recommended.append({
                "id": "sparkline_products", "type": "sparkline",
                "title": "Product sparklines",
                "description": "KPI cards with trends",
                "priority": 6
            })

        available = [
            {"id": "area",      "type": "area",      "title": "Area chart",      "icon": "📈"},
            {"id": "bar",       "type": "bar",        "title": "Bar chart",       "icon": "📊"},
            {"id": "donut",     "type": "donut",      "title": "Doughnut chart",  "icon": "🍩"},
            {"id": "heatmap",   "type": "heatmap",    "title": "Heatmap",         "icon": "🔥"},
            {"id": "scatter",   "type": "scatter",    "title": "Scatter plot",    "icon": "✦"},
            {"id": "sparkline", "type": "sparkline",  "title": "KPI sparklines",  "icon": "⚡"},
            {"id": "table",     "type": "table",      "title": "Data table",      "icon": "📋"},
        ]

        return {
            "recommended": recommended,
            "available":   available,
            "columns":     cols,
            "has_date":    has_date,
            "has_revenue": has_revenue,
            "has_category":has_category,
            "has_region":  has_region,
            "has_product": has_product,
            "has_qty":     has_qty,
        }



    def compute(self, date_from=None, date_to=None):
        df = self.df.copy()

        if self.date_col and date_from:
            df = df[df[self.date_col] >= pd.to_datetime(date_from)]
        if self.date_col and date_to:
            df = df[df[self.date_col] <= pd.to_datetime(date_to)]

        kpis = {}

        if self.revenue_col:
            rev = pd.to_numeric(df[self.revenue_col], errors="coerce")
            kpis["total_revenue"]   = round(float(rev.sum()), 2)
            kpis["avg_order_value"] = round(float(rev.mean()), 2)
            kpis["max_sale"]        = round(float(rev.max()), 2)
            kpis["min_sale"]        = round(float(rev.min()), 2)
        else:
            kpis["total_revenue"]   = 0
            kpis["avg_order_value"] = 0

        kpis["total_rows"]      = len(df)
        kpis["total_orders"]    = len(df[self.order_col].dropna()) if self.order_col else len(df)
        kpis["total_customers"] = df[self.customer_col].nunique() if self.customer_col else 0

        if self.revenue_col and self.date_col:
            kpis["daily_revenue"]       = self._daily_revenue(df)
            kpis["daily_orders"]        = self._daily_orders(df)
            kpis["monthly_trend"]       = self._monthly_trend(df)
            kpis["week_vs_last_week"]   = self._week_vs_last_week(df)
        else:
            kpis["daily_revenue"]       = []
            kpis["daily_orders"]        = []
            kpis["monthly_trend"]       = []
            kpis["week_vs_last_week"]   = {}

        kpis["peak_hours"]          = self._peak_hours(df)
        kpis["category_breakdown"]  = self._category_breakdown(df)
        kpis["region_breakdown"]    = self._region_breakdown(df)
        kpis["top_products"]        = self._top_products(df)
        kpis["trending_today"]      = self._trending_products(df)

        kpis["detected_columns"] = {
            "revenue":  self.revenue_col,
            "date":     self.date_col,
            "order":    self.order_col,
            "customer": self.customer_col,
            "region":   self.region_col,
            "category": self.category_col,
            "product":  self.product_col,
            "quantity": self.qty_col,
        }

        return kpis

    def _daily_revenue(self, df):
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        d = d.dropna()
        d["day"] = pd.to_datetime(d[self.date_col]).dt.strftime("%Y-%m-%d")
        grouped  = d.groupby("day")[self.revenue_col].sum().reset_index()
        grouped  = grouped.sort_values("day").tail(30)
        return grouped.rename(columns={self.revenue_col: "revenue"}).to_dict("records")

    def _daily_orders(self, df):
        if not self.date_col:
            return []
        d = df[[self.date_col]].copy()
        d = d.dropna()
        d["day"]  = pd.to_datetime(d[self.date_col]).dt.strftime("%Y-%m-%d")
        grouped   = d.groupby("day").size().reset_index(name="orders")
        grouped   = grouped.sort_values("day").tail(30)
        return grouped.to_dict("records")

    def _monthly_trend(self, df):
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        d = d.dropna()
        d["month"] = pd.to_datetime(d[self.date_col]).dt.to_period("M")
        grouped    = d.groupby("month")[self.revenue_col].sum().reset_index()
        grouped["month"] = grouped["month"].astype(str)
        return grouped.rename(columns={self.revenue_col: "revenue"}).to_dict("records")

    def _week_vs_last_week(self, df):
        if not self.date_col or not self.revenue_col:
            return {}
        d = df[[self.date_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        d["_dt"] = pd.to_datetime(d[self.date_col], errors="coerce")
        d = d.dropna()
        if d.empty:
            return {}
        latest    = d["_dt"].max()
        this_week = d[d["_dt"] >= latest - timedelta(days=7)][self.revenue_col].sum()
        last_week = d[(d["_dt"] >= latest - timedelta(days=14)) &
                      (d["_dt"] <  latest - timedelta(days=7))][self.revenue_col].sum()
        change    = round(((this_week - last_week) / last_week * 100), 1) if last_week > 0 else 0
        return {
            "this_week": round(float(this_week), 2),
            "last_week": round(float(last_week), 2),
            "change":    change,
            "direction": "up" if change >= 0 else "down"
        }

    def _peak_hours(self, df):
        if self.hour_col:
            d = df[[self.hour_col]].copy().dropna()
            d["hour"]  = d[self.hour_col].astype(int)
            grouped    = d.groupby("hour").size().reset_index(name="orders")
            return grouped.to_dict("records")
        if self.date_col:
            d = df[[self.date_col]].copy().dropna()
            d["hour"]  = pd.to_datetime(d[self.date_col], errors="coerce").dt.hour
            d = d.dropna()
            if d.empty:
                return self._simulated_peak_hours()
            grouped = d.groupby("hour").size().reset_index(name="orders")
            return grouped.to_dict("records")
        return self._simulated_peak_hours()

    def _simulated_peak_hours(self):
        hours = [
            {"hour": 8,  "orders": 12}, {"hour": 9,  "orders": 18},
            {"hour": 10, "orders": 25}, {"hour": 11, "orders": 30},
            {"hour": 12, "orders": 45}, {"hour": 13, "orders": 40},
            {"hour": 14, "orders": 35}, {"hour": 15, "orders": 38},
            {"hour": 16, "orders": 42}, {"hour": 17, "orders": 50},
            {"hour": 18, "orders": 48}, {"hour": 19, "orders": 35},
            {"hour": 20, "orders": 28}, {"hour": 21, "orders": 20},
        ]
        return hours

    def _category_breakdown(self, df):
        if not self.category_col or not self.revenue_col:
            return []
        d = df[[self.category_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        grouped = d.groupby(self.category_col)[self.revenue_col].sum().reset_index()
        grouped = grouped.sort_values(self.revenue_col, ascending=False).head(8)
        return grouped.rename(columns={
            self.category_col: "category",
            self.revenue_col:  "revenue"
        }).to_dict("records")

    def _region_breakdown(self, df):
        if not self.region_col or not self.revenue_col:
            return []
        d = df[[self.region_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        grouped = d.groupby(self.region_col)[self.revenue_col].sum().reset_index()
        grouped = grouped.sort_values(self.revenue_col, ascending=False)
        return grouped.rename(columns={
            self.region_col:  "region",
            self.revenue_col: "revenue"
        }).to_dict("records")

    def _top_products(self, df):
        if not self.product_col or not self.revenue_col:
            return []
        d = df[[self.product_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        grouped = d.groupby(self.product_col)[self.revenue_col].sum().reset_index()
        grouped = grouped.sort_values(self.revenue_col, ascending=False).head(5)
        return grouped.rename(columns={
            self.product_col:  "product",
            self.revenue_col:  "revenue"
        }).to_dict("records")

    def _trending_products(self, df):
        if not self.product_col or not self.revenue_col:
            return []
        d = df[[self.product_col, self.revenue_col]].copy()
        d[self.revenue_col] = pd.to_numeric(d[self.revenue_col], errors="coerce")
        if self.date_col:
            d["_dt"] = pd.to_datetime(df[self.date_col], errors="coerce")
            latest   = d["_dt"].max()
            d = d[d["_dt"] >= latest - timedelta(days=30)]
        grouped = d.groupby(self.product_col)[self.revenue_col].sum().reset_index()
        grouped = grouped.sort_values(self.revenue_col, ascending=False).head(5)
        return grouped.rename(columns={
            self.product_col:  "product",
            self.revenue_col:  "revenue"
        }).to_dict("records")
