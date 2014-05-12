import fsm, utils, random, json, os, calendar, datetime, itertools

def run_simulation(p, a, c_l, c_h, b, d, w, pop, selection_strength, mutate_prob, generations, file_prefix=None, milestone=1000, silent=False, player1_seed='dwol', player2_seed='alle'):

    # if no file_prefix was provided, create a new folder at ./trials/ to store created files in
    if file_prefix is None:
        i = 0
        while True:
            dir = os.path.dirname('./trials/trial{}/info.txt'.format(i))
            if not os.path.exists(dir):
                file_prefix = './trials/trial{}/'.format(i)
                break
            i += 1

    dir = os.path.dirname('{}/info.txt'.format(file_prefix))
    if not os.path.exists(dir):
        os.makedirs(dir)

    # output a file with the setup parameters
    with open('{}setup_vars.json'.format(file_prefix), 'w+') as outfile:
        setup_vars = {'p': p, 'a': a, 'c_l': c_l, 'c_h': c_h, 'b': b, 'd': d, 'w': w, 'pop': pop, 'mutate_prob': mutate_prob, 'generations': generations, 'selection_strength': selection_strength, 'file_prefix': file_prefix, 'milestone': milestone, 'player1_seed': player1_seed, 'player2_seed': player2_seed}
        outfile.write(json.dumps(setup_vars))


    player1_pop = []
    player2_pop = []
    coop_stats = []
    mutations = ['alter_strategy', 'alter_action', 'add_state', 'delete_state']
    time_started = prev_gen_time = calendar.timegm(datetime.datetime.now().utctimetuple())
    finished_normally = True

    # create the initial population
    for _ in range(pop/2):
        player1 = fsm.Player1(player1_seed)
        player2 = fsm.Player2(player2_seed)

        player1_pop.append(player1)
        player2_pop.append(player2)

    # puts everything in a try block, so that if the user exits (with ctrl + c),
    # files may still be outputted at the end
    try:

        # outer loop for each generation
        for gen in range(generations):

            # statistics collected during the round
            continue_num = 0
            cooperate_num = 0
            cooperate_at_all_num = 0
            continue_at_all_num = 0
            moves = 0

            #####
            #
            # PLAY THE GAME
            #
            #####

            # create tuples matching each Player 1 with each Player 2 only once
            pairs = itertools.product(player1_pop, player2_pop)

            # loop through the pairs and play the strategies against each other
            for player1, player2 in pairs:

                # make sure that the current state is set to the first state
                player1.reset()
                player2.reset()

                repeat = True
                continue_at_all = False
                cooperate_at_all = False
                while repeat:
                    moves += 1

                    # choose temptation
                    if utils.probability(p):
                        temptation = 'low'
                    else:
                        temptation = 'high'

                    # determine the player1's action first
                    player1_action = player1.action(temptation)

                    # calculate payoffs based on player1's action
                    cooperate_defect = player1_action['move']
                    if cooperate_defect == 'defect' and temptation == 'high':
                        player1.add_payoff(c_h)
                        player2.add_payoff(d)
                    elif cooperate_defect == 'defect' and temptation == 'low':
                        player1.add_payoff(c_l)
                        player2.add_payoff(d)
                    elif cooperate_defect == 'cooperate':
                        cooperate_num += 1
                        if not cooperate_at_all:
                            cooperate_at_all = True
                            cooperate_at_all_num += 1
                        player1.add_payoff(a)
                        player2.add_payoff(b)

                    # advance both players
                    player1.advance_state()
                    player2.advance_state(player1_action)

                    # decide player2's action (in response to player1's)
                    player2_action = player2.action(temptation)

                    omega_repeat = utils.probability(w)
                    cont = player2_action['action'] == 'continue'
                    if cont:
                        continue_num += 1
                        if not continue_at_all:
                            continue_at_all = True
                            continue_at_all_num += 1

                    # repeat if player2 played "continue," and the random dice roll chose to continue
                    repeat = omega_repeat and cont

            coop_stats.append((continue_num, cooperate_num, continue_at_all_num, cooperate_at_all_num, moves))


            #####
            #
            # DETERMINE NEXT GENERATION
            #
            #####

            # reproduction process:
            # segments the number line from 0 - 1 based on the players' relative fitness
            # then, creates new players by choosing random numbers between 0 and 1

            # player1s

            dist = utils.create_distribution(player1_pop, selection_strength, games=pop/2)
            new_player1_pop = []
            for _ in range(pop/2):
                rand = random.random()
                parent = utils.determine_player(dist, rand)
                new_player1_pop.append(utils.player_deep_copy(parent))

            player1_pop = new_player1_pop



            # player2s

            dist = utils.create_distribution(player2_pop, selection_strength, games=pop/2)
            new_player2_pop = []
            for _ in range(pop/2):
                rand = random.random()
                parent = utils.determine_player(dist, rand)
                new_player2_pop.append(utils.player_deep_copy(parent))

            player2_pop = new_player2_pop

            #####
            #
            # MUTATE
            #
            #####

            # don't mutate on the last generation
            if gen < generations - 1:

                for player1 in player1_pop:
                    if utils.probability(mutate_prob):
                        mutation = random.choice(mutations)
                        if mutation == 'alter_strategy':
                            player1.alter_strategy()
                        elif mutation == 'alter_action':
                            player1.alter_action()
                        elif mutation == 'delete_state':
                            player1.delete_state()
                        elif mutation == 'add_state':
                            player1.add_state()

                for player2 in player2_pop:
                    if utils.probability(mutate_prob):
                        mutation = random.choice(mutations)
                        if mutation == 'alter_strategy':
                            player2.alter_strategy()
                        elif mutation == 'alter_action':
                            player2.alter_action()
                        elif mutation == 'delete_state':
                            player2.delete_state()
                        elif mutation == 'add_state':
                            player2.add_state()

            # if the generation is a milestone, save the populations and record some stats
            if gen % milestone == 0:

                now = calendar.timegm(datetime.datetime.now().utctimetuple())
                gen_runtime = round(float(now - prev_gen_time)/60, 3)

                # save player 1 population
                with open('{}player1_pop_{}.json'.format(file_prefix, gen), 'w+') as outfile:

                    # convert players to dictionaries
                    player1_pop_json = [player1.to_dict() for player1 in player1_pop]
                    outfile.write(json.dumps(player1_pop_json))

                # save player 2 population
                with open('{}player2_pop_{}.json'.format(file_prefix, gen), 'w+') as outfile:

                    # convert players to dictionaries
                    player2_pop_json = [player2.to_dict() for player2 in player2_pop]
                    outfile.write(json.dumps(player2_pop_json))

                # save stats
                with open('{}cooperate_continue_stats_{}.json'.format(file_prefix, gen), 'w+') as outfile:
                    rounds = []
                    labels = ['continue', 'cooperate', 'continue_at_all', 'cooperate_at_all', 'moves']
                    for rnd in coop_stats:
                        rnd = {labels[i]:val for i, val in enumerate(rnd)}
                        rounds.append(rnd)
                    
                    outfile.write(json.dumps(rounds))

                with open('{}cooperate_continue_totals_{}.json'.format(file_prefix, gen), 'w+') as outfile:
                    for rnd in coop_stats:
                        rnd = {labels[i]:val for i, val in enumerate(rnd)}
                        rounds.append(rnd)
                        
                    total_cooperated_at_all = sum([i['cooperate_at_all'] for i in rounds])
                    total_continued_at_all = sum([i['continue_at_all'] for i in rounds])
                    total_cooperated = sum([i['cooperate'] for i in rounds])
                    total_continued = sum([i['continue'] for i in rounds])
                    total_moves = sum([i['moves'] for i in rounds])

                    totals = {
                        'total_cooperated_at_all': total_cooperated_at_all,
                        'total_continued_at_all': total_continued_at_all,
                        'total_cooperated': total_cooperated,
                        'total_continued': total_continued,
                        'total_moves': total_moves,
                    }

                    outfile.write(json.dumps(totals))
                    coop_stats = []

                if not silent:
                    print 'Generation {} ({} mins.)'.format(gen, gen_runtime)

                prev_gen_time = calendar.timegm(datetime.datetime.now().utctimetuple())

    except KeyboardInterrupt:
        finished_normally = False

    time_finished = calendar.timegm(datetime.datetime.now().utctimetuple())
    setup_vars_str = ''
    for var in setup_vars:
        setup_vars_str += '\t{}: {}\n'.format(var, setup_vars[var])

    runtime = round(float(time_finished - time_started)/60, 3)

    with open('{}cooperate_continue_stats.json'.format(file_prefix), 'w+') as outfile:
        rounds = []
        labels = ['continue', 'cooperate', 'continue_at_all', 'cooperate_at_all', 'moves']
        for rnd in coop_stats:
            rnd = {labels[i]:val for i, val in enumerate(rnd)}
            rounds.append(rnd)
        
        outfile.write(json.dumps(rounds))

    total_cooperated_at_all = sum([i['cooperate_at_all'] for i in rounds])
    total_continued_at_all = sum([i['continue_at_all'] for i in rounds])
    total_cooperated = sum([i['cooperate'] for i in rounds])
    total_continued = sum([i['continue'] for i in rounds])
    total_moves = sum([i['moves'] for i in rounds])
    total_games = (gen + 1) * (pop/2)

    with open('{}cooperate_continue_totals.json'.format(file_prefix), 'w+') as outfile:
        totals = {
            'total_cooperated_at_all': total_cooperated_at_all,
            'total_continued_at_all': total_continued_at_all,
            'total_cooperated': total_cooperated,
            'total_continued': total_continued,
            'total_moves': total_moves
        }
        
        outfile.write(json.dumps(totals))

    with open('{}info.txt'.format(file_prefix), 'w+') as outfile:
        string = """Finished Normally: {}
Time Started: {}
Time Finished: {}
Runtime (minutes): {}
Generations: {}
Total Coop at All (since last milestone): {}
Total Cont at All (since last milestone): {}
Total Coop Moves (since last milestone): {}
Total Cont Moves (since last milestone): {}
Total moves (since last milestone): {}
Setup Variables:
{}""".format(finished_normally, time_started, time_finished, runtime, gen + 1, total_cooperated_at_all, total_continued_at_all, total_cooperated, total_continued, total_moves, setup_vars_str)
        
        outfile.write(string)

    with open('{}player1_pop.json'.format(file_prefix), 'w+') as outfile:
        player1_pop_json = [player1.to_dict() for player1 in player1_pop]

        outfile.write(json.dumps(player1_pop_json))

    with open('{}player2_pop.json'.format(file_prefix), 'w+') as outfile:
        player2_pop_json = [player2.to_dict() for player2 in player2_pop]
        outfile.write(json.dumps(player2_pop_json))


    return player1_pop, player2_pop
