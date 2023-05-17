import random
import numpy as np


# ranges of state variables
RANGE = {
    'bird_y': [140, 720],
    'gap_x': [90, 400],
    'gap_y': [300, 550]
}
# size of buckets
BUCKET_SIZE = [2, 50, 2]
# num of buckets
bucket_num = [int(i) for i in [
    (RANGE['bird_y'][1] - RANGE['bird_y'][0]) / BUCKET_SIZE[0],
    (RANGE['gap_x'][1] - RANGE['gap_x'][0]) / BUCKET_SIZE[1],
    (RANGE['gap_y'][1] - RANGE['gap_y'][0]) / BUCKET_SIZE[2]
                                ]]


def mapping(sample, start, bucket_size):
    index = (sample - start) // bucket_size
    return int(index)


def map_state_to_index(state):
    # Todo: Take into your account that ... There is a special state at the start of the game "pipe_x variable is at the very right"
    """
    # input form:
    state = {
        'bird_y':
        'bird_v':
        'pipe_positions':
        'score':
        'game_state':
    }
    """
    bird_y = mapping(state['bird_y'], RANGE['bird_y'][0], BUCKET_SIZE[0])

    bird_v = 1
    if state['bird_v'] < 0:
        bird_v = 0

    pipe_x = mapping(state['pipe_positions'][0], RANGE['gap_x'][0], BUCKET_SIZE[1])
    pipe_x = pipe_x if pipe_x < bucket_num[1] else bucket_num[1]
    pipe_y = mapping(state['pipe_positions'][1], RANGE['gap_y'][0], BUCKET_SIZE[2])

    indexes = (
        bird_y,
        bird_v,
        pipe_x,
        pipe_y
    )

    return indexes  # It's a tuple to be used in indexing a np array


class Q_learn:
    def __init__(self, state):
        self.init_state_index = map_state_to_index(state)
        self.state_index = self.init_state_index
        self.next_state_index = None
        self.action_index = 1
        # Initialize Q-table
        self.num_states = (bucket_num[0],  # num of bird_y buckets
                           2,   # num of bird_velocity buckets
                           bucket_num[0] + 1,  # num of gap_x buckets
                           bucket_num[0]   # num of gap_y buckets
                           )
        self.num_actions = (2,)  # It's a tuple
        try:
            self.Q = np.load("./q_table.npy")
        except FileNotFoundError:
            self.Q = np.zeros(self.num_states + self.num_actions)

        # Set hyper parameters
        self.alpha = 0.3
        self.gamma = 0.9
        self.num_episodes = 0

        # Define epsilon (the exploration rate)
        self.epsilon = 0.1

    def reset(self):
        self.state_index = self.init_state_index
        self.action_index = 1

    # Define a function to select an action using epsilon-greedy strategy
    def epsilon_greedy(self, state_index):
        # Choose a random action with probability epsilon
        if random.uniform(0, 1) < self.epsilon:
            action_index = random.randrange(0, self.Q[state_index].size)
        # Otherwise, choose the action with the highest Q-value
        else:
            max_value = max(self.Q[state_index])
            actions_indices = [i for i, v in enumerate(self.Q[state_index]) if v == max_value]
            action_index = random.choice(actions_indices)

        self.action_index = action_index
        return action_index

    def take_action(self, state, exploration=True):
        """
        It maps "action_index = 1" to "jump"
        and "action_index = 0" to " " meaning no jump
        """
        state_index = map_state_to_index(state)
        if exploration:  # True during learning
            action = "jump" if self.epsilon_greedy(state_index) else " "
        else:
            max_value = max(self.Q[state_index])
            actions_indices = [i for i, v in enumerate(self.Q[state_index]) if v == max_value]
            action_index = random.choice(actions_indices)
            action = "jump" if action_index else " "
        return action

    # Q-learning algorithm
    def learn(self, state, reward, done=False):
        self.next_state_index = map_state_to_index(state)
        # Update Q-value for state-action pair
        td_error = reward + self.gamma * np.max(self.Q[self.next_state_index]) - self.Q[self.state_index + (self.action_index,)]
        self.Q[self.state_index + (self.action_index,)] += self.alpha * td_error

        # update state
        self.state_index = self.next_state_index

        # when episode ends reset the agent
        if done:
            self.reset()
            # print number of complete episodes
            # print(self.num_episodes)
            self.num_episodes += 1
            # save Q_table each 100 episodes
            if self.num_episodes % 100 == 0:
                np.save("./q_table.npy", self.Q, allow_pickle=True)
