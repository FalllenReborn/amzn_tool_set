# by Targosz Seweryn
# tseweryn@amazon.com

import pandas as pd

from defect_logger import defect_logger


class GrabDataframe:
    @staticmethod
    @defect_logger
    def get_df_excel(ex_path):
        df = pd.read_excel(
            ex_path,
            sheet_name=0,
            header=0,
            names=None,
            index_col=None,
            usecols=None,
            squeeze=None,
            dtype=None,
            engine=None,
            converters=None,
            true_values=None,
            false_values=None,
            skiprows=None,
            nrows=None,
            na_values=None,
            keep_default_na=True,
            na_filter=True,
            verbose=False,
            parse_dates=False,
            date_parser=None,
            thousands=None,
            decimal=',',
            comment=None,
            skipfooter=0,
            convert_float=None,
            mangle_dupe_cols=True,
            storage_options=None
        )
        return df
