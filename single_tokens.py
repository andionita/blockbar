'''
Represent the transfer history of single tokens as directed graphs
Outcome: graphs with loops
'''
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Reading in data
all_tx = pd.read_csv('data/export-token-nft-0x9db475371b5cc2913d3219f72e16a3f101339a05_von_anfang_bis_20122022_concise.csv',
                sep=';')

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

# setting up matplotlib figure
fig, axes = plt.subplots(nrows=2, ncols=2)
ax = axes.flatten()

# setting token ids to display, creating subgraphs for the token ids, displaying graphs in subplots
#token_ids = all_tx_copy['Token_ID'].unique()
# token in loops
#token_ids = [287, 392, 395, 501]
#token_ids = [533, 561, 592, 610]
token_ids = [612, 654, 669, 703]
#token_ids = [669, 703, 1454, 5650]
# token in sales
#token_ids = [5131]
for i in range(0, len(token_ids)):
    all_tx_labels_token = all_tx_labels[all_tx_labels['Token_ID'] == token_ids[i]]
    #all_tx_labels_token = all_tx_labels[all_tx_labels['Token_ID'] == 287]
    print("edges count = " + str(len(all_tx_labels_token)))
    #if len(all_tx_labels_token) < 6:
    #    continue
    print(all_tx_labels_token.loc[:, ['From_node_label', 'To_node_label', 'Token_ID']])
    DG = nx.from_pandas_edgelist(
        df=all_tx_labels_token,
        source='From_node_label',
        target='To_node_label',
        edge_attr='Token_ID',
        create_using=nx.DiGraph()
    )
    pos = nx.spring_layout(DG)
    nx.draw_networkx(DG, pos,
                    ax=ax[i],
                    connectionstyle='arc3, rad = 0.20', node_size=1200, arrowsize=25, width=1.5)
    nx.draw_networkx_edge_labels(
        DG,
        pos=pos,
        ax=ax[i],
        edge_labels=nx.get_edge_attributes(DG,'Token_ID'), font_size=16
        )
    ax[i].set_axis_off()
plt.show()
