import sys
import pickle
import click
import matplotlib.pyplot as plt


@click.command()
@click.argument('inf', type=click.File("rb"))
@click.argument('outf', type=click.Path())
@click.option('--cmps-only/--all')
def main(inf, outf, cmps_only):
    df = pickle.load(inf)
    smp = df.iloc[range(-1, -4000, -100)]
    print(smp)
    if cmps_only:
        ys = ["cmpspertok"]
    else:
        ys = ["cmpspertok", "schspertok", "mwespertok", "allmwespertok"]
    fig = plt.gcf()
    fig.set_size_inches(645.0 / 72, 441.0 / 72)
    df.plot.line(y=ys, logx=True)
    if outf:
        plt.savefig(outf, bbox_inches="tight")
    else:
        plt.show()


if __name__ == "__main__":
    main()
