import pandas as pd
import numpy as np
import os

class DataReconciler:
    def __init__(self):
        self.key_cols = ['Territory', 'Product Code', 'PART NO', 'Ship to']

    def get_sheet_names(self, filepath):
        if filepath.lower().endswith('.xlsx'):
            try:
                xls = pd.ExcelFile(filepath)
                return xls.sheet_names
            except Exception as e:
                raise Exception(f"ไม่สามารถอ่านโครงสร้างไฟล์ Excel ได้: {str(e)}")
        else:
            return ["CSV Default"]

    def get_columns(self, filepath, sheet_name):
        df = self.clean_and_prepare_df(filepath, sheet_name)
        return list(df.columns)

    def clean_and_prepare_df(self, filepath, sheet_name, row_range=""):
        try:
            if filepath.lower().endswith('.csv'):
                encodings = ['utf-8-sig', 'utf-8', 'cp874', 'tis-620', 'windows-1252']
                df = None
                for enc in encodings:
                    try:
                        df = pd.read_csv(filepath, header=None, encoding=enc, dtype=str, sep=None, engine='python')
                        break
                    except Exception:
                        continue
            else:
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=None, dtype=str)

            if df is None or df.empty:
                raise ValueError(f"ไม่พบข้อมูลใน Sheet: {sheet_name}")

            header_idx = -1
            for idx, row in df.head(50).iterrows():
                row_vals = [str(val).strip().lower() for val in row.values if pd.notna(val)]
                if any('territory' in str(v) for v in row_vals) and any('part' in str(v) and 'no' in str(v) for v in row_vals):
                    header_idx = idx
                    break
            
            if header_idx == -1:
                raise KeyError(f"ใน Sheet '{sheet_name}' 不ไม่พบหัวตารางข้อมูลหลัก")

            columns = []
            for i, c in enumerate(df.iloc[header_idx]):
                c_str = str(c).strip()
                c_lower = c_str.lower()
                
                if 'territory' in c_lower: columns.append('Territory')
                elif 'product' in c_lower and 'code' in c_lower: columns.append('Product Code')
                elif 'part' in c_lower and 'no' in c_lower: columns.append('PART NO')
                elif 'ship' in c_lower and 'to' in c_lower: columns.append('Ship to')
                elif c_lower == 'nan' or c_lower == '' or c_lower == 'none': columns.append(f"Unnamed_Col_{i}")
                else: columns.append(c_str)
            
            df.columns = columns
            df = df.iloc[header_idx + 1:].reset_index(drop=True)
            df = df.loc[:, ~df.columns.duplicated()]
            
            if row_range.strip():
                try:
                    start, end = map(int, row_range.split('-'))
                    df = df.iloc[max(0, start-1):end]
                except:
                    pass 
            
            for col in self.key_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    df = df[df[col].notna() & (df[col] != '') & (df[col].str.lower() != 'nan') & (df[col].str.lower() != 'none')]
            
            if df.set_index(self.key_cols).index.duplicated().any():
                df = df[~df.set_index(self.key_cols).index.duplicated(keep='first')]

            return df
        except Exception as e:
            raise Exception(f"Error in {os.path.basename(filepath)} (Sheet: {sheet_name}): {str(e)}")

    def compare_data(self, file1, sheet1, file2, sheet2, target_cols=None, row_range=""):
        df1 = self.clean_and_prepare_df(file1, sheet1, row_range)
        df2 = self.clean_and_prepare_df(file2, sheet2, row_range)

        missing1 = [c for c in self.key_cols if c not in df1.columns]
        missing2 = [c for c in self.key_cols if c not in df2.columns]
        if missing1 or missing2:
            raise KeyError(f"Missing Key Columns. File1: {missing1}, File2: {missing2}")

        df1.set_index(self.key_cols, inplace=True)
        df2.set_index(self.key_cols, inplace=True)

        common_cols = list(df1.columns.intersection(df2.columns))

        if target_cols:
            filtered_common = [c for c in common_cols if c in target_cols or c in self.key_cols]
            common_cols = filtered_common

        common_cols = pd.Index(common_cols)

        df1_c = df1[common_cols].fillna('')
        df2_c = df2[common_cols].fillna('')

        new_keys = df2_c.index.difference(df1_c.index)
        df_new = df2_c.loc[new_keys].copy()
        df_new['Status'] = 'New'

        deleted_keys = df1_c.index.difference(df2_c.index)
        df_deleted = df1_c.loc[deleted_keys].copy()
        df_deleted['Status'] = 'Deleted'

        common_keys = df1_c.index.intersection(df2_c.index)
        df1_common = df1_c.loc[common_keys].sort_index()
        df2_common = df2_c.loc[common_keys].sort_index()

        diff_mask = (df1_common != df2_common)
        changed_rows = diff_mask.any(axis=1)
        
        df_changed = pd.DataFrame()
        if changed_rows.any():
            df1_diff = df1_common[changed_rows]
            df2_diff = df2_common[changed_rows]
            records = []
            
            for idx in df1_diff.index:
                row_data = {'Status': 'Changed'}
                if isinstance(idx, tuple):
                    row_data.update(dict(zip(self.key_cols, idx)))
                else:
                    row_data.update({self.key_cols[0]: idx})
                
                for col in common_cols:
                    val1 = str(df1_diff.loc[idx, col]).strip()
                    val2 = str(df2_diff.loc[idx, col]).strip()
                    if val1 != val2:
                        val1_disp = "-" if val1 == "" else val1
                        val2_disp = "-" if val2 == "" else val2
                        row_data[col] = f"[ {val1_disp} ➔ {val2_disp} ]"
                    else:
                        row_data[col] = val2
                records.append(row_data)
                
            df_changed = pd.DataFrame(records)
            if not df_changed.empty:
                df_changed.set_index(self.key_cols, inplace=True)

        result_df = pd.concat([df_changed, df_new, df_deleted]).reset_index()
        
        if not result_df.empty:
            cols_order = ['Status'] + self.key_cols + [c for c in result_df.columns if c not in self.key_cols and c != 'Status']
            result_df = result_df[cols_order]

        return result_df