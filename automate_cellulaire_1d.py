import numpy as np
import time
import matplotlib.pyplot as plt
import sys
from mpi4py import MPI

nombre_cas   : int = 256
nb_cellules  : int = 360  # Cellules fantomes
nb_iterations: int = 360

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


local_compute_time = 0.
local_display_time = 0.

def save_as_md(cells, symbols='⬜⬛'):
    res = np.empty(shape=cells.shape, dtype='<U')
    res[cells==0] = symbols[0]
    res[cells==1] = symbols[1]
    np.savetxt(f'resultat_{num_config:03d}.md', res, fmt='%s', delimiter='', header=f'Config #{num_config}', encoding='utf-8')

def save_as_png(cells):
    fig = plt.figure(figsize=(nb_iterations/10., nb_cellules/10.))
    ax = plt.axes()
    ax.set_axis_off()
    ax.imshow(cells[:, 1:-1], interpolation='none', cmap='RdPu')
    plt.savefig(f"resultat_{num_config:03d}.png", dpi=100, bbox_inches='tight')
    plt.close()


local_cas = nombre_cas//size

for num_config in range(rank*local_cas, (rank+1)*local_cas):
    local_t1 = time.time()
    local_cells = np.zeros((nb_iterations, nb_cellules+2), dtype=np.int16)
    local_cells[0, (nb_cellules+2)//2] = 1
    for iter in range(1, nb_iterations):
        vals = np.left_shift(1, 4*local_cells[iter-1, 0:-2]
                             + 2*local_cells[iter-1, 1:-1]
                             + local_cells[iter-1, 2:])
        local_cells[iter, 1:-1] = np.logical_and(np.bitwise_and(vals, num_config), 1)
    local_t2 = time.time()
    local_compute_time += local_t2 - local_t1



    t1 = time.time()
    save_as_md(local_cells)
    #save_as_png(cells)
    t2 = time.time()
    local_display_time += t2 - t1




compute_time = comm.reduce(local_compute_time,op=MPI.MAX, root=0)
display_time = comm.reduce(local_display_time,op=MPI.MAX, root = 0)

if rank == 0 :
    print(f"Temps calcul des generations de cellules : {compute_time:.6g}")
    print(f"Temps d'affichage des resultats : {display_time:.6g}")

MPI.Finalize()