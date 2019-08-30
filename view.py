import sys
import pickle


def main():
    with open(sys.argv[1], "rb") as inf:
        df = pickle.load(inf)
    smp = df.iloc[range(-1, -4000, -100)]
    print(smp)
    df.plot.line(y=["cmpspertok", "schspertok", "mwespertok", "allmwespertok"])
    import matplotlib.pyplot as plt
    plt.show()


if __name__ == "__main__":
    main()
