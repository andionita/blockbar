'''
Computes and displays Centrality measures:
- in-degree centrality
- out-degree centrality
- betweenness centrality
- closeness centrality
- in-degree
- out-degree
together with:
- the clustering coefficient
- average shortest path length
- strongest connected component

Input: etherscan CSV file (concise)
Outcome: Horizontal Bar-charts (centrality measures), values of other measures as stdout
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
label_map = dict(zip(all_tx_labels['From_node_label'], all_tx_labels['From']))
label_map.update(dict(zip(all_tx_labels['To_node_label'], all_tx_labels['To'])))

address_map={}
address_map['0x2eb8ce0db81af594db6a7817ce9c54efdba820d9']='monkey-shoulder.eth'
address_map['0xd65e80d7c0f8e2850d2f8269157fc2470b0be878']='johnnie-walker.eth'
address_map['0x8f2c56a49a9982ba33d0236d4d84fba1b1088561']='hennessy-cognac.eth'
address_map['0x8b62461f1f3120bdb0a26e1633cfd2f4e683b848']='dewars-scotch.eth'
address_map['0x8461bb0dc52bff2c1ca252fa216a95f6e470a73f']='royalsalutewhisky.eth'
address_map['0xc85b85aa1d6286b35b3dcb05d87621725f78067d']='penfoldswine.eth'
address_map['0xb820bddb311f0bdfdbc45885e4269bea9bdcdffc']='thedalmore.eth'
address_map['0xe56969d8a0b333b286f3023efbcd3c112216c4bf']='glenfiddichwhisky.eth'
address_map['0xcb6725e29947acc2edc2c70d87b5dadfef4c7b6e']='patrontequila.eth'
address_map['0xb839fd92cc51e1ad70602221e5a2d6a73e5babef']='redeem.blockbar.eth'
address_map['0x8b62461f1f3120bdb0a26e1633cfd2f4e683b848']='dewars-scotch.eth'
address_map['0xe56969d8a0b333b286f3023efbcd3c112216c4bf']='glenfiddichwhisky.eth'
address_map['0xd4734ce5102715924ffd44a41d7bb785ca2e6743']='shwaz.eth'
address_map['0xea94fa609015830e368a685a464a82c2ac20cacd']='onxy.eth'
address_map['0xace69a426da0857043938bc38701cb6c16feea04']='ardbegwhisky.eth'
address_map['0x86a41524cb61edd8b115a72ad9735f8068996688']='whalen.eth'

DG = nx.from_pandas_edgelist(
    df=all_tx_labels,
    source='From_node_label',
    target='To_node_label',
    edge_attr='Token_ID',
    #create_using=nx.MultiDiGraph()
    create_using=nx.DiGraph()
)

centralities = dict(sorted(nx.in_degree_centrality(DG).items(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(nx.out_degree_centrality(DG).items(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(nx.betweenness_centrality(DG).items(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(nx.closeness_centrality(DG).items(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(nx.clustering(DG).items(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(DG.in_degree(), key=lambda x:x[1], reverse=True))
#centralities = dict(sorted(DG.out_degree(), key=lambda x:x[1], reverse=True))
centralities_labels = [label_map[item] for item in list(centralities.keys())]
#print(centralities_labels[:10])
centralities_names = [address_map[item] if item in address_map else item for item in centralities_labels]

fig, ax = plt.subplots(figsize=[5,4])
ax.barh(list(reversed(centralities_names[:10])), list(reversed(list(centralities.values())[:10])))
ax.set_title('In-Degree Centrality')
#ax.set_title('Out-Degree Centrality')
#ax.set_title('Betweenness Centrality')
#ax.set_title('Closeness Centrality')
#ax.set_title('Clustering Coefficient')
#ax.set_title('In-Degree')
#ax.set_title('Out-Degree')
plt.subplots_adjust(left=0.23)
plt.show()

#print("Network diameter: " + str(nx.diameter(DG)))
print("Average shortest path length: " + str(nx.average_shortest_path_length(DG)))
print("Strongly connected component:")
print(max(nx.strongly_connected_components(DG), key=len))
