import pandas as pd
import numpy as np
import json
import os

class DataCleaner:
    def __init__(self):
        self.report = {
            "original_rows":    0,
            "original_cols":    0,
            "duplicates_removed": 0,
            "nulls_filled":     0,
            "columns_dropped":  [],
            "type_conversions": [],
            "final_rows":       0,
            "final_cols":       0,
        }

    def clean(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        elif ext == ".json":
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        self.report["original_rows"] = len(df)
        self.report["original_cols"] = len(df.columns)

        df = self._clean_column_names(df)
        df = self._drop_empty_columns(df)
        df = self._remove_duplicates(df)
        df = self._fill_nulls(df)
        df = self._convert_types(df)
        df = self._strip_whitespace(df)

        self.report["final_rows"] = len(df)
        self.report["final_cols"] = len(df.columns)

        return df, self.report

    def _clean_column_names(self, df):
        df.columns = (
            df.columns.str.strip()
                      .str.lower()
                      .str.replace(r"[^a-z0-9]+", "_", regex=True)
                      .str.strip("_")
        )
        return df

    def _drop_empty_columns(self, df):
        threshold = 0.8
        before    = list(df.columns)
        df        = df.dropna(thresh=int(len(df) * (1 - threshold)), axis=1)
        dropped   = [c for c in before if c not in df.columns]
        self.report["columns_dropped"] = dropped
        return df

    def _remove_duplicates(self, df):
        before = len(df)
        df     = df.drop_duplicates()
        self.report["duplicates_removed"] = before - len(df)
        return df

    def _fill_nulls(self, df):
        filled = 0
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count == 0:
                continue
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0]
                          if not df[col].mode().empty else "Unknown")
            filled += null_count
        self.report["nulls_filled"] = int(filled)
        return df

    def _convert_types(self, df):
        conversions = []
        for col in df.columns:
            if df[col].dtype == object:
                converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
                if converted.notna().sum() > len(df) * 0.7:
                    df[col] = converted
                    conversions.append(f"{col} → datetime")
                    continue
                try:
                    df[col] = pd.to_numeric(df[col].str.replace(r"[,$%]", "", regex=True))
                    conversions.append(f"{col} → numeric")
                except Exception:
                    pass
        self.report["type_conversions"] = conversions
        return df

    def _strip_whitespace(self, df):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()
        return df