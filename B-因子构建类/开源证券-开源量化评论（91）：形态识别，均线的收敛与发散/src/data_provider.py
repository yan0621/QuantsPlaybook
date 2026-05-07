"""
Author: Hugo
Date: 2024-06-05 15:31:53
LastEditors: shen.lan123@gmail.com
LastEditTime: 2026-05-07 10:11:14
Description: 

用于加载本地数据
"""

from datetime import datetime, time
from pathlib import Path
from typing import Optional

import pandas as pd
from cachetools import TTLCache, cached
from loguru import logger

DATA_PATH:Path = Path(__file__).parents[1]


class LoadH5Data:
    def __init__(self):
        super().__init__()

    @staticmethod
    def _resolve_module_storage(module_id: str) -> tuple[Path, str]:
        """兼容历史模块命名，返回实际数据目录与元数据模块名。"""
        if module_id in {"data", "Dataset"}:
            return DATA_PATH / "data", "Dataset"
        return DATA_PATH / module_id, module_id

    @staticmethod
    def _resolve_trading_loc(
        trading_dates: pd.Index, date: pd.Timestamp, method: str = "ffill"
    ) -> int:
        """兼容 pandas 2.x 的交易日索引定位。"""
        key = date
        # 若交易日索引为字符串（如 YYYYMMDD），则保持旧逻辑的键格式。
        if not isinstance(trading_dates, pd.DatetimeIndex):
            key = date.strftime("%Y%m%d")

        idx = trading_dates.get_indexer([key], method=method)[0]
        if idx == -1:
            raise KeyError(f"cannot locate trading date {date} with method={method}")
        return int(idx)

    def load_meta(self, data_path: Path, module_id: str) -> Optional[dict]:
        meta_file: Path = data_path / f"meta_{module_id}"
        if not meta_file.is_file():
            return None
        try:
            # with open(meta_file, "rb") as f:
            #     return pickle.load(f)
            return pd.read_pickle(meta_file)
        except Exception as e:
            logger.info(e)
            return None
    

    @cached(cache=TTLCache(maxsize=3, ttl=3600))
    def get_trading_dates(self) -> pd.Index:
        calendar_file: Path = DATA_PATH /"data" / "calendar.h5"
        if not calendar_file.exists():
            raise IOError(f"{calendar_file} does not exist")

        ser_calendar: pd.Series = pd.read_hdf(calendar_file)["dates"].sort_values()
        return pd.Index(ser_calendar)

    def get_pre_trading_date(self, date: datetime) -> datetime:
        date:pd.Timestamp = pd.to_datetime(date)
        trading_dates: pd.Index = self.get_trading_dates()
        ix: int = self._resolve_trading_loc(trading_dates, date, method="ffill") - 1
        pre_trading_date: datetime = trading_dates[ix]
        return pre_trading_date

    def get_nearest_trading_date(
        self, date: datetime, method: str = "ffill"
    ) -> datetime:
        date:pd.Timestamp = pd.to_datetime(date)
        trading_dates: pd.Index = self.get_trading_dates()
        idx:int= self._resolve_trading_loc(trading_dates, date, method=method)
        return trading_dates[idx]

    def get_shifted_trading_date(self, date: datetime, shift_days: int) -> datetime:
        date:pd.Timestamp = pd.to_datetime(date)
        trading_dates: pd.Index = self.get_trading_dates()
        ix: int = self._resolve_trading_loc(trading_dates, date, method="ffill")
        return trading_dates[ix + shift_days]
    
    @cached(cache=TTLCache(maxsize=128, ttl=3600))
    def get_data(
        self, 
        name: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        module_id, data_id = name.split(".")
        assert len(module_id) and len(data_id), "getData only supports (module_id.data_id) pattern!"

        if start_date is None:
            start_date = datetime(2007, 1, 1)
        if end_date is None:
            end_date = datetime.combine(datetime.now().date(), time())
            end_date = self.get_pre_trading_date(end_date)

        start_date,end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
        end_date = self.get_nearest_trading_date(end_date, method="ffill")
        
        data_path, meta_module_id = self._resolve_module_storage(module_id)
        meta: Optional[dict] = self.load_meta(data_path, meta_module_id)
        assert meta is not None, f"{name} doesn't exist!"

        start_date_str: str = start_date.strftime("%Y-%m-%d")
        
        end_date_str: str = end_date.strftime("%Y-%m-%d")
        assert meta["startDate"] <= start_date, f"start_date in {name} meta file is later than {start_date_str}"
        assert meta["endDate"] >= end_date, f"end_date in {name} meta file is earlier than {end_date_str}"

        target_file_path: Path = data_path / f"{data_id}.h5"
        data: pd.DataFrame = pd.read_hdf(target_file_path)
        data = data.loc[start_date_str:end_date_str]
        return data

    def get_shifted_data(
        self, name: str, start_date: datetime, end_date: datetime, shift_days: int = -1
    ) -> pd.DataFrame:
        start_date: datetime = self.get_nearest_trading_date(start_date)
        end_date: datetime = self.get_nearest_trading_date(end_date)
        query_start_date: datetime = self.get_shifted_trading_date(
            start_date, shift_days
        )
        query_end_date: datetime = self.get_shifted_trading_date(end_date, shift_days)
        min_start_date: datetime = min(start_date, query_start_date)
        max_end_date: datetime = max(end_date, query_end_date)

        trading_dates: pd.Index = self.get_trading_dates()
        valid_trading_dates: pd.Index = trading_dates[
            trading_dates.slice_indexer(min_start_date, max_end_date)
        ]

        data: pd.DataFrame = self.get_data(
            name, start_date=query_start_date, end_date=query_end_date
        )
        data:pd.DataFrame = data.reindex(index=valid_trading_dates)
        data:pd.DataFrame = data.shift(-shift_days)
        data:pd.DataFrame = data.loc[start_date:end_date]
        return data

