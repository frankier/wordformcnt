import pickle
from functools import reduce
import pandas
from consts import LEM, CMP, SCH, MWE
from collections import Counter
import click


def mk_cnt_filter(*matches):
    def res(row):
        return row["cnt"] if row["typ"] in matches else 0
    return res


@click.command()
@click.argument("infs", multiple=True, type=click.Path())
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
    df["tokcnt"] = df.apply(mk_cnt_filter(LEM, CMP), 1)
    df["cmpcnt"] = df.apply(mk_cnt_filter(CMP), 1)
    if do_lextract:
        df["schcnt"] = df.apply(mk_cnt_filter(SCH), 1)
        df["mwecnt"] = df.apply(mk_cnt_filter(MWE), 1)
    df[["cumtoks", "cumcmps", "cumschs", "cummwes"]] = df[["tokcnt", "cmpcnt", "schcnt", "mwecnt"]].cumsum()
    tottoks = df["cumtoks"][0]
    df["freq"] = df.apply(lambda row: row["cumtoks"] / tottoks, 1)
    df["cmpspertok"] = df.apply(lambda row: row["cumcmps"] / row["cumtoks"], 1)
    if do_lextract:
        df["schspertok"] = df.apply(lambda row: row["cumschs"] / row["cumtoks"], 1)
        df["mwespertok"] = df.apply(lambda row: row["cummwes"] / row["cumtoks"], 1)
        df["allmwespertok"] = df.apply(lambda row: (row["cumschs"] + row["cummwes"]) / row["cumtoks"], 1)
    df.drop(columns=["cumtoks", "cumcmps", "cumschs", "cummwes", "tokcnt", "cmpcnt", "schcnt", "mwecnt"], inplace=True, errors="ignore")
    df.set_index("rank", inplace=True)

    pickle.dump(df, outf)


if __name__ == "__main__":
    main()
