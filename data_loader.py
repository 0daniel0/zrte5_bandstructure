#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pickle

# ## Az ábrákhoz szükséges adatok betöltése

ROOT_PATH = "/var/www/ami-kell/data/"
ROOT_PATH = "data/"


def get_path(root, i):
    return root + "/stress0-" + str(i) + ".pickle"


def get_short_path(root, i):
    return root + "/stress" + str(i) + ".pickle"


def get_bands(path):
    with open(path, 'rb') as handle:
        b = pickle.load(handle)
    [eigh, lk, kt, kl] = b
    return eigh, lk, kt, kl


def get_data(root, n=25):
    """
    root: folder, containing pickle files, loads data, returns tgap, data, path_list
    """
    tgap = []
    data = []
    path_list = []
    for i in range(n):
        path = get_path(root, i)
        try:
            [eigh, lk, kt, kl] = get_bands(path)
            #             make the labels html compatible
            for j, klj in enumerate(kl):
                if klj == '$\\Gamma$':
                    kl[j] = '\u0393'
                if klj == '$X_1$':
                    kl[j] = 'X<sub>1</sub>'
                if klj == '$A_1$':
                    kl[j] = 'A<sub>1</sub>'
            datai = [eigh, lk, kt, kl]
            data.append(datai)
            #             feat = (eigh[:, 68] - eigh[:, 67]).min()
            #             gap = eigh[:, 68].min() - eigh[:, 67].max()
            gap = eigh[:, 2].min() - eigh[:, 1].max()
        except FileNotFoundError:
            try:
                path = get_short_path(root, i)
                [eigh, lk, kt, kl] = get_bands(path)
                #             make the labels html compatible
                for j, kli in enumerate(kl):
                    if kli == '$\\Gamma$':
                        kl[j] = '\u0393'
                    if kli == '$X_1$':
                        kl[j] = 'X<sub>1</sub>'
                    if kli == '$A_1$':
                        kl[j] = 'A<sub>1</sub>'
                datai = [eigh, lk, kt, kl]
                data.append(datai)
                #             feat = (eigh[:, 68] - eigh[:, 67]).min()
                #             gap = eigh[:, 68].min() - eigh[:, 67].max()
                gap = eigh[:, 2].min() - eigh[:, 1].max()
            except FileNotFoundError:
                print(root, i, "Notfound")
                gap = np.NaN
                # feat = np.NaN
                data.append([[], [], [], []])
        path_list.append(path)
        tgap.append(gap)
    tgap = np.array(tgap)
    tgap[tgap < 0] = 0
    return list(1000 * tgap), data, path_list


def get_stress(root, i):
    # xx/zz only
    if root.find("only") != -1:
        n = 11
        delta = np.round(np.linspace(-0.05, 0.05, n, endpoint=True), 3)
        delta = list(delta)
        delta.append(0.1)
        delta.append(-0.1)
        return delta[i]

    # xx/zz 1
    if root.find("1") != -1:
        n = 11
        delta = np.round(np.linspace(-0.01, 0.01, n, endpoint=True), 3)
        delta = list(delta)
        del delta[5]
        del delta[0], delta[-1]
        delta.append(0.015)
        delta.append(-0.015)
        return delta[i]

    # xx/zz 2
    if root.find("2") != -1:
        n = 11
        delta = np.round(np.linspace(-2, -1, n, endpoint=True) / 100, 3)
        delta = list(delta)
        del delta[-1]
        delta += list(-np.array(delta))
        return delta[i]

    else:
        raise FileNotFoundError("Not found: " + root)


def get_strain_datas():
    root = ROOT_PATH + "line_graphs/"
    xxonly = root + "xxonly"
    zzonly = root + "zzonly"
    xx1 = root + "xx1"
    zz1 = root + "zz1"
    xx2 = root + "xx2"
    zz2 = root + "zz2"

    xx, dxx, pathxx = get_data(xxonly, n=13)
    zz, dzz, pathzz = get_data(zzonly, n=13)
    xx1, dxx1, pathxx1 = get_data(xx1, n=10)
    zz1, dzz1, pathzz1 = get_data(zz1, n=10)
    xx2, dxx2, pathxx2 = get_data(xx2, n=20)
    zz2, dzz2, pathzz2 = get_data(zz2, n=20)

    x = xx + xx1 + xx2
    z = zz + zz1 + zz2
    pathx = pathxx + pathxx1 + pathxx2
    pathz = pathzz + pathzz1 + pathzz2
    datax = dxx + dxx1 + dxx2
    dataz = dzz + dzz1 + dzz2

    x = np.array(x)
    z = np.array(z)
    datax = np.array(datax, dtype=object)
    dataz = np.array(dataz, dtype=object)
    pathx = np.array(pathx, dtype=object)
    pathz = np.array(pathz, dtype=object)

    d = []

    # xx/zz only
    n = 11
    delta = np.round(np.linspace(-0.05, 0.05, n, endpoint=True), 3)
    delta = list(delta)
    delta.append(0.1)
    delta.append(-0.1)

    d += delta

    # xx/zz 1
    n = 11
    delta = np.round(np.linspace(-0.01, 0.01, n, endpoint=True), 3)
    delta = list(delta)
    del delta[5]
    del delta[0], delta[-1]
    delta.append(0.015)
    delta.append(-0.015)

    d += delta

    # xx/zz 2
    n = 11
    delta = np.round(np.linspace(-2, -1, n, endpoint=True) / 100, 3)
    delta = list(delta)
    del delta[-1]
    delta += list(-np.array(delta))

    d += delta
    d = np.array(d)
    idx = np.argsort(d)
    return 100 * d[idx], x[idx], z[idx], datax[idx], dataz[idx], pathx[idx], pathz[idx]


def load_data(row, col, bandp, posp):
    ext = ".txt"
    gap = np.empty((row, col), dtype=float)
    gap[:] = np.NaN
    x = np.empty((row, col), dtype=float)
    y = np.empty((row, col), dtype=float)
    z = np.empty((row, col), dtype=float)

    for i in range(row):
        for j in range(col):
            try:
                path = bandp + str(i) + "-" + str(j) + ext
                gap[i, j] = np.loadtxt(path)
            except FileNotFoundError:
                pass
            #                 print(path)
            try:
                path = posp + str(i) + "-" + str(j) + ext
                a, b, c = np.loadtxt(path)
                x[i, j] = a
                y[i, j] = b
                z[i, j] = c
            except FileNotFoundError:
                pass
    #                 print(path)

    return [gap.T.flatten(), x.flatten(), y.flatten(), z.flatten()]


def load_data2(row, col, bandp):
    ext = ".txt"
    gap = np.empty((row, col), dtype=float)
    gap[:] = np.NaN
    for i in range(row):
        for j in range(col):
            try:
                path = bandp + str(i) + "-" + str(j) + ext
                gap[i, j] = np.loadtxt(path)
            except FileNotFoundError:
                pass
    #             print(path)

    return gap.T.flatten()


def get_phase_data():
    bandp = ROOT_PATH + "featmin/data"
    feat = load_data2(row=20, col=20, bandp=bandp)

    bandp = ROOT_PATH + "gapmin/data"
    posp = ROOT_PATH + "pos_data/article_grid_stress"
    gap, x, y, z = load_data(row=20, col=20, bandp=bandp, posp=posp)
    gap[gap < 0] = 0
    x = (x / 2.002504813 - 1) * 100
    y = (y / 7.194483612 - 1) * 100
    z = (z / 13.869471954 - 1) * 100
    topgap = 1000 * gap
    mask = (y + 2 * x - 6) < 0
    topgap[mask] *= -1
    return topgap, gap, feat, x, y, z


def load_bands_data(i, j):
    """loads single band data"""
    root = ROOT_PATH + "article_grid/"
    path = root + "stress{}-{}.pickle".format(i, j)
    with open(path, "rb") as f:
        data = pickle.load(f)

    eigh, lk, kt, kl = data
    for i, kli in enumerate(kl):
        if kli == '$\\Gamma$':
            kl[i] = '\u0393'
        if kli == '$X_1$':
            kl[i] = 'X<sub>1</sub>'
        if kli == '$A_1$':
            kl[i] = 'A<sub>1</sub>'
    data = (eigh, lk, kt, kl)
    return data


def load_all_bands_data():
    """loads all bands data"""

    band_data_cont_inner = {}
    for i in range(20):
        for j in range(20):
            try:
                band_data_cont_inner[str(i) + "-" + str(j)] = load_bands_data(i, j)
            except FileNotFoundError:
                band_data_cont_inner[str(i) + "-" + str(j)] = load_bands_data(i - 1, j)
    return band_data_cont_inner


def get_bands_data(i, j):
    """uses single band data"""
    return band_data_cont[str(i) + "-" + str(j)]


band_data_cont = load_all_bands_data()  # phase figure's bandstructure
