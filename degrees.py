'''
Computes out-degree and in-degree distribution

Input: etherscan CSV file (concise)
Outcome: distribution curve (on log scales or with zoom-in on bending point)
'''
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# read in data
INPUT_CSV='data/export-token-nft-0x9db475371b5cc2913d3219f72e16a3f101339a05_von_anfang_bis_20122022_concise.csv'
all_tx = pd.read_csv(INPUT_CSV, sep=';')

# Relabeling data
all_tx_copy = all_tx.copy()
all_tx_from = all_tx_copy.loc[:, ['From', 'UnixTimestamp']].rename(columns={'From':'Address'})
all_tx_to = all_tx_copy.loc[:, ['To', 'UnixTimestamp']].rename(columns={'To':'Address'})
addresses = pd.concat([all_tx_from, all_tx_to]).groupby('Address').agg('min').sort_values('UnixTimestamp', ascending=True).reset_index()
# Code reference: https://stackoverflow.com/questions/50860366/pandas-set-row-values-to-letter-of-the-alphabet-corresponding-to-index-number
node_labels = pd.Series(list(addresses.index.values), name='node_label')
address_labels = pd.concat([addresses, node_labels], axis=1).loc[:, ['Address', 'node_label']]
all_tx_labels = all_tx_copy.merge(address_labels, how='left', left_on='From', right_on='Address').rename(columns={'node_label':'From_node_label'})
all_tx_labels = all_tx_labels.merge(address_labels, how='left', left_on='To', right_on='Address').rename(columns={'node_label':'To_node_label'})
all_tx_labels.drop(columns=['Address_x', 'Address_y'], axis=1, inplace=True)
from_label_map = dict(zip(all_tx_labels['From_node_label'], all_tx_labels['From']))
to_label_map = dict(zip(all_tx_labels['To_node_label'], all_tx_labels['To']))

DG = nx.from_pandas_edgelist(
    df=all_tx_labels,
    source='From_node_label',
    target='To_node_label',
    edge_attr='Token_ID',
    create_using=nx.DiGraph()
)

degrees = sorted((d for n, d in DG.out_degree()), reverse=True)
#degrees = sorted((d for n, d in DG.in_degree()), reverse=True)

fig, ax = plt.subplots(figsize=[5, 4])
ax.plot(*np.unique(degrees, return_counts=True))
ax.set_title('Out-Degree Distribution')
#ax.set_title('In-Degree Distribution')
ax.set_xlabel('Out-Degree')
#ax.set_xlabel('In-Degree')
ax.set_ylabel('# of Nodes')
ax.set_yscale('log')
ax.set_xscale('log')

# alternative rendering with zoom-in on bending point
#axins = ax.inset_axes([0.5, 0.5, 0.47, 0.47])
#axins.plot(*np.unique(degrees, return_counts=True))
#x1, x2, y1, y2 = 0, 120, 0, 120
#axins.set_xlim(x1, x2)
#axins.set_ylim(y1, y2)
#ax.indicate_inset_zoom(axins, edgecolor='black')

plt.show()
