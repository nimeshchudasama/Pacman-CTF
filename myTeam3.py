# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from capture import GameState

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.defender_steps = 0
    self.defender_switch = True

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)
    '''
    You should change this in your own agent.
    '''
    myTeam = self.getTeam(gameState=gameState)
    defending = max(myTeam)
    attacking = min(myTeam)

    if gameState.getAgentState(attacking).isPacman:
      self.defender_switch = False

    if self.index == defending:
      ans = self.defend(gameState)
      return ans
    else:
      ans = self.attack(gameState)
      return ans

  def defend(self, gameState):
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    self.defender_steps += 1
    # print "Defender Steps: " + str(self.defender_steps) + ", Defender Switch: " + str(self.defender_switch)
    if self.defender_steps < 5:
      return Directions.STOP
    # if self.defender_switch:
    #   return self.attack(gameState)
    if len(invaders) <= 0:
      return Directions.STOP

    enemy = invaders[0].getPosition()
    myPos = gameState.getAgentState(self.index).getPosition()
    if len(invaders) > 0:
      upperLimit = 9999
      for invader in invaders:
        distance = self.getMazeDistance(pos1=gameState.getAgentPosition(index=self.index), pos2=invader.getPosition())
        if distance < upperLimit:
          enemy = invader.getPosition()
          upperLimit = distance

    actions = gameState.getLegalActions(self.index)
    best_action = Directions.STOP
    upperLimit = 9999
    for action in actions:
      future_state = gameState.generateSuccessor(agentIndex=self.index, action=action)
      distance = self.getMazeDistance(pos1=future_state.getAgentState(index=self.index).getPosition(), pos2=enemy)
      if distance < upperLimit:
        best_action = action
        upperLimit = distance
    return best_action if best_action != None else Directions.STOP

  def follow_attacker(self, gameState):
    pass

  def attack(self, gameState):
    return self.maximizer(gameState, 0, -99999, 99999)

  def evaluationFunction(self, gameState):
    # sum(food_distances from current position)
    food_list = self.getFood(gameState).asList()
    food_distances = []
    distance_sum = 0
    for pellet in food_list:
      distance = self.getMazeDistance(pos1=gameState.getAgentPosition(self.index), pos2=pellet)
      distance_sum += distance
      food_distances.append([pellet, distance])
    # sum(capsule_distances from current position)
    enemy_capsules = self.getCapsules(gameState)
    capsule_distances = []
    capsule_sum = 0
    for capsule in enemy_capsules:
      distance = self.getMazeDistance(pos1=gameState.getAgentPosition(self.index), pos2=capsule)
      capsule_sum += distance
      capsule_distances.append([capsule, distance])
    # sum(enemy_positions[ghosts] from current position
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    enemy_defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    enemy_distances = []
    enemy_sum = 0
    for defender in enemy_defenders:
      distance = self.getMazeDistance(pos1=gameState.getAgentPosition(self.index), pos2=defender.getPosition())
      enemy_sum += distance
      enemy_distances.append([defender, distance])
    # print "Distance Sum: " + str(distance_sum)
    # print "Capsule Sum:  " + str(capsule_sum)
    # print "Enemy Sum:    " + str(enemy_sum)
    if distance_sum == 0:
      distance_sum = 100
    if capsule_sum == 0:
      capsule_sum = 65
    if enemy_sum == 0:
      enemy_sum = -10
    # linear combination sum( w_i * x_i )
    x_1 = float(float(1.00) / distance_sum)
    x_2 = float(float(1.00) / capsule_sum)
    x_3 = float(float(1.00) / enemy_sum)

    # print "x_1: " + str(x_1)
    # print "x_2: " + str(x_2)
    # print "x_3: " + str(x_3)

    w_1 = float(100.00)
    w_2 = float(65.00)
    w_3 = float(-10.00)
    # print str(self.index) + " : " + str(float(w_1 * x_1 + w_2 * x_2 + w_3 * x_3))
    return w_1 * x_1 + w_2 * x_2 + w_3 * x_3

  def maximizer(self, gameState, depth, alpha, beta):
    if gameState.isOver():
      return gameState.getScore()
    if depth >= 3:
      return self.evaluationFunction(gameState)
    actions = gameState.getLegalActions(self.index)
    best_score = -9999
    best_action = Directions.STOP
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      score = self.minimizer(successor, depth + 1, alpha, beta)
      if score > best_score:
        best_score = score
        best_action = action
      alpha = max(alpha, best_score)
      if alpha > beta:
        return best_score
    return best_action if depth == 0 else best_score

  def minimizer(self, gameState, depth, alpha, beta):
    if gameState.isOver():
      return gameState.getScore()
    if depth >= 3:
      return self.evaluationFunction(gameState)
    actions = gameState.getLegalActions(self.index)
    best_score = 9999
    best_action = Directions.STOP
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      score = self.maximizer(successor, depth + 1, alpha, beta)
      if score < best_score:
        best_score = score
        best_action = action
      beta = min(beta, best_score)
      if alpha > beta:
        return best_score
    return best_score
