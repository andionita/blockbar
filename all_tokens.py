'''
Represent the transfer history of all tokens as a graph
Outcome: Thickness graph
'''
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy

# Reading in data
INPUT_CSV='data/export-token-nft-0x9db475371b5cc2913d3219f72e16a3f101339a05_von_anfang_bis_20122022_concise.csv'
ADDRESS_FILE_CSV='data/Address_labels.csv'
IN_DEGREES_FILE='data/Out_degrees.csv'
OUT_DEGREES_FILE='data/In_degrees.csv'
all_tx = pd.read_csv(INPUT_CSV, sep=';')
# Limiting the number of transaction to the first 1000, otherwise the resulting graph is unreadable
#all_tx = all_tx[:5000]

# Relabeling Data
all_tx_copy = all_tx.copy()
all_tx_from = all_tx_copy.loc[:, ['From', 'UnixTimestamp']].rename(columns={'From':'Address'})
all_tx_to = all_tx_copy.loc[:, ['To', 'UnixTimestamp']].rename(columns={'To':'Address'})
addresses = pd.concat([all_tx_from, all_tx_to]).groupby('Address').agg('min').sort_values('UnixTimestamp', ascending=True).reset_index()
# Code reference: https://stackoverflow.com/questions/50860366/pandas-set-row-values-to-letter-of-the-alphabet-corresponding-to-index-number
node_labels = pd.Series(list(addresses.index.values), name='node_label')
address_labels = pd.concat([addresses, node_labels], axis=1).loc[:, ['Address', 'node_label']]
# save address labels to CSV file
#address_labels.to_csv(ADDRESS_FILE_CSV)
all_tx_labels = all_tx_copy.merge(address_labels, how='left', left_on='From', right_on='Address').rename(columns={'node_label':'From_node_label'})
all_tx_labels = all_tx_labels.merge(address_labels, how='left', left_on='To', right_on='Address').rename(columns={'node_label':'To_node_label'})
all_tx_labels.drop(columns=['Address_x', 'Address_y'], axis=1, inplace=True)
all_tx_labels_copy = all_tx_labels.copy()
edgelist = all_tx_labels_copy.drop(columns=['Txhash', 'UnixTimestamp', 'From', 'To', 'Token_ID', 'Method'])

# computing counts as edge weight
edgelist['count'] = 0
edgelist = edgelist.groupby(['From_node_label', 'To_node_label'])['count'].count().reset_index(name='count')
print('original no of rows: ' + str(len(edgelist)))

# filtering graph, removing edges with low edge weight, removing specific nodes outside of main connected component
edgelist = edgelist[edgelist['count'] > 5]
edgelist = edgelist[(edgelist['From_node_label'] != 1509) & (edgelist['From_node_label'] != 309) &
                    (edgelist['From_node_label'] != 1123) & (edgelist['From_node_label'] != 1913) &
                    (edgelist['From_node_label'] != 245)]
print('after filtering: ' + str(len(edgelist)))

# using log scala for counts
edgelist['count'] = edgelist['count'].apply(lambda x: float(numpy.math.log(1 + x, 5)))

# constructing graph and rendering it
dg = nx.from_pandas_edgelist(
    df=edgelist,
    source='From_node_label',
    target='To_node_label',
    edge_attr='count',
    create_using=nx.Graph()
    #create_using = nx.DiGraph()
)

edges = dg.edges()
counts = [dg[u][v]['count'] for u,v in edges]

pos = nx.spring_layout(dg)
#pos = nx.nx_agraph.graphviz_layout(dg)
nx.draw_networkx(dg, pos, width=counts,
                 node_size=800,
                 connectionstyle='arc3, rad = 0.05',
                 arrowsize=15)

plt.show()
