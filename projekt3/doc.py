# !/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def print_data(df: pd.DataFrame):
    df.loc[(df.p11 < 3, "p11")] = 0
    df.loc[(df.p11 > 2, "p11")] = 1

    df.loc[(df.p12 > 600, "p12")] = 6
    df.loc[(df.p12 > 500, "p12")] = 5
    df.loc[(df.p12 > 400, "p12")] = 4
    df.loc[(df.p12 > 300, "p12")] = 3
    df.loc[(df.p12 > 200, "p12")] = 2
    df.loc[(df.p12 == 100, "p12")] = 1

    df.loc[(df.p5a == 1, "p5a")] = "V obci"
    df.loc[(df.p5a == 2, "p5a")] = "Mimo obec"

    df1 = df.groupby(["p12", "p5a"])["p5a"].count().reset_index(name="count")
    df2 = df.groupby(["p12"])["p12"].count().reset_index(name="count")
    df3 = df[df.p11 != 0]
    df3 = df3.groupby(["p12", "p11"])["p12"].count().reset_index(name="count")

    table = pd.crosstab([df.p5a, df.p11], df.p12, rownames=["lokace", "Drogy"],
                        colnames=["příčina"])

    print("Vysvětlivky:\n" +
          "\tsloupce:\n" +
          "\t   1: nezaviněná řidičem\n" +
          "\t   2: nepřiměřená rychlost jízdy\n" +
          "\t   3: nesprávné předjíždění\n" +
          "\t   4: nedání přednosti v jízdě\n" +
          "\t   5: nesprávný způsob jízdy\n" +
          "\t   6: technická závada vozidla\n" +
          "\n\tdrogy:\n" +
          "\t   1: řidič byl pod omamnými látkami\n" +
          "\t   0: řidič nebyl pod omamnými látkami\n")

    print("Tabulka:")
    print("------------------------------------------------------------------")
    print(table)
    print("------------------------------------------------------------------")

    print("\nProcentuání rozdělení nehod:")

    print("\nnezaviněná řidičem:\t\t" +
          str(round((100/df.p12.count())*df2.values[0][1], 2)) +
          " % z toho " +
          str(round((100/df2.values[0][1])*df3.values[0][2], 2)) +
          "  % pod vlivem drog")

    print("nepřiměřená rychlost jízdy: \t" +
          str(round((100/df.p12.count())*df2.values[1][1], 2)) +
          " % z toho " +
          str(round((100/df2.values[1][1])*df3.values[1][2], 2)) +
          " % pod vlivem drog")

    print("nesprávné předjíždění: \t\t" +
          str(round((100/df.p12.count())*df2.values[2][1], 2)) +
          "  % z toho " +
          str(round((100/df2.values[2][1])*df3.values[2][2], 2)) +
          "  % pod vlivem drog")

    print("nedání přednosti v jízdě: \t" +
          str(round((100/df.p12.count())*df2.values[3][1], 2)) +
          " % z toho " +
          str(round((100/df2.values[3][1])*df3.values[3][2], 2)) +
          "  % pod vlivem drog")

    print("nesprávný způsob jízdy: \t" +
          str(round((100/df.p12.count())*df2.values[4][1], 2)) +
          " % z toho " +
          str(round((100/df2.values[4][1])*df3.values[4][2], 2)) +
          " % pod vlivem drog")

    print("technická závada vozidla: \t" +
          str(round((100/df.p12.count())*df2.values[5][1], 2)) +
          "  % z toho " +
          str(round((100/df2.values[5][1])*df3.values[5][2], 2)) +
          "  % pod vlivem drog")

    print("\nPočet nehod:")

    print("\nCelkově: \t" + str(df.p12.count()))

    print("\nV obci: \t" + str(df[df["p5a"] == "V obci"].count()["p5a"]) +
          " ( " + str(round((100/df.p12.count()) *
                      df[df["p5a"] == "V obci"].count()["p5a"], 2)) + " % )")

    print("Mimo obec: \t" + str(df[df["p5a"] == "Mimo obec"].count()["p5a"]) +
          " ( " + str(round((100/df.p12.count()) *
                      df[df["p5a"] == "Mimo obec"].count()["p5a"], 2)) +
          " % )")

    print("\nnezaviněná řidičem:\t\t" + str(df2.values[0][1]))
    print("nepřiměřená rychlost jízdy: \t" + str(df2.values[1][1]))
    print("nesprávné předjíždění: \t\t" + str(df2.values[2][1]))
    print("nedání přednosti v jízdě: \t" + str(df2.values[3][1]))
    print("nesprávný způsob jízdy: \t" + str(df2.values[4][1]))
    print("technická závada vozidla: \t" + str(df2.values[5][1]))

    labels = ["nezaviněná řidičem",
              "nepřiměřená rychlost jízdy",
              "nesprávné předjíždění",
              "nedání přednosti v jízdě",
              "nesprávný způsob jízdy",
              "technická závada vozidla"]

    sns.set(rc={'axes.facecolor': 'grey'})

    fig, ax = plt.subplots(1, 1, figsize=(13, 7), sharey=True,
                           constrained_layout=True)

    # nastaveni dat pro dany graf
    sns.barplot(ax=ax, x='p12', y='count', hue='p5a', data=df1)
    ax.set_yscale("log")
    ax.set_xticklabels(labels)
    ax.set(ylabel="Počet nehod", xlabel="Hlavní příčina nehody")

    fig.savefig("graf.png")
    plt.close(fig)


if __name__ == "__main__":
    print_data(pd.read_pickle("accidents.pkl.gz"))
