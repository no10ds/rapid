from typing import Tuple, Callable, List

import pandas as pd


class ValidationContext:
    def __init__(self, df: pd.DataFrame):
        self._error_context: List[str] = list()
        self._df: pd.DataFrame = df

    def pipe(
        self,
        function: Callable[[pd.DataFrame, ...], Tuple[pd.DataFrame, List[str]]],
        *args,
        **kwargs
    ):
        result, errors = function(self._df, *args, **kwargs)
        self._error_context.extend(errors) if errors else None
        self._df = result
        return self

    def get_dataframe(self) -> pd.DataFrame:
        return self._df

    def has_errors(self) -> bool:
        return len(self._error_context) > 0

    def errors(self) -> List[str]:
        return self._error_context
