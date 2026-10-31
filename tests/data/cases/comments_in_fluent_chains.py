def f():
    return (
        df_day.assign(date=date, fund_ticker=ticker).pipe(lambda x: x.loc[x["Shares"].notnull()])
        # arrives as int sometimes
        .assign(Shares=df_day["Shares"].astype("float64"))
    )


def f2():
    return (
        df_day.assign(date=date, fund_ticker=ticker).pipe(lambda x: x.loc[x["Shares"].notnull()])
        # arrives as int sometimes
        # second comment
        .assign(Shares=df_day["Shares"].astype("float64"))
    )


def f3():
    return (
        query.filter(User.active == True)
        # comment on ordering
        .order_by(User.created_at)
        # comment on limit
        .limit(10)
    )


def f4():
    return (
        base.first()
        # comment before second
        .second()
        # comment before attr
        .attr
    )


# output


def f():
    return (
        df_day.assign(date=date, fund_ticker=ticker)
        .pipe(lambda x: x.loc[x["Shares"].notnull()])
        # arrives as int sometimes
        .assign(Shares=df_day["Shares"].astype("float64"))
    )


def f2():
    return (
        df_day.assign(date=date, fund_ticker=ticker)
        .pipe(lambda x: x.loc[x["Shares"].notnull()])
        # arrives as int sometimes
        # second comment
        .assign(Shares=df_day["Shares"].astype("float64"))
    )


def f3():
    return (
        query.filter(User.active == True)
        # comment on ordering
        .order_by(User.created_at)
        # comment on limit
        .limit(10)
    )


def f4():
    return (
        base.first()
        # comment before second
        .second()
        # comment before attr
        .attr
    )
