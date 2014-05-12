import utils, draw_fsm, fsm, json, os, copy, pprint


def visualize_frozen(file_prefix, gen=None):
    player1_pop, player2_pop, setup_vars = utils.unfreeze(file_prefix, gen)
    visualize(player1_pop, player2_pop, file_prefix, gen)

def visualize_bulk_frozen_nostats(file_prefix):
    player1_pop, player2_pop = utils.unfreeze_bulk_nostats(file_prefix)
    visualize(player1_pop, player2_pop, file_prefix + '-final/')

def bulk_frozen_stats(file_prefix):
    cooperate_continue_stats = utils.unfreeze_bulk_stats(file_prefix)

    with open(file_prefix + '-final/cooperate_continue_stats.json', 'w+') as outfile:
        outfile.write(json.dumps(cooperate_continue_stats))

def visualize(player1_pop, player2_pop, file_prefix, gen=None):
    file_prefix += 'viz/{}/'.format('final' if gen is None else gen)
    dir = os.path.dirname('{}/info.txt'.format(file_prefix))
    if not os.path.exists(dir):
        os.makedirs(dir)

    unique_player1_strategies, unique_player2_strategies = utils.group_alike_strategies(player1_pop, player2_pop)


    for i, player1 in enumerate(unique_player1_strategies):
        with open('{}player1_{}.png'.format(file_prefix, i), 'w+') as outfile:
            draw_fsm.graph_player1(player1[0], outfile, utils.classify_player1_strategy(player1[0]))


    for i, player2 in enumerate(unique_player2_strategies):
        with open('{}player2_{}.png'.format(file_prefix, i), 'w+') as outfile:
            draw_fsm.graph_player2(player2[0], outfile, utils.classify_player2_strategy(player2[0]))

    html_file = '<html><body><h1>Player 1 Strategies</h1>'
    for i, player1 in enumerate(unique_player1_strategies):
        html_file += '<h3>{}</h3><br /><img src="player1_{}.png" /><br /><br />'.format(float(player1[1])/(len(player1_pop)), i)

    html_file += '<br /><br /><br /><h1>Player 2 Strategies</h1>'

    for i, player2 in enumerate(unique_player2_strategies):
        html_file += '<h3>{}</h3><br /><img src="player2_{}.png" /><br /><br />'.format(float(player2[1])/(len(player2_pop)), i)

    html_file += '</body></html>'

    with open('{}strategies.html'.format(file_prefix), 'w+') as outfile:
        outfile.write(html_file)