import json, os, numpy

def merge_dictionaries(dict1, dict2):
    if set(dict1.keys()) == set(dict2.keys()):
        for key in dict1:
            dict1[key] += dict2[key]

        return dict1
    else:
        raise

def tally_bulk(file_prefix, gens, milestone):
    i = 0
    p1_strats = ['DWOL', 'DWL', 'Other D', 'CWOL', 'CWL', 'Other C', 'Only L', 'Unclassified']
    p2_strats = ['All E', 'All C', 'Unclassified']

    p1_tallies = {i:{x: 0 for x in range(0, gens, milestone)} for i in p1_strats}
    p2_tallies = {i:{x: 0 for x in range(0, gens, milestone)} for i in p2_strats}

    while os.path.isdir('{}trial{}'.format(file_prefix, i)):
        p1_tallies_trial, p2_tallies_trial = tally(file_prefix + 'trial{}/'.format(i), gens, milestone, True)
        for key in p1_tallies:
            p1_tallies[key] = merge_dictionaries(p1_tallies[key], p1_tallies_trial[key])

        for key in p2_tallies:
            p2_tallies[key] = merge_dictionaries(p2_tallies[key], p2_tallies_trial[key])

        i += 1



    with open('{}player1_tally.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p1_tallies))

    with open('{}player2_tally.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p2_tallies))



def tally_stats(file_prefix, gens, milestone, return_data=False):
    cooperate_continue_stats = {'cooperate': {}}
    i = 0
    while i <= gens:
        if os.path.isfile('{}cooperate_continue_stats_{}.json'.format(file_prefix, i)):
            infile = open('{}cooperate_continue_stats_{}.json'.format(file_prefix, i), 'r')
            data = json.load(infile)

            cooperate_continue_stats['cooperate'][i] = float(data[0]['cooperate'])/data[0]['moves']

        i += milestone

    with open('{}coop_tally.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(cooperate_continue_stats))


def tally(file_prefix, gens, milestone, return_data=False):
    i = 0
    p1_strats = ['DWOL', 'DWL', 'Other D', 'CWOL', 'CWL', 'Other C', 'Only L', 'Unclassified']
    p2_strats = ['All E', 'All C', 'Unclassified']

    p1_tallies = {i:{} for i in p1_strats}
    p2_tallies = {i:{} for i in p2_strats}

    p1_stats = {'total': {}, 'at_all': {}}
    p2_stats = {'total': {}, 'at_all': {}}

    continues = []
    cooperates = []

    while i <= gens:

        if os.path.isfile('{}classification/gen{}_player1.json'.format(file_prefix, i)):
            with open('{}classification/gen{}_player1.json'.format(file_prefix, i), 'r') as player1_infile:
                player1s = json.load(player1_infile)

            with open('{}classification/gen{}_player2.json'.format(file_prefix, i), 'r') as player2_infile:
                player2s = json.load(player2_infile)

            with open('{}cooperate_continue_stats_{}.json'.format(file_prefix, i)) as stats_infile:
                cooperate_continue_stats = json.load(stats_infile)[0]

            p1_total = float(cooperate_continue_stats['cooperate'])/float(cooperate_continue_stats['moves'])
            p1_stats['total'][i] = p1_total
            p1_stats['at_all'][i] = cooperate_continue_stats['cooperate_at_all']
            cooperates.append(p1_total)

            p2_total = float(cooperate_continue_stats['continue'])/float(cooperate_continue_stats['moves'])
            p2_stats['total'][i] = p2_total
            p2_stats['at_all'][i] = cooperate_continue_stats['continue_at_all']
            continues.append(p2_total)

            for strat in p1_strats:
                p1_tallies[strat][i] = 0

            for strat in p2_strats:
                p2_tallies[strat][i] = 0

            for player1 in player1s:
                if player1[0] is None:
                    p1_tallies['Unclassified'][i] += player1[1]
                else:
                    p1_tallies[player1[0]][i] += player1[1]


            for player2 in player2s:
                if player2[0] is None:
                    p2_tallies['Unclassified'][i] += player2[1]
                else:
                    p2_tallies[player2[0]][i] += player2[1]



        i += milestone

    with open('{}classification/player1_tally.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p1_tallies))

    with open('{}classification/player2_tally.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p2_tallies))

    with open('{}classification/player1_stats.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p1_stats))

    with open('{}classification/player2_stats.json'.format(file_prefix), 'w+') as outfile:
        outfile.write(json.dumps(p2_stats))

    with open('{}classification/aggregate_stats.json'.format(file_prefix), 'w+') as outfile:
        aggregate_stats = {
            'player1': numpy.mean(cooperates),
            'player2': numpy.mean(continues)
        }
        outfile.write(json.dumps(aggregate_stats))

    if return_data:
        return p1_tallies, p2_tallies, p1_stats, p2_stats

