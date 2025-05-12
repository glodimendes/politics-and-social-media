import networkx as nx
import numpy as np
import itertools as it
import multiprocessing
import threading
import os

def calc_opinion_diversity(G: nx.Graph):
    opinion_count = {}
    for node in G.nodes():
        opinion = str(G.nodes[node]['opinion'])
        if opinion not in opinion_count:
            opinion_count[opinion] = 0
        opinion_count[opinion] += 1

    total_nodes = G.number_of_nodes()
    diversity_index = sum((count / total_nodes) ** 2 for count in opinion_count.values())
    return 1 - diversity_index

def kumulative_opinion_diversity(G: nx.Graph, it_counter:int, index_sum: list):
    return index_sum / it_counter


def init_opinions(G: nx.Graph, num_opinions: int = 2):
    # initialize the graph with random opinions
    for node in G.nodes():
        G.nodes[node]['opinion'] = np.random.randint(0, num_opinions)
    G.graph['diversity_index_sum'] = 0
    return G

def iterate_dispersion(G: nx.Graph, opinion_counter, r):
    for node in G.nodes():
        do_inovate = np.random.rand() < r
        if do_inovate:
            G.nodes[node]['next_opinion'] = next(opinion_counter)

        else:
            neighbors = list(G.neighbors(node))
            neighbors.append(node)  # include self in neighbors
            neighbor_opinions = [G.nodes[neigh]['opinion'] for neigh in neighbors]
            G.nodes[node]['next_opinion'] = np.random.choice(neighbor_opinions)
    for node in G.nodes():
        G.nodes[node]['opinion'] = G.nodes[node]['next_opinion']
    return G

def simulate_opinion_dispersion(G: nx.Graph, iterations: int = 100, num_opinions: int = 2, r: float = 0.05, cutoff_div_index: int = 50, verbose: bool = False):
    if verbose:
        print(f"[Thread] {threading.current_thread().name}")
        print(f"[Process] PID {multiprocessing.current_process().pid}")

    G = init_opinions(G, num_opinions)
    opinion_counter = it.count(num_opinions)
    for i in range(iterations):
        G = iterate_dispersion(G, opinion_counter, r)
        kum_diversity_index = 0
        if i > cutoff_div_index:
            diversity_index = calc_opinion_diversity(G)
            G.graph['diversity_index_sum'] += diversity_index
            kum_diversity_index = kumulative_opinion_diversity(G, (i+1)-cutoff_div_index, G.graph['diversity_index_sum'])
    return G, kum_diversity_index

def simulate_opinion_dispersion_parallel(source_dir, net, iterations, num_opinions, alpha, cutoff_div_index):

    data_path = os.path.join(source_dir, f"{net}.edge")
    G = nx.read_edgelist(data_path, nodetype=int, data=(("weight", float),))
    G = G.to_undirected()

    r = alpha / G.number_of_nodes()
    _, div_ind = simulate_opinion_dispersion(
        G, 
        iterations=iterations, 
        num_opinions=num_opinions,
        r=r,
        cutoff_div_index=cutoff_div_index,
        verbose=True
        )

    return div_ind