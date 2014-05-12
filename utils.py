import random, sys, math, fsm, copy, json, os, numpy

def classify_player2_edge(looked, temptation, move):
    """
    Determines label and color for player2 edges
    Returns tuple (label, color)
    """

    if not looked and temptation == 'high' and move == 'cooperate':
        return ('no look, cooperate, high', 'green')
    elif not looked and temptation == 'low' and move == 'cooperate':
        return ('no look, cooperate, low', 'green')
    elif not looked and temptation == 'high' and move == 'defect':
        return ('no look, defect, high', 'red')
    elif not looked and temptation == 'low' and move == 'defect':
        return ('no look, defect, low', 'red')
    elif looked and temptation == 'high' and move == 'cooperate':
        return ('look, cooperate, high', 'blue')
    elif looked and temptation == 'low' and move == 'cooperate':
        return ('look, cooperate, low', 'blue')
    elif looked and temptation == 'high' and move == 'defect':
        return ('look, defect, high', 'red')
    elif looked and temptation == 'low' and move == 'defect':
        return ('look, defect, low', 'red')


def get_player2_edges(state):
    """
    For visualization
    Gets edges ("arrows") for a particular Player 2 state
    """
    strategy_set = state.strategy_set
    edges = []
    strategies = []

    for look_nolook in ['looked', 'nolook']:
        for high_low in ['high', 'low']:
            for cooperate_defect in ['cooperate', 'defect']:
                destination = strategy_set[look_nolook][high_low][cooperate_defect]
                strategies.append((look_nolook == 'looked', high_low, cooperate_defect, destination))

    for strategy in strategies:
        classification = classify_player2_edge(strategy[0], strategy[1], strategy[2])
        edges.append({
            'label': classification[0],
            'color': classification[1],
            'destination': strategy[3]
        })

    return edges


def traverse_player1_tree(player1, nodes=None, state=None):
    """
    Traverses player1 state graph recursively
    """

    if state is None:
        state = player1.states[player1.initial_state]

    if nodes is None:
        nodes = []

    nodes.append(state.id)
    next_state = state.strategy_set['next']

    if next_state not in nodes:
        nodes = traverse_player1_tree(player1, nodes, player1.states[next_state])
    
    return nodes


def traverse_player2_tree(player2, nodes=None, state=None):
    """
    Traverses player2 state graph recursively, returning active state ids
    """
    if state is None:
        state = player2.states[player2.initial_state]
    
    if nodes is None:
        nodes = set()

    key = 0

    id = state.id

    nodes.add(id)

    if state.action_set['action'] != 'exit' or id == player2.initial_state:
        edges = get_player2_edges(state)

        for edge in edges:
            if edge['destination'] not in nodes:
                traverse_player2_tree(player2, nodes, player2.states[edge['destination']])
            key += 1

    return nodes


def random_id():
    return '%030x' % random.randrange(16**30)


def probability(prob):
    return random.random() <= prob


def score(payoffs, selection_strength, games):
    payoffs = float(payoffs)/games
    value = math.exp(payoffs * selection_strength)
    return value

def create_distribution(players, selection_strength, games):
    """
    Creates a distribution based on the relative scores of players
    """

    total_scores = sum([i.score(selection_strength, games) for i in players])
    for player in players:
        player.reproduction_probability = float(player.score(selection_strength, games))/total_scores

    dist = []
    for i, player in enumerate(players):
        if i == 0:
            dist.append((0, player.reproduction_probability, player))
        elif i == len(players) - 1:
            cumsum = dist[i-1][1]
            dist.append((cumsum, 1, player))
        else:
            cumsum = dist[i-1][1]
            dist.append((cumsum, cumsum + player.reproduction_probability, player))

    return dist



def determine_player(distribution, value):
    """
    Based on a distribution from create_distribution(), returns the winning that a value will map to
    Value is a float, 0 <= value <= 1
    """

    for num_range in distribution:
        lower_bound = num_range[0]
        upper_bound = num_range[1]
        player = num_range[2]
        if lower_bound == 0:
            if lower_bound <= value <= upper_bound:
                return player
        else:
            if lower_bound < value <= upper_bound:
                return player
    else:
        raise


def player_deep_copy(player):
    """
    Returns a deep copy of the inputted player (i.e., no element of the new player object refers to elements of the old player object)
    """
    states = {}
    for state_id in player.states:
        state = player.states[state_id]
        state_copy = fsm.State(strategy_set=copy.deepcopy(state.strategy_set), action_set=copy.deepcopy(state.action_set), id=state.id)
        states[state_copy.id] = state_copy

    if player.type == 1:
        return fsm.Player1(states=states, initial_state=player.initial_state)
    elif player.type == 2:
        return fsm.Player2(states=states, initial_state=player.initial_state)
    else:
        raise

def get_player1_state_num_by_id(id, states):
    """
    Searches Player 1 states and returns the number in the states list that corresponds to the given state id
    """
    for i, state in enumerate(states):
        if state.id == id:
            return i
    else:
        return None


def equal_strategies_player1(strategy1, strategy2):
    """
    Checks if two Player 1 objects are playing equivalent strategies
    Assumes that the strategies have already been reduced
    """
    if strategy1.type != strategy2.type or strategy1.type != 1:
        return False

    strat1_states = [strategy1.states[i] for i in traverse_player1_tree(strategy1)]
    strat2_states = [strategy2.states[i] for i in traverse_player1_tree(strategy2)]

    # check length
    if len(strat1_states) != len(strat2_states):
        return False

    # check states
    states = zip(strat1_states, strat2_states)
    for strat1_state, strat2_state in states:
        if strat1_state.action_set != strat2_state.action_set:
            return False

    # check arrows
    for strat1_state, strat2_state in states:
        if get_player1_state_num_by_id(strat1_state.id, strat1_states) != get_player1_state_num_by_id(strat2_state.id, strat2_states):
            return False

    return True


def equal_strategies_player2(strategy1, strategy2):
    """
    Checks if two Player 2 strategies are equivalent
    Can only check for equivalency of All C or All E
    """

    if strategy1.type != strategy2.type != 2:
        return False

    strat1_states = [strategy1.states[i] for i in traverse_player2_tree(strategy1)]
    strat2_states = [strategy2.states[i] for i in traverse_player2_tree(strategy2)]

    # check length
    if len(strat1_states) != len(strat2_states) or len(strat2_states) != 1:
        return False

    # check if all states the same
    states = zip(strat1_states, strat2_states)
    for strat1_state, strat2_state in states:
        if strat1_state.action_set != strat2_state.action_set:
            return False

    return True


def from_dict(player):
    """
    Creates a player object from a dictionary (for unfreezing states from JSON)
    """

    initial_state = player['initial_state']
    type = player['type']
    states = {}
    for state_id in player['states']:
        state = player['states'][state_id]
        id = state['id']
        strategy_set = state['strategy_set']
        action_set = state['action_set']

        states[state_id] = fsm.State(action_set=action_set, strategy_set=strategy_set, id=id)

    if type == 1:
        new_player = fsm.Player1(states=states, initial_state=initial_state)
    elif type == 2:
        new_player = fsm.Player2(states=states, initial_state=initial_state)

    return new_player



def unfreeze(file_prefix, gen=None):
    """
    Takes a directory (file_prefix, must have trailing slash), loads the generation specified, 
    and returns the player population and setup variables
    """
    if gen is None:
        suffix = ''
    else:
        suffix = '_{}'.format(gen)

    with open('{}player1_pop{}.json'.format(file_prefix, suffix), 'r') as infile:
        player1_pop = json.load(infile)
        player1_pop = [from_dict(player) for player in player1_pop]

    with open('{}player2_pop{}.json'.format(file_prefix, suffix), 'r') as infile:
        player2_pop = json.load(infile)
        player2_pop = [from_dict(player) for player in player2_pop]

    with open('{}setup_vars.json'.format(file_prefix), 'r') as infile:
        setup_vars = json.load(infile)

    return player1_pop, player2_pop, setup_vars


def unfreeze_bulk_stats(file_prefix):
    """
    Unfreezes trials in bulk and aggregates their cooperate/continue stats
    Use when averaging stats from a large number of trials with the same parameters
    Trial folders should be in the current directory scope, and named {file_prefix}-0/, {file_prefix-1}/, etc.
    trial_prefix should not have a trailing slash
    """
    dir = os.path.dirname('{}-final/test.txt'.format(file_prefix))
    if not os.path.exists(dir):
        os.makedirs(dir)

    i = 0
    nums = []
    while True:
        if os.path.isfile('{}-{}/player1_pop.json'.format(file_prefix, i)):
            nums.append(i)
            i += 1
        else:
            break

    player1_pops = []
    player2_pops = []
    stats_list = []
    cooperate_continue_stats = []
    cooperate_stats = []
    continue_stats = []
    cooperate_at_all_stats = []
    continue_at_all_stats = []

    for i in nums:
        with open('./{}-{}/cooperate_continue_stats.json'.format(file_prefix, i), 'r+') as infile:
            stats = json.load(infile)
            stats_list.append(stats)
    
    for stats in stats_list:
        for i, gen in enumerate(stats):
            if i >= len(cooperate_stats):
                cooperate_stats.append([])
                continue_stats.append([])
                cooperate_at_all_stats.append([])
                continue_at_all_stats.append([])

            cooperate_stats[i].append(gen['cooperate'])
            continue_stats[i].append(gen['continue'])
            cooperate_at_all_stats[i].append(gen['cooperate_at_all'])
            continue_at_all_stats[i].append(gen['continue_at_all'])

    for i in range(len(cooperate_stats)):
        cooperate_continue_stats_gen = {
            'cooperate': numpy.mean(cooperate_stats[i]),
            'continue': numpy.mean(continue_stats[i]),
            'cooperate_at_all': numpy.mean(cooperate_at_all_stats[i]),
            'continue_at_all': numpy.mean(continue_at_all_stats[i]),
        }
        cooperate_continue_stats.append(cooperate_continue_stats_gen)

    return cooperate_continue_stats

def unfreeze_bulk_nostats(file_prefix):
    """
    Unfreezes a large number of trials in bulk and combines their populations to make one large population
    Use when visualizing and aggregating strastegy classifications of a large number of trials with the same parameters
    Trial folders should be in the current directory scope, and named {file_prefix}-0/, {file_prefix-1}/, etc.
    trial_prefix should not have a trailing slash
    """
    dir = os.path.dirname('{}-final/test.txt'.format(file_prefix))
    if not os.path.exists(dir):
        os.makedirs(dir)

    i = 0
    nums = []
    while True:
        if os.path.isfile('{}-{}/player1_pop.json'.format(file_prefix, i)):
            nums.append(i)
            i += 1
        else:
            break

    player1_pops = []
    player2_pops = []

    for i in nums:
        player1_pop, player2_pop, setup_vars = unfreeze('{}-{}/'.format(file_prefix, i))
        player1_pops += player1_pop
        player2_pops += player2_pop

    setup_vars['aggregate'] = True
    setup_vars['runs'] = 100
    

    with open(file_prefix + '-final/setup_vars.json', 'w+') as outfile:
        outfile.write(json.dumps(setup_vars))

    return player1_pops, player2_pops


def classify_strategies(player1_pop, player2_pop):
    """
    Takes player populations and classifies them, returning a list of player classifications
    Used for visualizations
    """
    unique_player1_strategies, unique_player2_strategies = group_alike_strategies(player1_pop, player2_pop)

    player1_classifications = []
    player2_classifications = []

    for player1 in unique_player1_strategies:
        classification = classify_player1_strategy(player1[0])
        player1_classifications.append((classification, player1[1]))

    for player2 in unique_player2_strategies:
        classification = classify_player2_strategy(player2[0])
        player2_classifications.append((classification, player2[1]))
    
    return player1_classifications, player2_classifications


def simplify_player1(player1):
    """
    Reduces a Player 1 strategy to its simplest form (i.e., with the least number of states)
    """

    first_action_set = {}
    action_sets = []
    for state_id in player1.states:
        if not first_action_set:
            first_action_set = copy.deepcopy(player1.states[state_id].action_set)
        elif player1.states[state_id].action_set != first_action_set:
            return player1
        else:
            action_sets.append(player1.states[state_id].action_set)
    else:
        new_state_id = random_id()
        strategy_set ={
            'next': new_state_id
        }
        new_state = fsm.State(strategy_set=strategy_set, action_set=first_action_set, id=new_state_id)
        states = {new_state_id: new_state}
        simplified_player = fsm.Player1(states=states, initial_state=new_state_id)
        return simplified_player



def simplify_player2(player2):
    """
    If a Player 2 strategy is made up of many states all with the same action, this will reduce them to
    a strategy with only a single state. That is, it only works on strategies reducible to All C or All E
    """

    first_action_set = {}
    action_sets = []
    for state_id in player2.states:
        if not first_action_set:
            first_action_set = copy.deepcopy(player2.states[state_id].action_set)
        elif player2.states[state_id].action_set != first_action_set:
            return player2
        else:
            action_sets.append(player2.states[state_id].action_set)
    else:
        new_state_id = random_id()
        strategy_set ={
                'looked':{
                    'low': {
                        'defect': new_state_id,
                        'cooperate': new_state_id,
                        },
                    'high': {
                        'defect': new_state_id,
                        'cooperate': new_state_id,
                    },
                },
                'nolook': {
                    'low': {
                        'defect': new_state_id,
                        'cooperate': new_state_id,
                        },
                    'high': {
                        'defect': new_state_id,
                        'cooperate': new_state_id,
                        },
                    }
                }
        new_state = fsm.State(strategy_set=strategy_set, action_set=first_action_set, id=new_state_id)
        states = {new_state_id: new_state}
        simplified_player = fsm.Player2(states=states, initial_state=new_state_id)
        return simplified_player

def group_alike_strategies(player1_pop, player2_pop):
    """
    Takes a population, finds the unique strategies, and returns a list of each strategy
    with the number of players playing it in a tuple -> (strategy, number)
    """

    unique_player1_strategies = []
    for player1 in player1_pop:
        player1 = simplify_player1(player1)
        for i, (unique_player1, count) in enumerate(unique_player1_strategies):
            if equal_strategies_player1(player1, unique_player1):
                unique_player1_strategies[i][1] += 1
                break
        else:
            unique_player1_strategies.append([player1, 1])

    unique_player2_strategies = []
    for player2 in player2_pop:
        player2 = simplify_player2(player2)
        for i, (unique_player2, count) in enumerate(unique_player2_strategies):
            if equal_strategies_player2(player2, unique_player2):
                unique_player2_strategies[i][1] += 1
                break
        else:
            unique_player2_strategies.append([player2, 1])
    unique_player1_strategies.sort(key=lambda x: x[1], reverse=True)
    unique_player2_strategies.sort(key=lambda x: x[1], reverse=True)

    return unique_player1_strategies, unique_player2_strategies



def classify_from_frozen(file_prefix, gens, milestone):
    """
    Takes a file_prefix, number of generations, and milestone, unfreezes the populations at each milestone,
    and classifies the strategies. Outputs JSON files for each milestone
    """

    dir = os.path.dirname('{}/classification/info.txt'.format(file_prefix))
    if not os.path.exists(dir):
        os.makedirs(dir)

    i = 0
    while i <= gens:
        if os.path.isfile('{}/player1_pop_{}.json'.format(file_prefix, i)):
            player1_pop, player2_pop, setup_vars = unfreeze(file_prefix, i)
            player1_classifications, player2_classifications = classify_strategies(player1_pop, player2_pop)

            with open('{}/classification/gen{}_player1.json'.format(file_prefix, i), 'w+') as outfile:
                outfile.write(json.dumps(player1_classifications))

            with open('{}/classification/gen{}_player2.json'.format(file_prefix, i), 'w+') as outfile:
                outfile.write(json.dumps(player2_classifications))

        i += milestone

def classify_player1_strategy(player1):
    """
    Classifies a Player 1 strategy as:
        DWOL
        CWOL
        DWL
        CWL
        Only L - this should really be 'Only L'
        Other D -> a mixture of DWOL and DWL
        Other C -> a mixture of CWOL and CWL
        Unclassified
    """


    if equal_strategies_player1(player1, fsm.Player1('dwol')):
        return 'DWOL'
    elif equal_strategies_player1(player1, fsm.Player1('cwol')):
        return 'CWOL'
    elif equal_strategies_player1(player1, fsm.Player1('dwl')):
        return 'DWL'
    elif equal_strategies_player1(player1, fsm.Player1('cwl')):
        return 'CWL'
    elif equal_strategies_player1(player1, fsm.Player1('onlyl')):
        return 'Only L'
    else:
        action = None
        for state_id in player1.states:
            if player1.states[state_id].action_set['high'] == player1.states[state_id].action_set['low']:
                if not action:
                    action = player1.states[state_id].action_set['high']
                elif action != player1.states[state_id].action_set['high']:
                    return None
            else:
                return None
        else:
            if action == 'defect':
                return 'Other D'
            else:
                return 'Other C'

def classify_player2_strategy(player2):
    """
    Classifies a Player 2 strategy as:
        All E
        All C
        Unclassified
    """
    if equal_strategies_player2(player2, fsm.Player2('alle')):
        return 'All E'
    elif equal_strategies_player2(player2, fsm.Player2('allc')):
        return 'All C'
    else:
        return None
