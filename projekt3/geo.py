# !/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    df = df.dropna(subset=['d', 'e'])
    gdf = geopandas.GeoDataFrame(df,
                                 geometry=geopandas.points_from_xy(df.d, df.e),
                                 crs='EPSG:5514')
    return gdf


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    gdf_jhm = gdf[gdf["region"] == "JHM"].to_crs("epsg:3857")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 9),
                                   constrained_layout=True)

    gdf_jhm[gdf_jhm["p5a"] == 1].plot(ax=ax1, markersize=2, color='#710C04')
    ax1.set_title("Nehody v JHM kraji: v obci", fontsize=13, pad=10)

    gdf_jhm[gdf_jhm["p5a"] == 2].plot(ax=ax2, markersize=2, color='tab:green')
    ax2.set_title("Nehody v JHM kraji: mimo obec", fontsize=13, pad=10)

    ax1.set_axis_off()
    ax2.set_axis_off()

    ctx.add_basemap(ax1, crs=gdf_jhm.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite, alpha=0.9)
    ctx.add_basemap(ax2, crs=gdf_jhm.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite, alpha=0.9)
    if show_figure:
        plt.show()
    if fig_location is not None:
        fig.savefig(fig_location)

    plt.close(fig)


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):

    gdf_jhm = gdf[gdf["region"] == "JHM"].to_crs("epsg:3857")

    coords = np.dstack([gdf_jhm.geometry.x, gdf_jhm.geometry.y]).reshape(-1, 2)

    db = sklearn.cluster.MiniBatchKMeans(n_clusters=20).fit(coords)

    gdf_c = gdf_jhm.copy()

    gdf_c["cluster"] = db.labels_

    gdf_c = gdf_c.dissolve(by="cluster", aggfunc={"region": "count"})
    gdf_c = gdf_c.rename(columns=dict(region="cnt"))

    gdf_coords = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(
                                        db.cluster_centers_[:, 0],
                                        db.cluster_centers_[:, 1]))

    gdf_final = gdf_c.merge(gdf_coords, left_on="cluster",
                            right_index=True).set_geometry("geometry_y")

    fig, ax = plt.subplots(1, 1, figsize=(10, 6), constrained_layout=True)

    gdf_jhm.plot(ax=ax, markersize=1, color='#878787')

    gdf_final.plot(ax=ax, markersize=(gdf_final["cnt"]/5), column="cnt",
                   legend=True, alpha=0.6)

    ax.set_title("Nehody v JHM kraji", fontsize=13, pad=10)

    ctx.add_basemap(ax, crs=gdf_jhm.crs.to_string(),
                    source=ctx.providers.Stamen.TonerLite, alpha=0.9)

    plt.axis("off")

    if show_figure:
        plt.show()
    if fig_location is not None:
        fig.savefig(fig_location)

    plt.close(fig)


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
