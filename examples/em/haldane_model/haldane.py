#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.05.2015 00:12:05 CEST
# File:    haldane.py

import z2pack
import numpy as np

# defining pauli matrices
identity = np.identity(2, dtype=complex)
pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)


def Hamilton(k, m, t1, t2, phi):
    k_a = 2 * np.pi / 3. * np.array([-k[0] - k[1], 2. * k[0] - k[1], - k[0] + 2. * k[1]])
    k_b = 2 * np.pi * np.array([k[0], k[1], k[0] - k[1]])
    H = 2 * t2 * np.cos(phi) * sum([np.cos(-val) for val in k_b]) * identity
    H += t1 * sum([np.cos(-val) for val in k_a]) * pauli_x
    H += t1 * sum([np.sin(-val) for val in k_a]) * pauli_y
    H += m * pauli_z
    H -= 2 * t2 * np.sin(phi) * sum([np.sin(-val) for val in k_b]) * pauli_z
    return H

def get_chern(m, t1, t2, phi):
    system = z2pack.em.System(lambda k: Hamilton(k, m, t1, t2, phi), occ=1)
    surface = system.surface(lambda s, t: [t, s, 0.], pickle_file=None)
    surface.wcc_calc(verbose=False)
    return surface.chern()['chern']

if __name__ == "__main__":
    print(get_chern(0.5, 1., 1. / 3., 0.5 * np.pi))
    print(get_chern(0.5, 1., 1. / 3., -0.5 * np.pi))

    
    