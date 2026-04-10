import pandas as pd
import numpy as np
import os

class ExcelParser:
    """
    Handles multi-department Excel files where departments
    are arranged side by side in one sheet
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.ext      = os.path.splitext(filepath)[1].lower()

    def parse(self):
        """
        Returns a dict of department DataFrames and
        a combined flat DataFrame for the KPI engine
        """
        if self.ext not in [".xlsx", ".xls", ".xlsm"]:
            raise ValueError(f"Not an Excel file: {self.ext}")

        xl = pd.ExcelFile(self.filepath)
        departments = {}
        combined    = None

        for sheet in xl.sheet_names:
            raw = pd.read_excel(
                self.filepath,
                sheet_name = sheet,
                header     = None
            )
            dept_frames = self._split_departments(raw, sheet)
            departments.update(dept_frames)

        if departments:
            combined = self._build_combined(departments)

        return combined, departments

    def _split_departments(self, raw, sheet_name):
        """
        Detects department blocks in a wide sheet
        and splits them into separate DataFrames
        """
        depts = {}

        # Find the header row (row with most non-null values)
        non_null_counts = raw.notna().sum(axis=1)
        header_row      = non_null_counts.idxmax()

        # Find department section titles (row above headers)
        dept_title_row  = header_row - 1 if header_row > 0 else None
        dept_titles     = {}

        if dept_title_row is not None:
            for col_idx, val in enumerate(
                raw.iloc[dept_title_row]
            ):
                if pd.notna(val) and isinstance(val, str) and len(str(val).strip()) > 0:
                    dept_titles[col_idx] = str(val).strip()

        # Get headers
        headers = raw.iloc[header_row].tolist()

        # Find column groups (separated by None/NaN columns)
        groups  = self._find_column_groups(headers)

        # Determine department for each group
        for group_start, group_cols in groups.items():
            dept_name = self._find_dept_name(
                group_start, dept_titles, headers, group_cols)

            if not dept_name:
                continue

            # Build DataFrame for this department
            col_names = [
                str(headers[c]).strip()
                for c in group_cols
                if pd.notna(headers[c])
            ]
            valid_cols = [
                c for c in group_cols
                if pd.notna(headers[c])
            ]

            if not col_names:
                continue

            df = raw.iloc[header_row + 1:, valid_cols].copy()
            df.columns = col_names
            df = df.dropna(how="all").reset_index(drop=True)

            # Parse dates
            for col in df.columns:
                if "date" in col.lower():
                    df[col] = pd.to_datetime(
                        df[col], errors="coerce")

            # Convert numerics
            for col in df.columns:
                if col.lower() not in ["date","machine_id",
                    "inspector","inspection_status",
                    "employee_id","attendance_status",
                    "po_number","item_id"]:
                    df[col] = pd.to_numeric(
                        df[col], errors="coerce")

            depts[dept_name] = df

        return depts

    def _find_column_groups(self, headers):
        """Groups consecutive non-null columns"""
        groups        = {}
        current_start = None
        current_cols  = []

        for i, h in enumerate(headers):
            if pd.notna(h) and str(h).strip():
                if current_start is None:
                    current_start = i
                current_cols.append(i)
            else:
                if current_cols:
                    groups[current_start] = current_cols
                    current_start = None
                    current_cols  = []

        if current_cols:
            groups[current_start] = current_cols

        return groups

    def _find_dept_name(self, group_start,
                        dept_titles, headers, group_cols):
        """Finds department name for a column group"""
        # Check dept title row first
        for title_col, title in dept_titles.items():
            if abs(title_col - group_start) <= 2:
                return title.upper().replace(" DATA","").strip()

        # Infer from column names
        col_names = " ".join([
            str(headers[c]).lower()
            for c in group_cols
            if pd.notna(headers[c])
        ])

        if any(k in col_names for k in [
            "production","machine","downtime","output"
        ]):
            return "PRODUCTION"
        if any(k in col_names for k in [
            "quality","inspect","defect","rejection"
        ]):
            return "QUALITY"
        if any(k in col_names for k in [
            "employee","attendance","hr","staff","leave"
        ]):
            return "HR"
        if any(k in col_names for k in [
            "purchase","po_number","order_qty","vendor","supplier"
        ]):
            return "PURCHASE"
        if any(k in col_names for k in [
            "stock","item","store","inventory","warehouse"
        ]):
            return "STORE"

        return f"DEPT_{group_start}"

    def _build_combined(self, departments):
        """
        Builds a combined flat DataFrame
        using production data as the base
        and merging on date where possible
        """
        priority = ["PRODUCTION","QUALITY","HR","PURCHASE","STORE"]

        base = None
        for dept in priority:
            if dept in departments:
                base = departments[dept].copy()
                base.columns = [
                    f"{dept.lower()}_{c}"
                    if c.lower() != "date"
                    else "date"
                    for c in base.columns
                ]
                break

        if base is None:
            # Just use the first available department
            first_key = list(departments.keys())[0]
            base = departments[first_key].copy()

        # Add key columns from other departments
        for dept in priority:
            if dept not in departments:
                continue
            df = departments[dept].copy()
            if "Date" not in df.columns:
                continue
            df = df.rename(columns={"Date":"date"})
            df.columns = [
                f"{dept.lower()}_{c}"
                if c != "date" else "date"
                for c in df.columns
            ]
            if "date" in base.columns and "date" in df.columns:
                try:
                    base = pd.merge(base, df, on="date", how="left")
                except Exception:
                    pass

        return base