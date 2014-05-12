import random, pprint, copy, utils, json

class State(object):
    """
    Has a strategy_set (defines 'arrows' that leave from it) and an action_set (defines what kind of 'circle' it is)
    """
    def __init__(self, strategy_set, action_set, id):
        self.strategy_set = strategy_set
        self.action_set = action_set
        self.id = id

    def action(self, temptation):
        """
        For player 1, returns observation set: move, looked, and temptation,
        for player 2, returns {'action': 'continue/exit'}
        """
        if self.action_set.get('action'):
            return {'action': self.action_set['action']}
        else:
            return {'move': self.action_set[temptation], 
                    'looked': self.action_set['look'], 
                    'temptation': temptation}

    def action_hash(self):
        return hash(frozenset(state.action_set))

    def __str__(self):
        return '\nState {}:\nstrategy set: {}\naction_set: {}'.format(self.id, pprint.pformat(self.strategy_set), pprint.pformat(self.action_set))


class Player1(object):
    def __init__(self, initial_strategy=None, states=None, initial_state=None):
        if states is None:
            self.states = {}
        else:
            self.states = states

        if initial_state is None:
            self.initial_state = utils.random_id()
        else:
            self.initial_state = initial_state
        
        self.state = self.initial_state
        self.type = 1
        self.payoffs = 0
        self.games = 0

        if initial_strategy:
            self._set_initial(initial_strategy)

    def to_dict(self):
        states = {}
        for state_id in self.states:
            state = self.states[state_id]
            states[state.id] = state.__dict__

        player = {
            'initial_state': self.initial_state,
            'states': states,
            'type': self.type,
        }

        return player


    def score(self, selection_strength, games):
        return utils.score(self.payoffs, selection_strength, games)

    def _set_initial(self, strat='dwol'):
        # start w/ dwol
        if strat == 'dwol':
            strategy_set ={
                    'next': self.initial_state
                    }

            action_set = {
                        'look': False,
                        'high': 'defect',
                        'low': 'defect',
                    }
        elif strat == 'cwol':
            strategy_set ={
                    'next': self.initial_state
                    }

            action_set = {
                        'look': False,
                        'high': 'cooperate',
                        'low': 'cooperate',
                    }
        elif strat == 'dwl':
            strategy_set ={
                    'next': self.initial_state
                    }

            action_set = {
                        'look': True,
                        'high': 'defect',
                        'low': 'defect',
                    }
        elif strat == 'cwl':
            strategy_set ={
                    'next': self.initial_state
                    }

            action_set = {
                        'look': True,
                        'high': 'cooperate',
                        'low': 'cooperate',
                    }
        elif strat == 'onlyl':
            strategy_set ={
                    'next': self.initial_state
                    }

            action_set = {
                        'look': True,
                        'high': 'defect',
                        'low': 'cooperate',
                    }


        self.states[self.initial_state] = State(strategy_set=copy.deepcopy(strategy_set), action_set=copy.deepcopy(action_set), id=self.initial_state)
        self.state = self.initial_state

    @property
    def current_state(self):
        return self.states[self.state]

    def add_payoff(self, payoff):
        self.payoffs += payoff

    def advance_state(self):
        """
        opponent_action is an observation set as described in State.action()
        """

        new_state = self.current_state.strategy_set['next']
        self.state = new_state

    def action(self, temptation):
        return self.current_state.action(temptation)


    def reset(self):
        self.state = self.initial_state

    def add_state(self):
        """
        Creates a new state
        Then, chooses a random state, chooses a random edge, and points
        that edge to the new state
        """

        state_ids = self.states.keys()

        # choose a random state to alter
        state_id = random.choice(state_ids)
        state = self.states[state_id]

        new_state = self._add_random_state()
        state.strategy_set['next'] = new_state

        self._delete_inactive_states()


    def _add_random_state(self):
        """
        Creates a random new state
        """

        new_id = utils.random_id()
        state_ids = self.states.keys() + [new_id]
        look = random.choice([True, False])
        if look:
            look_high_action = random.choice(['cooperate', 'defect'])
            look_low_action = random.choice(['cooperate', 'defect'])
        else:
            look_high_action = look_low_action = random.choice(['cooperate', 'defect'])


        set = {
        'strategy_set': {
            'next': random.choice(state_ids),
             },

        'action_set': {
                'look': look,
                'high': look_high_action,
                'low': look_low_action,
            },
        'id': new_id,
        }

        self.states[new_id] = State(**set)

        return new_id

    def alter_strategy(self):
        """
        Chooses a random state, then chooses a random edge ("arrow") of that 
        state, and alters that edge randomly
        """

        state_ids = self.states.keys()

        # choose a random state to alter
        state_id = random.choice(state_ids)
        state = self.states[state_id]

        # choose a random state to change to (or add a new one)
        new_state = random.choice(state_ids)
        state.strategy_set['next'] = new_state

        self._delete_inactive_states()

    def alter_action(self):
        """
        Chooses a random state, then randomly changes the action of that state
        """
        
        # choose a random state to alter
        state_ids = self.states.keys()
        state_id = random.choice(state_ids)
        state = self.states[state_id]

        # choose a random action
        rand_action = random.choice(['look', 'high', 'low'])
        if rand_action == 'look':
            rand_response = random.choice([True, False])

            # if we're changing from looking to not looking, low and high responses must be made the same
            # draw randomly between the two and set both to that value
            if rand_response is False and state.action_set['high'] != state.action_set['low']:
                state.action_set['high'] = state.action_set['low'] = random.choice([state.action_set['high'], state.action_set['low']])
            state.action_set[rand_action] = rand_response

        else:
            rand_response = random.choice(['cooperate', 'defect'])

            # if the player doesn't look, both high and low need to be changed
            if state.action_set['look'] is False:
                state.action_set['high'] = state.action_set['low'] = rand_response
            else:
                state.action_set[rand_action] = rand_response


    def _delete_inactive_states(self):
        """
        Finds states that don't have any edges pointing to them,
        and deletes them
        """

        active_states = utils.traverse_player1_tree(self)
        inactive_states = set(self.states.keys()) - set(active_states)
        for inactive_state in inactive_states:
            del self.states[inactive_state]

    def delete_state(self):
        """
        Chooses a random state and deletes it
        """

        # choose a random state
        states = self.states.keys()
        num_states = len(states)

        if num_states > 1:
            deleted_state_id = random.choice(states)
            deleted_state = self.states[deleted_state_id]
            states = list(set(states) - { deleted_state_id })


            for state_id in states:
                state = self.states[state_id]
                if state.strategy_set['next'] == deleted_state_id:
                    state.strategy_set['next'] = random.choice(states)
            
            # if the deleted state was the initial state, choose a new initial state
            if self.initial_state == deleted_state_id:
                self.initial_state = random.choice(states)

            # delete the state
            del self.states[deleted_state_id]

            self._delete_inactive_states()


    def __str__(self):
        string = ''
        for key in self.states:
            state = self.states[key]
            string += str(state)
        return string




class Player2(object):
    def __init__(self, initial_strategy=None, states=None, initial_state=None):
        if states is None:
            self.states = {}
        else:
            self.states = states

        if initial_state is None:
            self.initial_state = utils.random_id()
        else:
            self.initial_state = initial_state
        
        self.state = self.initial_state
        self.type = 2
        self.payoffs = 0

        if initial_strategy:
            self._set_initial(initial_strategy)

    def to_dict(self):
        """
        Encodes the player's strategy as a dictionary (for saving to JSON)
        """

        states = {}
        for state_id in self.states:
            state = self.states[state_id]
            states[state.id] = state.__dict__

        player = {
            'initial_state': self.initial_state,
            'states': states,
            'type': self.type,
        }

        return player

    def score(self, selection_strength, games):
        """
        Calculates player's fitness score based on payoffs
        """

        return utils.score(self.payoffs, selection_strength, games)

    def _set_initial(self, strat='alle'):
        """
        Sets initial strategy
        Options are:
            alle
            allc
            only_cwol
        """

        if strat == 'alle':
            strategy_set ={
                    'looked':{
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                        },
                    },
                    'nolook': {
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        }
                    }

            action_set = {
                        'action': 'exit',
                    }

            self.states[self.initial_state] = State(strategy_set=copy.deepcopy(strategy_set), action_set=copy.deepcopy(action_set), id=self.initial_state)
            self.state = self.initial_state

        elif strat == 'allc':
            strategy_set ={
                    'looked':{
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                        },
                    },
                    'nolook': {
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        }
                    }

            action_set = {
                        'action': 'continue',
                    }


            self.states[self.initial_state] = State(strategy_set=copy.deepcopy(strategy_set), action_set=copy.deepcopy(action_set), id=self.initial_state)
            self.state = self.initial_state

        elif strat == 'only_cwol':
            id_2 = utils.random_id()
            strategy_set ={
                    'looked':{
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                        },
                    },
                    'nolook': {
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': id_2,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': id_2,
                            },
                        }
                    }

            action_set = {
                        'action': 'exit',
                    }

            strategy_set2 ={
                    'looked':{
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': self.initial_state,
                        },
                    },
                    'nolook': {
                        'low': {
                            'defect': self.initial_state,
                            'cooperate': id_2,
                            },
                        'high': {
                            'defect': self.initial_state,
                            'cooperate': id_2,
                            },
                        }
                    }

            action_set2 = {
                        'action': 'continue',
                    }

            self.states[self.initial_state] = State(strategy_set=copy.deepcopy(strategy_set), action_set=copy.deepcopy(action_set), id=self.initial_state)
            self.states[id_2] = State(strategy_set=copy.deepcopy(strategy_set2), action_set=copy.deepcopy(action_set2), id=id_2)
            self.state = self.initial_state


    def add_payoff(self, payoff):
        self.payoffs += payoff

    def delete_state(self):
        """
        Chooses a random state and deletes it
        """

        # choose a random state
        states = self.states.keys()
        num_states = len(states)

        if num_states > 1:
            deleted_state_id = random.choice(states)
            deleted_state = self.states[deleted_state_id]
            states = list(set(states) - { deleted_state_id })


            for state_id in states:
                state = self.states[state_id]
                for look_nolook in ['looked', 'nolook']:
                    for high_low in ['high', 'low']:
                        for cooperate_defect in ['cooperate', 'defect']:
                            if state.strategy_set[look_nolook][high_low][cooperate_defect] == deleted_state_id:
                                state.strategy_set[look_nolook][high_low][cooperate_defect] = random.choice(states)
            
            # if the deleted state was the initial state, choose a new initial state
            if self.initial_state == deleted_state_id:
                self.initial_state = random.choice(states)

            # delete the state
            del self.states[deleted_state_id]

            self._delete_inactive_states()


    def _delete_inactive_states(self):
        """
        Finds states that don't have any edges pointing to them,
        and deletes them
        """

        active_states = utils.traverse_player2_tree(self)
        inactive_states = set(self.states.keys()) - set(active_states)
        
        # in some cases, arrows may still be pointing to inactive states if the action is exit
        # in those cases, randomly reassign the arrows

        for active_state_id in active_states:
            state = self.states[active_state_id]
            for look_nolook in ['looked', 'nolook']:
                for high_low in ['high', 'low']:
                    for cooperate_defect in ['cooperate', 'defect']:
                        if state.strategy_set[look_nolook][high_low][cooperate_defect] in inactive_states:
                            state.strategy_set[look_nolook][high_low][cooperate_defect] = random.choice(list(active_states))


        for inactive_state in inactive_states:
            del self.states[inactive_state]


    @property
    def current_state(self):
        return self.states[self.state]

    def reset(self):
        self.state = self.initial_state
        self.payoffs = 0

    def advance_state(self, opponent_action):
        """
        opponent_action is an observation set as described in State.action()
        """

        move = opponent_action['move']
        looked = opponent_action['looked']
        temptation = opponent_action['temptation']
        look_nolook = 'looked' if looked else 'nolook'
        new_state = self.current_state.strategy_set[look_nolook][temptation][move]
        self.state = new_state

    def action(self, temptation):
        return self.current_state.action(temptation)

    def _add_random_state(self):
        """
        Creates a random new state
        """

        action = random.choice(['continue', 'exit'])
        num_states = len(self.states)
        new_id = utils.random_id()
        ids = self.states.keys() + [new_id]

        set = {
        'strategy_set': {
            'looked': {
                'low': {
                    'defect': random.choice(ids),
                    'cooperate': random.choice(ids),
                    },
                'high': {
                    'defect': random.choice(ids),
                    'cooperate': random.choice(ids),
                    },
                },
            'nolook': {
                'low': {
                    'defect': random.choice(ids),
                    'cooperate': random.choice(ids),
                    },
                'high': {
                    'defect': random.choice(ids),
                    'cooperate': random.choice(ids),
                    },
                }
            },

        'action_set': {
                'action': action,
            },

        'id': new_id,
        }

        self.states[new_id] = State(**set)

        return new_id

    def alter_strategy(self):
        """
        Chooses a random state, then chooses a random edge ("arrow") of that 
        state, and alters that edge randomly
        """

        # choose a random state
        state_id = random.choice(self.states.keys())
        state = self.states[state_id]

        # choose a random state to change to
        new_state = random.choice(self.states.keys())

        # choose a random strategy
        look_nolook = random.choice(['looked', 'nolook'])
        low_high = random.choice(['low', 'high'])
        cooperate_defect = random.choice(['cooperate', 'defect'])
        state.strategy_set[look_nolook][low_high][cooperate_defect] = new_state

        self._delete_inactive_states()

    def add_state(self):
        """
        Creates a new state
        Then, chooses a random state, chooses a random edge, and points
        that edge to the new state
        """

        # choose a random state
        state_id = random.choice(self.states.keys())
        state = self.states[state_id]

        new_state = self._add_random_state()

        # choose a random strategy
        look_nolook = random.choice(['looked', 'nolook'])
        low_high = random.choice(['low', 'high'])
        cooperate_defect = random.choice(['cooperate', 'defect'])
        state.strategy_set[look_nolook][low_high][cooperate_defect] = new_state

        self._delete_inactive_states()


    def alter_action(self):
        """
        Chooses a random state, then randomly changes the action of that state
        """

        # choose a random state
        state_id = random.choice(self.states.keys())
        state = self.states[state_id]

        # choose a random response
        rand_response = random.choice(['continue', 'exit'])
        state.action_set['action'] = rand_response

        self._delete_inactive_states()

    def __str__(self):
        string = ''
        for key in self.states:
            state = self.states[key]
            string += '\n' + str(state) + '\n'
        return string
