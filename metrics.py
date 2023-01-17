'''
Computing various metrics for the tokens transfer transactions:
- out- and in-degrees
- number of sellers and buyers
- happy path in the graph of token transfers
- loops in the token transfer graph
- token retention time
'''
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy

# read in data
INPUT_CSV='data/export-token-nft-0x9db475371b5cc2913d3219f72e16a3f101339a05_von_anfang_bis_20122022_concise.csv'
all_tx = pd.read_csv(INPUT_CSV, sep=';')
#all_tx = all_tx[:1000]

# Relabelling data
all_tx_copy = all_tx.copy()
all_tx_from = all_tx_copy.loc[:, ['From', 'UnixTimestamp']].rename(columns={'From':'Address'})
all_tx_to = all_tx_copy.loc[:, ['To', 'UnixTimestamp']].rename(columns={'To':'Address'})
addresses = pd.concat([all_tx_from, all_tx_to]).groupby('Address').agg('min').sort_values('UnixTimestamp', ascending=True).reset_index()
# https://stackoverflow.com/questions/50860366/pandas-set-row-values-to-letter-of-the-alphabet-corresponding-to-index-number
# index to upper letter
node_labels = pd.Series(list(addresses.index.values), name='node_label')
address_labels = pd.concat([addresses, node_labels], axis=1).loc[:, ['Address', 'node_label']]
# save address labels to CSV file
#address_labels.to_csv(ADDRESS_FILE_CSV)
all_tx_labels = all_tx_copy.merge(address_labels, how='left', left_on='From', right_on='Address').rename(columns={'node_label':'From_node_label'})
all_tx_labels = all_tx_labels.merge(address_labels, how='left', left_on='To', right_on='Address').rename(columns={'node_label':'To_node_label'})
all_tx_labels.drop(columns=['Address_x', 'Address_y'], axis=1, inplace=True)

# Computing Out- and In- Degrees
token_ids = all_tx_copy['Token_ID'].unique()
DG = nx.from_pandas_edgelist(
    df=all_tx_labels,
    source='From_node_label',
    target='To_node_label',
    edge_attr='Token_ID',
    create_using=nx.MultiDiGraph()
)

print("---------------------")
out_degrees = DG.out_degree(node_labels.tolist())
out_degrees = sorted(out_degrees, key=lambda element: element[1], reverse=True)
print("Out degrees:")
print(out_degrees)
#pd.DataFrame.from_dict(out_degrees).to_csv(OUT_DEGREES_FILE)

in_degrees = DG.in_degree(node_labels.tolist())
in_degrees = sorted(in_degrees, key=lambda element: element[1], reverse=True)
print("In degrees:")
print(in_degrees)
#pd.DataFrame.from_dict(in_degrees).to_csv(IN_DEGREES_FILE)

# Sellers : Buyers
print("-----------------------------")
from_nodes = all_tx_labels['From_node_label'].unique()
to_nodes = all_tx_labels['To_node_label'].unique()
only_sellers = set(from_nodes).difference(set(to_nodes))
only_buyers = set(to_nodes).difference(set(from_nodes))
all_nodes = set(from_nodes).union(to_nodes)
print("Total nodes count: " + str(len(all_nodes)))
print("Total Sellers count: " + str(len(from_nodes)) + " (" + str(round(100 * len(from_nodes) / len(all_nodes), 2)) + "%)")
print("Only Sellers count: " + str(len(only_sellers)) + " (" + str(round(100 * len(only_sellers) / len(all_nodes), 2)) + "%)")
print("Total Buyers count " + str(len(to_nodes)) + " (" + str(round(100 * len(to_nodes) / len(all_nodes), 2)) + "%)")
print("Only Buyers count: " + str(len(only_buyers)) + " (" + str(round(100 * len(only_buyers) / len(all_nodes), 2)) + "%)")
print("-----------------------------")

# Happy Path
# computer counts = edge weigths
all_tx_labels_copy = all_tx_labels.copy()
edgelist = all_tx_labels_copy.drop(columns=['Txhash', 'UnixTimestamp', 'From', 'To', 'Token_ID', 'Method'])
edgelist['count'] = 0
edgelist = edgelist.groupby(['From_node_label', 'To_node_label'])['count'].count().reset_index(name='count')
edgelist = edgelist.sort_values(['From_node_label', 'count'], ascending=[True, False])
# build happy bath
happypath = pd.DataFrame(columns=['From_node_label', 'To_node_label', 'count'])
current_node = 0
happy_nodes = [0]
while True:
    if len(edgelist[edgelist.From_node_label == current_node]) > 0:
        row = edgelist[edgelist.From_node_label == current_node].iloc[0]
    else:
        break
    happypath = happypath.append(row)
    current_node = row['To_node_label']
    happy_nodes.append(current_node)
# draw graph
#print('happy nodes')
#print(happy_nodes)
#print('address labels')
#print(address_labels[address_labels.node_label.isin(happy_nodes)].Address.values.tolist())
happy_dict = {}
for node in happy_nodes:
    happy_dict[node] = address_labels[address_labels.node_label == node].Address.values.tolist()[0]
print('happy dict')
print(happy_dict)
happy_labels = address_labels[address_labels.node_label.isin(happy_nodes)].Address.values.tolist()
dg = nx.from_pandas_edgelist(
        df=happypath,
        source='From_node_label',
        target='To_node_label',
        edge_attr='count',
        create_using=nx.DiGraph()
    )
pos = nx.spring_layout(dg)
nx.draw_networkx(dg, pos, node_size=800, labels=happy_dict)
#nx.draw_networkx_nodes(dg, pos, labels=)
nx.draw_networkx_edge_labels(dg, pos=pos, edge_labels=nx.get_edge_attributes(dg, 'count'))
plt.show()

# Detect loops
loopdf = all_tx_labels.copy()
loopdf = loopdf.drop(columns=['Txhash', 'UnixTimestamp', 'From', 'To', 'Method'])
loopdf['loop_count'] = 0
loopdf = loopdf.groupby(['To_node_label', 'Token_ID'])['loop_count'].count().reset_index(name='loop_count')
loopdf = loopdf[loopdf.loop_count > 1]
loopdf = loopdf.sort_values(['loop_count', 'Token_ID'], ascending=[False, True])
# print out nodes that are visited more times per token
print(loopdf)

# Computing Token retention time
token_ids = all_tx_labels['Token_ID'].unique()
avg_holdtime_per_token = 0
avg_holdtime_per_node = 0
skip_token = 0
for i in token_ids:
    tokendf = all_tx_labels[all_tx_labels.Token_ID == i].copy()
    tokendf = tokendf.drop(columns=['Txhash', 'From', 'To', 'Method'])
    tokendf['holdtime'] = tokendf['UnixTimestamp'] - tokendf['UnixTimestamp'].shift()
    avg_holdtime = tokendf.loc[:, 'holdtime'].mean()
    if not numpy.isnan(avg_holdtime):
        avg_holdtime_per_token += avg_holdtime
    else:
        skip_token += 1
    avg_holdtime_per_node += tokendf.loc[:, 'holdtime'].sum()
avg_holdtime_per_token /= (len(token_ids) - skip_token)
avg_holdtime_per_node /= (len(all_tx_labels) - len(token_ids))
print('Average holding time per token = ' + str(round(avg_holdtime_per_token, 2)) + " sec")
print('Average holding time per node = ' + str(round(avg_holdtime_per_node, 2)) + " sec")