from pygraphviz import *
import pprint, utils

def classify_player1_node(action_set):
    """
    Determines label and color for player1 nodes
    Returns tuple (label, color)
    """

    look = action_set['look']
    high = action_set['high']
    low = action_set['low']

    if not look and high == 'cooperate':
        return ('CWOL', 'green')
    elif not look and high == 'defect':
        return ('DWOL', 'red')
    elif look and high == 'cooperate' and low == 'cooperate':
        return ('CWL', 'blue')
    elif look and high == 'defect' and low == 'defect':
        return ('DWL', 'red')
    elif look and high == 'defect' and low == 'cooperate':
        return ('look, high -> defect \\n low -> cooperate', 'purple')
    elif look and high == 'cooperate' and low == 'defect':
        return ('look, high -> cooperate \\n low -> defect', 'violet')


def classify_player2_node(action_set):
    """
    Determines label and color for player2 nodes
    Returns tuple (label, color)
    """

    action = action_set['action']
    if action == 'continue':
        return ('continue', 'green')
    elif action == 'exit':
        return ('exit', 'red')


def get_player2_action(state):
    return state.action_set['action']



def build_player2_graph(player2, graph, state=None):
    """
    Traverses player2 state graph recursively
    """

    if state is None:
        state = player2.states[player2.initial_state]

    key = 0

    classification = classify_player2_node(state.action_set)

    if state.id == player2.initial_state:
        label = 'initial\\n{}'.format(classification[0])
    else:
        label = '{}'.format(classification[0])

    fontcolor = 'white' if classification[1] == 'blue' else 'black'
    graph.add_node(state.id, label=label, fillcolor=classification[1], fontcolor=fontcolor)

    if state.action_set['action'] != 'exit' or state.id == player2.initial_state:

        edges = utils.get_player2_edges(state)

        for edge in edges:
            if edge['destination'] not in graph.nodes():
                build_player2_graph(player2, graph, player2.states[edge['destination']])

            graph.add_edge(state.id, edge['destination'], color=edge['color'], label=edge['label'], key=state.id + str(key))
            key += 1



def graph_player2(player2, outfile='player2.png', classification=None):
    if not classification:
        classification = 'Unclassified'

    # setup
    graph = AGraph(layout='dot', directed=True, rankdir='LR', strict=False, label=classification)
    graph.node_attr['style']='filled'

    build_player2_graph(player2, graph)
    graph.draw(outfile, prog='neato')


def build_player1_graph(player1, graph, state=None):
    """
    Traverses player1 state graph recursively
    """

    if state is None:
        state = player1.states[player1.initial_state]


    next_state = state.strategy_set['next']
    classification = classify_player1_node(state.action_set)

    if state.id == player1.initial_state:
        label = 'initial\\n{}'.format(classification[0])
    else:
        label = '{}'.format(classification[0])

    fontcolor = 'white' if classification[1] == 'blue' else 'black'
    graph.add_node(state.id, label=label, fontcolor=fontcolor, fillcolor=classification[1])

    if next_state not in graph.nodes():
        build_player1_graph(player1, graph, player1.states[next_state])

    graph.add_edge(state.id, next_state)


def graph_player1(player1, outfile='player2.png', classification=None):
    if not classification:
        classification = 'Unclassified'
    # setup
    graph = AGraph(layout='dot', directed=True, rankdir='LR', strict=True, label=classification)
    graph.node_attr['style']='filled'

    build_player1_graph(player1, graph)

    graph.draw(outfile, prog='neato')

