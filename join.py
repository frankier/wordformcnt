import sys
import pickle
from functools import reduce
import pandas
from consts import (LEM, CMP, SCH, MWE)


def mk_cnt_filter(*matches):
    def res(row):
        return row["cnt"] if row["typ"] in matches else 0
    return res


def main():
    assert len(sys.argv) >= 3
    counters = []
    for infn in sys.argv[1:-1]:
        with open(infn, "rb") as inf:
            counters.append(pickle.load(inf))
    total = reduce(lambda a, b: a.update(b), counters)
    df = pandas.DataFrame([(lemma, typ, cnt) for (lemma, typ), cnt in total.items()], columns=("lemma", "typ", "cnt"))
    df["rank"] = df["cnt"].rank(method="first", ascending=False)
    df.sort_values("rank", inplace=True, ascending=False)
    df["tokcnt"] = df.apply(mk_cnt_filter(LEM, CMP), 1)
    df["cmpcnt"] = df.apply(mk_cnt_filter(CMP), 1)
    df["schcnt"] = df.apply(mk_cnt_filter(SCH), 1)
    df["mwecnt"] = df.apply(mk_cnt_filter(MWE), 1)
    df[["cumtoks", "cumcmps", "cumschs", "cummwes"]] = df[["tokcnt", "cmpcnt", "schcnt", "mwecnt"]].cumsum()
    df["cmpspertok"] = df.apply(lambda row: row["cumcmps"] / row["cumtoks"], 1)
    df["schspertok"] = df.apply(lambda row: row["cumschs"] / row["cumtoks"], 1)
    df["mwespertok"] = df.apply(lambda row: row["cummwes"] / row["cumtoks"], 1)
    df["allmwespertok"] = df.apply(lambda row: (row["cumschs"] + row["cummwes"]) / row["cumtoks"], 1)
    df.drop(columns=["cumtoks", "cumcmps", "cumschs", "cummwes", "tokcnt", "cmpcnt", "schcnt", "mwecnt"], inplace=True)
    df.set_index("rank", inplace=True)

    pickle.dump(df, open(sys.argv[-1], 'wb'))


if __name__ == "__main__":
    main()
