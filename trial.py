import simulation

# probability that temptation is low
p = .51

# player1 payoff for cooperating
# c_h > c_l > a > 0
a = 1.1

# player1 payoffs for defecting
# c_l if temptation is low, c_h if temptation is high
c_l = 4.0
c_h = 12.0

# payoff for player2 if player1 cooperates
# b > 0
b = 1.0
d = -10.0

# probability that game repeats
w = .895

# population size
pop = 100

# probability that any one player will be mutated each generation
# or, the expected percentage of the population that will be mutated each generation
mutate_prob = .05


generations = 10000
milestone = 10
silent = True

selection_strength = .4

# options: dwol, dwl, cwl, cwol, onlyl
player1_seed = 'dwol'

# options: alle, allc, only_cwol
player2_seed = 'alle'

# where to store trial data
# if set to None, it will store in ./trials/trial{x}/ where {x} is the next available number
file_prefix = './demo/'

simulation.run_simulation(p=p, a=a, c_l=c_l, c_h=c_h, b=b, d=d, w=w, pop=pop, selection_strength=selection_strength, mutate_prob=mutate_prob, generations=generations, milestone=milestone, file_prefix=file_prefix, silent=False, player1_seed=player1_seed, player2_seed=player2_seed)