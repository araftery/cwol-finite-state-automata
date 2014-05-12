import sys, os, json, utils, shutil, tally_classifications

def analyze(file_prefix, viz):

    # make sure the file prefix has a trailing slash
    if not file_prefix[-1] == '/':
        file_prefix += '/'

    if not os.path.isdir(file_prefix):
        raise Exception('The file prefix you provided is invalid.')

    # get setup vars
    with open('{}setup_vars.json'.format(file_prefix), 'r') as infile:
        setup_vars = json.load(infile)

    # classify strategies
    print 'Classifying strategies...'
    utils.classify_from_frozen(file_prefix, setup_vars['generations'], setup_vars['milestone'])
    print 'Done.'
    print


    # tally classifications
    print 'Tallying classifications...'
    tally_classifications.tally(file_prefix, setup_vars['generations'], setup_vars['milestone'])
    print 'Done.'
    print

    # visualize
    if viz:
        try:
            import visualize_strategies
            print 'Visualizing strategies [          ]',
            print '\b'*12,
            steps = setup_vars['generations'] / 10
            for i in range(setup_vars['generations']):
                if i % setup_vars['milestone'] == 0:
                    visualize_strategies.visualize_frozen(file_prefix, i)

                if i % steps == 0:
                    print '\b.',
                    sys.stdout.flush()
            print '\b]  Done.',
            print
        except ImportError:
            print 'PyGraphViz library not found. Skipping visualization.'
            viz = False
    else:
        print 'Skipping visualization.'
        print

    # move files
    print 'Moving files...'
    os.makedirs('{}analysis/'.format(file_prefix))
    shutil.copyfile('{}setup_vars.json'.format(file_prefix), '{}analysis/setup_vars.json'.format(file_prefix))
    shutil.move('{}classification/player1_tally.json'.format(file_prefix), '{}analysis/player1_tally.json'.format(file_prefix))
    shutil.move('{}classification/player2_tally.json'.format(file_prefix), '{}analysis/player2_tally.json'.format(file_prefix))
    shutil.move('{}classification/player1_stats.json'.format(file_prefix), '{}analysis/player1_stats.json'.format(file_prefix))
    shutil.move('{}classification/player2_stats.json'.format(file_prefix), '{}analysis/player2_stats.json'.format(file_prefix))
    shutil.move('{}classification/aggregate_stats.json'.format(file_prefix), '{}analysis/aggregate_stats.json'.format(file_prefix))
    if viz:
        shutil.move('{}viz/'.format(file_prefix), '{}analysis/viz/'.format(file_prefix))
    shutil.copyfile('./analyze_files/analyze.html', '{}analysis/index.html'.format(file_prefix))
    shutil.copyfile('./analyze_files/analyze.js', '{}analysis/analyze.js'.format(file_prefix))
    shutil.copyfile('./analyze_files/d3.legend.js', '{}analysis/d3.legend.js'.format(file_prefix))
    print 'Done.'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('You did not provide a file prefix.')

    file_prefix = sys.argv[1]
    viz = True

    if len(sys.argv) > 2 and sys.argv[2] == '--no-viz':
        viz = False

    analyze(file_prefix, viz)