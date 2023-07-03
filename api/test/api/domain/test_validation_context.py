from unittest.mock import Mock

import pandas as pd

from api.domain.validation_context import ValidationContext


class TestValidationContext:
    def test_function_chain_call_with_errors(self):
        df1 = pd.DataFrame()

        context = ValidationContext(df1)

        func1 = Mock()
        df2 = pd.DataFrame({"col1": [1, 2, 3]})
        func1.return_value = (df2, ["error1"])

        func2 = Mock()
        df3 = pd.DataFrame({"col2": [3, 4, 5]})
        func2.return_value = (df3, ["error2"])

        result = context.pipe(func1).pipe(func2, "arg1", "arg2")

        func1.assert_called_once_with(df1)
        func2.assert_called_once_with(df2, "arg1", "arg2")

        assert result.get_dataframe().equals(df3)
        assert result.errors() == ["error1", "error2"]
