#!/usr/bin/env python3.8
# coding=utf-8
# Author: Daniel Kamenický (xkamen21)

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os, sys
pd.options.mode.chained_assignment = None

# Ukol 1: nacteni dat
def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    #kontrola zdali existuje pickle soubor
    try:
        df = pd.read_pickle(filename, compression="gzip")
    except FileNotFoundError:
        sys.stderr.write("Soubor accidents.pkl.gz nebyl nalezen")
        exit(1)

    #kontrola datoveho typu dataframe
    if not isinstance(df, pd.DataFrame):
        sys.stderr.write("Data nejsou ve tvaru DataFrame")
        exit(1)

    #kontrola zdali neni dataframe prazdny
    if df is None or df.empty:
        sys.stderr.write("Pickle soubor je prazdny")
        exit(1)

    #vytvoreni noveho sloupce s datem typu datetime
    #sloupec p2a byl ponechan, nebylo specifikovane co s nim delat
    df['date'] = pd.to_datetime(df.p2a)
    #ulzoeni velikosti pred upravou
    orig_size = df.memory_usage(index=True, deep=True).sum()/1048576

    #nastaveni typu na category, dynamicky udelane pres forcyklus
    for c in df.columns:
        if c == 'region' or c == 'p13a' or c == 'p13b' or c == 'p13c' or c == 'p53' or c == 'p12' or c == 'date':
            continue
        else:
            df[c] = df[c].astype('category')

    #ulozeni nove velikosti dat
    new_size = df.memory_usage(index=True, deep=True).sum()/1048576

    #naformatovani na jedno desetinne misto
    new_size = "{:.1f}".format(new_size)
    orig_size = "{:.1f}".format(orig_size)

    #vypis velikosti pokud byl zadan verbose
    if verbose:
        print("orig_size=" + orig_size + " MB")
        print("new_size=" + new_size + " MB")

    #vraceni dataframu
    return df

# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):

    #kontrola zdali neni dataframe prazdny
    if df is None or df.empty:
        sys.stderr.write("Spatne predany DataFrame")
        exit(1)

    #rpzdeleni dataframu do mensich celku
    dfa = pd.melt(df, id_vars=['region'], value_vars=['p13a'])
    dfb = pd.melt(df, id_vars=['region'], value_vars=['p13b'])
    dfc = pd.melt(df, id_vars=['region'], value_vars=['p13c'])
    dfx = pd.melt(df, id_vars=['region'], value_vars=['p1'])

    #spocitani jednotlivych hodnot v dataframu
    dfa = dfa.groupby(["region"]).sum().reset_index()
    dfb = dfb.groupby(["region"]).sum().reset_index()
    dfc = dfc.groupby(["region"]).sum().reset_index()
    dfx = dfx.groupby(["region"]).count().reset_index()

    sns.set(rc={'axes.facecolor':'grey'})

    #vytvareni samotneho grafu
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(7, 10), constrained_layout=True)

    #nastaveni dat pro dany graf
    sns.barplot(palette = "viridis",data=dfa, x=dfa.region, y=dfa.value, ax=ax1, order = dfx.sort_values('value', ascending = False).region).set_title("Úmrtí", fontsize=20, pad=10)
    sns.barplot(palette = "viridis",data=dfb, x=dfb.region, y=dfb.value, ax=ax2, order = dfx.sort_values('value', ascending = False).region).set_title("Těžce ranění", fontsize=20, pad=10)
    sns.barplot(palette = "viridis",data=dfc, x=dfc.region, y=dfc.value, ax=ax3, order = dfx.sort_values('value', ascending = False).region).set_title("Lehce ranění", fontsize=20, pad=10)
    sns.barplot(palette = "viridis",data=dfx, x=dfx.region, y=dfx.value, ax=ax4, order = dfx.sort_values('value', ascending = False).region).set_title("Celkem nehod", fontsize=20, pad=10)

    #nastvaeni tick parametru pro lepsi prehled (pri oddelani chybelo)
    ax1.tick_params(bottom=True)
    ax2.tick_params(bottom=True)
    ax3.tick_params(bottom=True)
    ax4.tick_params(bottom=True)

    #nastaveni x a y popsiku
    ax1.set(ylabel="Počet", xlabel="")
    ax2.set(ylabel="Počet", xlabel="")
    ax3.set(ylabel="Počet", xlabel="")
    ax4.set(ylabel="Počet", xlabel="")

    #ukazani a ulozeni grafu
    if show_figure:
        plt.show()
    if fig_location != None:
        fig.savefig(fig_location)

    #uzavreni okna
    plt.close(fig)

# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):

    #kontrola zdali neni dataframe prazdny
    if df is None or df.empty:
        sys.stderr.write("Spatne predany DataFrame")
        exit(1)

    #vytazeni potrebnych kraju a vytvoreni intervalu
    regions = ['JHC', 'KVK', 'PHA', 'OLK']
    df1 = df.loc[df['region'].isin(regions)]
    df1['range'] = pd.cut(df1.p53, [0,500,2000,5000,10000, float('inf')], include_lowest=True)
    df1['type'] = pd.cut(df1.p12, [0,101,210,320,420,520,620], include_lowest=True)

    #rozdeleni dataframu na mensi dataframe
    df1 = df1.groupby(["region", "range", "type"])["region"].count().reset_index(name = "count")
    dfa = df1.loc[df1['region'] == 'JHC'].reset_index()
    dfb = df1.loc[df1['region'] == 'KVK'].reset_index()
    dfc = df1.loc[df1['region'] == 'PHA'].reset_index()
    dfd = df1.loc[df1['region'] == 'OLK'].reset_index()

    #list nazvu osy y
    labels = ["< 50","50 - 200","200 - 500","500 - 1000","> 1000"]

    #vytvareni samotneho grafu
    fig, axes = plt.subplots(2, 2, figsize=(13, 8),sharey=True, constrained_layout=True)
    ax=axes.flatten()

    #nastaveni dat pro dany graf
    sns.barplot(ax=ax[0], x='range', y='count', hue='type', data=dfa).set_title("JHC", fontsize=15)
    sns.barplot(ax=ax[1], x='range', y='count', hue='type', data=dfb).set_title("KVK", fontsize=15)
    sns.barplot(ax=ax[2], x='range', y='count', hue='type', data=dfc).set_title("PHA", fontsize=15)
    sns.barplot(ax=ax[3], x='range', y='count', hue='type', data=dfd).set_title("OLK", fontsize=15)
    ax[2].set_yscale("log")

    #schovani legend a nastaveni x a y popsiku
    for a in ax:
        a.legend([],[], frameon=False)
        a.set_xticklabels(labels)
        a.set(ylabel="Počet", xlabel = "Škoda [tisíc Kč]")

    #nastaveni legendy, jelikoz grafy jsou stejne z hlediska struktury, muzem pouzit legendu posledniho grafu (jsem si vedom ze to jde i lepe a jinak)
    l = plt.legend(bbox_to_anchor=(1.58, 1),borderaxespad=0)
    l.set_title("Příčina nehody")
    l.get_texts()[0].set_text("nezaviněná řidičem")
    l.get_texts()[1].set_text("nepřiměřená rychlost jízdy")
    l.get_texts()[2].set_text("nesprávné předjíždění")
    l.get_texts()[3].set_text("nedání přednosti v jizdě")
    l.get_texts()[4].set_text("nesprývný způsob jízdy")
    l.get_texts()[5].set_text("technická závada vozidla")

    #ukazani a ulozeni grafu
    if show_figure:
        plt.show()
    if fig_location != None:
        fig.savefig(fig_location)

    #uzavreni okna
    plt.close(fig)

# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):

    #kontrola zdali neni dataframe prazdny
    if df is None or df.empty:
        sys.stderr.write("Spatne predany DataFrame")
        exit(1)

    #vytvoreni mensiho dataframu
    regions = ['HKK', 'JHM', 'MSK', 'PLK']
    df1 = df[['region','p16','date']].copy()
    df1 = df1.loc[df['region'].isin(regions)]

    #vytvoreni crosstable
    table = pd.crosstab(index = [df1.region, df1.date], columns = df1.p16).rename(columns={0: "jiný stav", 1: "povrch suchý - neznečištěný", 2: "povrch suchý - znečištěný",
    3: "povrch mokrý", 4: "na vozovce je bláto", 5: "náledí, ujetý sníh - posypané", 6: "náledí, ujetý sníh - neposypané", 7: "rozlitý olej, nafta apod.",
    8: "souvislý sníh", 9: "náhlá změna stavu"}).reset_index()

    #rozparsovani tabulek podle kraje vice tabulek
    tableA = table.loc[table.region == 'HKK']
    tableB = table.loc[table.region == 'JHM']
    tableC = table.loc[table.region == 'MSK']
    tableD = table.loc[table.region == 'PLK']
    tableA = tableA.resample('M', on='date').sum()
    tableB = tableB.resample('M', on='date').sum()
    tableC = tableC.resample('M', on='date').sum()
    tableD = tableD.resample('M', on='date').sum()

    #nastaveni barvy pozadi
    sns.set(rc={'axes.facecolor':'grey'})

    #vytvareni samotneho grafu
    fig, axes = plt.subplots(2, 2, figsize=(13, 8),sharey=True, sharex=True, constrained_layout=True)
    ax=axes.flatten()

    #nastaveni dat pro dany graf
    sns.lineplot(ax=ax[0], data=tableA, dashes=False, palette = "viridis").set_title("HKK", fontsize=15)
    sns.lineplot(ax=ax[1], data=tableB, dashes=False, palette = "viridis").set_title("JHM", fontsize=15)
    sns.lineplot(ax=ax[2], data=tableC, dashes=False, palette = "viridis").set_title("MSK", fontsize=15)
    sns.lineplot(ax=ax[3], data=tableD, dashes=False, palette = "viridis").set_title("PLK", fontsize=15)

    #schovani legend a nastaveni x a y popsiku
    for a in ax:
        a.legend([],[], frameon=False)
        a.set(ylabel="Počet nehod", xlabel = "Datum vzniku nehody")

    #design upravy lablelu
    ax[0].set(xlabel = "")
    ax[1].set(ylabel="", xlabel = "")
    ax[3].set(ylabel = "")

    #nastaveni legendy
    l = plt.legend(bbox_to_anchor=(1.68, 1),borderaxespad=0)
    l.set_title("Stav vozovky")

    #ukazani a ulozeni grafu
    if show_figure:
        plt.show()
    if fig_location != None:
        fig.savefig(fig_location)

    #uzavreni okna
    plt.close(fig)

if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)
    pass
