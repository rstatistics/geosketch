import numpy as np
import os
from scanorama import *
from scipy.sparse import vstack
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import normalize, LabelEncoder

from experiments import *
from process import load_names
from utils import *

np.random.seed(0)

NAMESPACE = 'mouse_brain'
METHOD = 'svd'
DIMRED = 100

data_names = [
    'data/mouse_brain/dropviz/Cerebellum_ALT',
    'data/mouse_brain/dropviz/Cortex_noRep5_FRONTALonly',
    'data/mouse_brain/dropviz/Cortex_noRep5_POSTERIORonly',
    'data/mouse_brain/dropviz/EntoPeduncular',
    'data/mouse_brain/dropviz/GlobusPallidus',
    'data/mouse_brain/dropviz/Hippocampus',
    'data/mouse_brain/dropviz/Striatum',
    'data/mouse_brain/dropviz/SubstantiaNigra',
    'data/mouse_brain/dropviz/Thalamus',
]

def keep_valid(datasets):
    n_valid = 0
    qc_idx = []
    for i in range(len(datasets)):
        
        valid_idx = []
        with open('{}/meta.txt'.format(data_names[i])) as f:
            
            n_lines = 0
            for j, line in enumerate(f):
                
                fields = line.rstrip().split()
                if fields[1] != 'NA':
                    valid_idx.append(j)
                    if fields[3] != 'doublet' and \
                       fields[3] != 'outlier':
                        qc_idx.append(n_valid)
                    n_valid += 1
                n_lines += 1

        assert(n_lines == datasets[i].shape[0])
        assert(len(qc_idx) <= n_valid)

        datasets[i] = datasets[i][valid_idx, :]
        print('{} has {} valid cells'
              .format(data_names[i], len(valid_idx)))

    print('Found {} cells among all datasets'.format(n_valid))
    print('Found {} valid cells among all datasets'.format(len(qc_idx)))
    
    return qc_idx
    
if __name__ == '__main__':
    datasets, genes_list, n_cells = load_names(data_names, norm=False)
    qc_idx = keep_valid(datasets)
    datasets, genes = merge_datasets(datasets, genes_list)
    X = vstack(datasets)

    if not os.path.isfile('data/dimred/{}_{}.txt'.format(METHOD, NAMESPACE)):
        log('Dimension reduction with {}...'.format(METHOD))
        X_dimred = reduce_dimensionality(
            normalize(X), method=METHOD, dimred=DIMRED
        )
        log('Dimensionality = {}'.format(X_dimred.shape[1]))
        np.savetxt('data/dimred/{}_{}.txt'.format(METHOD, NAMESPACE), X_dimred)
    else:
        X_dimred = np.loadtxt('data/dimred/{}_{}.txt'.format(METHOD, NAMESPACE))
        
    X = X[qc_idx]
    X_dimred = X_dimred[qc_idx]
    
    viz_genes = [
        'Gja1', 'Flt1', 'Gabra6', 'Syt1', 'Gabrb2', 'Gabra1',
        'Meg3', 'Mbp', 'Rgs5', 'Pcp2', 'Dcn', 'Pvalb', 'Nnat',
        'C1qb', 'Acta2', 'Syt6', 'Lhx1', 'Sox4', 'Tshz2', 'Cplx3',
        'Shisa8', 'Fibcd1', 'Drd1', 'Otof', 'Chat', 'Th', 'Rora',
        'Synpr', 'Cacng4', 'Ttr', 'Gpr37', 'C1ql3', 'Fezf2',
    ]

    labels = np.array(
        open('data/cell_labels/mouse_brain_cluster.txt')
        .read().rstrip().split('\n')
    )
    labels = labels[qc_idx]
    le = LabelEncoder().fit(labels)
    cell_names = sorted(set(labels))
    cell_labels = le.transform(labels)
    
    from ample import srs_center, srs_positive, srs_unit
    samp_idx = srs_center(X_dimred, 20000, replace=False)
    embedding = visualize(
        [ X_dimred[samp_idx, :] ], cell_labels[samp_idx],
        NAMESPACE + '_srs_center{}'.format(len(samp_idx)),
        [ str(ct) for ct in sorted(set(cell_labels)) ],
        perplexity=100, n_iter=500, image_suffix='.png',
    )
    samp_idx = srs_positive(X_dimred, 20000, replace=False)
    embedding = visualize(
        [ X_dimred[samp_idx, :] ], cell_labels[samp_idx],
        NAMESPACE + '_srs_positive{}'.format(len(samp_idx)),
        [ str(ct) for ct in sorted(set(cell_labels)) ],
        perplexity=100, n_iter=500, image_suffix='.png',
    )
    samp_idx = srs_unit(X_dimred, 20000, replace=False)
    embedding = visualize(
        [ X_dimred[samp_idx, :] ], cell_labels[samp_idx],
        NAMESPACE + '_srs_unit{}'.format(len(samp_idx)),
        [ str(ct) for ct in sorted(set(cell_labels)) ],
        perplexity=100, n_iter=500, image_suffix='.png',
    )
    exit()
    
    experiments(
        X_dimred, NAMESPACE, n_seeds=2,
        cell_labels=cell_labels,
        louvain_nmi=True, spectral_nmi=True,
        rare=True,
        rare_label=le.transform(['Macrophage'])[0],
    )
    exit()
    experiment_gs(
        X_dimred, NAMESPACE, cell_labels=cell_labels,
        #gene_names=viz_genes, genes=genes,
        #gene_expr=vstack(datasets),
        N_only=20000, kmeans=False, visualize_orig=False
    )
    experiment_uni(
        X_dimred, NAMESPACE, cell_labels=cell_labels,
        #gene_names=viz_genes, genes=genes,
        #gene_expr=vstack(datasets),
        N_only=20000, kmeans=False, visualize_orig=False
    )
    experiment_srs(
        X_dimred, NAMESPACE, cell_labels=cell_labels,
        #gene_names=viz_genes, genes=genes,
        #gene_expr=vstack(datasets),
        N_only=20000, kmeans=False, visualize_orig=False
    )
    experiment_kmeanspp(
        X_dimred, NAMESPACE, cell_labels=cell_labels,
        #gene_names=viz_genes, genes=genes,
        #gene_expr=vstack(datasets),
        N_only=20000, kmeans=False, visualize_orig=False
    )
    exit()
    
    from ample import gs
    samp_idx = gs(X_dimred, 1000, replace=False)
    save_sketch(X, samp_idx, genes, NAMESPACE + '1000')
    
    for scale in [ 10, 25, 100 ]:
        N = int(X.shape[0] / scale)
        samp_idx = gs(X_dimred, N, replace=False)
        save_sketch(X, samp_idx, genes, NAMESPACE + str(N))
    

    from differential_entropies import differential_entropies
    differential_entropies(X_dimred, labels)

    from ample import gs, uniform, srs
    samp_idx = srs(X_dimred, 20000, replace=False)
    report_cluster_counts(cell_labels[samp_idx])
    samp_idx = gs(X_dimred, 20000, replace=False)
    report_cluster_counts(cell_labels[samp_idx])
    embedding = visualize(
        [ X_dimred[samp_idx, :] ], cell_labels[samp_idx],
        NAMESPACE + '_geosketch{}'.format(len(samp_idx)),
        [ str(ct) for ct in sorted(set(cell_labels)) ],
        perplexity=100, n_iter=500, image_suffix='.png',
    )

