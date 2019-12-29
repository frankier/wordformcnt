import pickle
import click
import matplotlib.pyplot as plt


MIN_CNT = 10


@click.command()
@click.argument('inf', type=click.File("rb"))
@click.argument('outf', type=click.Path(), required=False)
@click.option('--cmps-only/--all')
@click.option('--logx/--no-logx')
@click.option('--mark', type=int, multiple=True)
@click.option('--mark-max/--dont-mark-max')
@click.option('--cnt', type=int)
def main(inf, outf, cmps_only, logx, mark, mark_max, cnt):
    df = pickle.load(inf)
    smp = df.iloc[range(-1, -4000, -100)]
    print(smp)
    ys = ["freq", "cmpspertok"]
    labels = ["Remaining proportion", "Compounds per token"]
    if not cmps_only:
        ys += ["schspertok", "mwespertok", "allmwespertok"]
        labels += ["Schemas per token", "Simple MWEs per token", "Combined MWEs per token"]
    df.plot.line(y=ys, logx=logx)
    fig = plt.gcf()
    fig.set_size_inches(645.0 / 72, 441.0 / 72)

    def mark_at(mark_rank):
        plt.axvline(mark_rank, linestyle="--", color="red")
        max_cmpspertok = df["cmpspertok"][mark_rank]
        print(f"Compounds per token @{mark_rank}: {max_cmpspertok}")
        plt.axhline(max_cmpspertok, linestyle="--", color="red")
        freq_at_max_cmpspertok = df["freq"][mark_rank]
        print(f"Remaining proportion @{mark_rank}: {freq_at_max_cmpspertok}")
        plt.axhline(freq_at_max_cmpspertok, linestyle="--", color="red")

    for m in mark:
        print("Mark at:", m)
        mark_at(m)

    if mark_max:
        max_rank = df[df["cnt"] > MIN_CNT]["cmpspertok"].idxmax()
        print("Rank at max compounds per token:", max_rank)
        mark_at(max_rank)

    plt.legend(labels, loc='upper right')
    plt.ylim(0, 1)
    if cnt:
        rank = df[df["cnt"] == cnt].index.min()
        print("Max rank:", rank)
        plt.xlim(0, rank)
    plt.savefig(outf, bbox_inches="tight")


if __name__ == "__main__":
    main()
