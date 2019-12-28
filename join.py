import pickle
from functools import reduce
import pandas
from consts import LEM, CMP, SCH, MWE
from collections import Counter
import click
import numpy as np


def mk_cnt_filter(*matches):
    def res(row):
        return row["cnt"] if row["typ"] in matches else 0
    return res


@click.command()
@click.argument("infs", nargs=-1, type=click.Path())
@click.argument("outf", type=click.File("wb"))
@click.option("--do-lextract/--no-lextract", default=True)
def main(infs, outf, do_lextract):
    counters = []
    for infn in infs:
        with open(infn, "rb") as inf:
            counters.append(pickle.load(inf))
    total = reduce(lambda a, b: a + b, counters, Counter())
    df = pandas.DataFrame([(lemma, typ, cnt) for (lemma, typ), cnt in total.items()], columns=("lemma", "typ", "cnt"))
    df["rank"] = df["cnt"].rank(method="first", ascending=False)
    df.sort_values("rank", inplace=True, ascending=False)
    df["tokcnt"] = np.where(df["typ"].isin((LEM, CMP)), df["cnt"], 0)
    df["cmpcnt"] = np.where(df["typ"] == CMP, df["cnt"], 0)
    cum_lbls = ["cumtoks", "cumcmps"]
    cnt_lbls = ["tokcnt", "cmpcnt"]
    if do_lextract:
        df["schcnt"] = np.where(df["typ"] == SCH, df["cnt"], 0)
        df["mwecnt"] = np.where(df["typ"] == MWE, df["cnt"], 0)
        cum_lbls += ["cumschs", "cummwes"]
        cnt_lbls += ["schcnt", "mwecnt"]
    df[cum_lbls] = df[cnt_lbls].cumsum()
    tottoks = df["cumtoks"][0]
    df["freq"] = df["cumtoks"] / tottoks
    df["cmpspertok"] = df["cumcmps"] / df["cumtoks"]
    if do_lextract:
        df["schspertok"] = df["cumschs"] / df["cumtoks"]
        df["mwespertok"] = df["cummwes"] / df["cumtoks"]
        df["allmwespertok"] = (df["cumschs"] + df["cummwes"]) / df["cumtoks"]
    df.drop(columns=["cumtoks", "cumcmps", "cumschs", "cummwes", "tokcnt", "cmpcnt", "schcnt", "mwecnt"], inplace=True, errors="ignore")
    df.set_index("rank", inplace=True)

    pickle.dump(df, outf)


if __name__ == "__main__":
    main()
