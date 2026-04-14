import pandas as pd
import os

class ExcelParser:
    """
    Handles multi-sheet Excel files
    Each sheet = one department
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.ext = os.path.splitext(filepath)[1].lower()

    def parse(self):
        if self.ext not in [".xlsx", ".xls", ".xlsm"]:
            raise ValueError(f"Not an Excel file: {self.ext}")

        xls = pd.ExcelFile(self.filepath)

        departments = {}
        combined = None

        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            if df.empty:
                continue

            dept_name = sheet.strip().upper()
            departments[dept_name] = df

        # optional combined
        if departments:
            combined = pd.concat(departments.values(), ignore_index=True)

        print("DETECTED DEPARTMENTS:", departments.keys())

        return combined, departments