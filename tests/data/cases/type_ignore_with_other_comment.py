import pandas as pd

interval_td = pd.Interval(
    pd.Timedelta("1 days"), pd.Timedelta("2 days"), closed="neither"
)

_td = (  # pyright: ignore[reportOperatorIssue,reportUnknownVariableType]
    interval_td
    - pd.Interval(  # type: ignore[operator]
        pd.Timedelta(1, "ns"), pd.Timedelta(2, "ns")
    )
)

# output

import pandas as pd

interval_td = pd.Interval(
    pd.Timedelta("1 days"), pd.Timedelta("2 days"), closed="neither"
)

_td = (  # pyright: ignore[reportOperatorIssue,reportUnknownVariableType]
    interval_td
    - pd.Interval(  # type: ignore[operator]
        pd.Timedelta(1, "ns"), pd.Timedelta(2, "ns")
    )
)
