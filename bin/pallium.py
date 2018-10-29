import numpy as np
import os
from scanorama import *
from scipy.sparse import vstack

from process import load_names
from experiments import *
from utils import *

NAMESPACE = 'pallium'
METHOD = 'svd'
DIMRED = 100

data_names = [
    'data/murine_atlases/neuron_1M/neuron_1M',
]

if __name__ == '__main__':
    if not os.path.isfile('data/dimred/{}.txt'.format(NAMESPACE)):
        datasets, genes_list, n_cells = load_names(data_names)
        datasets, genes = merge_datasets(datasets, genes_list)

        log('Dimension reduction with {}...'.format(METHOD))
        X = vstack(datasets)
        X_dimred = reduce_dimensionality(X, method=METHOD, dimred=DIMRED)
        if METHOD == 'jl_sparse':
            X_dimred = X_dimred.toarray()
        log('Dimensionality = {}'.format(X_dimred.shape[1]))
        np.savetxt('data/dimred/{}.txt'.format(NAMESPACE), X_dimred)
    else:
        X_dimred = np.loadtxt('data/dimred/{}.txt'.format(NAMESPACE))

    viz_genes = [
        'Gja1', 'Flt1', 'Gabra6', 'Syt1', 'Gabrb2', 'Gabra1',
        'Meg3', 'Mbp', 'Rgs5', 'Pcp2', 'Dcn', 'Pvalb', 'Nnat',
        'C1qb', 'Acta2', 'Syt6', 'Lhx1', 'Sox4', 'Tshz2', 'Cplx3',
        'Shisa8', 'Fibcd1', 'Drd1', 'Otof', 'Chat', 'Th', 'Rora',
        'Synpr', 'Cacng4', 'Ttr', 'Gpr37', 'C1ql3', 'Fezf2',
    ]

    cell_labels = (
        open('data/cell_labels/pallium.txt')
        .read().rstrip().split('\n')
    )
    le = LabelEncoder().fit(cell_labels)
    cell_labels = le.transform(cell_labels)
    
    balance(X_dimred, NAMESPACE, cell_labels)

    exit()
    
    experiment_gs(X_dimred, NAMESPACE,
                  gene_names=viz_genes, genes=genes,
                  gene_expr=vstack(datasets),
                  visualize_orig=False,
                  kmeans=False)
    
    log('Done.')
