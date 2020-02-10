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
global_food = list()
score = 0
switch = False
moves = 0
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
    global global_food, score, switch
    prev = self.getPreviousObservation()
    if prev != None:
      global_food = self.getFood(prev).asList()
    food_list = self.getFood(gameState).asList()
    # print str(len(global_food)) + " : " + str(len(food_list))
    if (len(global_food) > len(food_list)) and gameState.getAgentState(self.index).isPacman:
      global_food = food_list[:]
      food_list = self.getFoodYouAreDefending(gameState).asList()
      switch = True
    if not gameState.getAgentState(self.index).isPacman and self.index == attacking:
      switch = False
    if switch:
      if self.getScore(gameState) != score:
        score = self.getScore(gameState)
        switch = False
      else:
        return self.attack_home(gameState)
    if self.index == defending:
      return self.defend(gameState)
    else:
      return self.attack(gameState)

  def attack_home(self, gameState):
    food_list = self.getFoodYouAreDefending(gameState).asList()
    upperLimit = 9999
    closest_pellet = food_list[0]
    for pellet in food_list:
      distance = self.getMazeDistance(pos1=gameState.getAgentPosition(index=self.index), pos2=pellet)
      if distance < upperLimit:
        closest_pellet = pellet
        upperLimit = distance
    actions = gameState.getLegalActions(self.index)
    best_action = Directions.STOP
    upperLimit = 9999
    for action in actions:
      future_state = gameState.generateSuccessor(agentIndex=self.index, action=action)
      distance = self.getMazeDistance(pos1=future_state.getAgentPosition(index=self.index), pos2=closest_pellet)
      if distance < upperLimit:
        best_action = action
        upperLimit = distance
    return best_action if best_action != None else Directions.STOP

  def attack(self, gameState):
    global moves
    moves += 1
    food_list = self.getFood(gameState).asList()
    upperLimit = 9999
    closest_pellet = food_list[0]
    for pellet in food_list:
      distance = self.getMazeDistance(pos1=gameState.getAgentPosition(index=self.index), pos2=pellet)
      if distance < upperLimit:
        closest_pellet = pellet
        upperLimit = distance
    if moves % 5 == 0:
      closest_pellet = random.choice(food_list)
    actions = gameState.getLegalActions(self.index)
    best_action = Directions.STOP
    upperLimit = 9999
    for action in actions:
      future_state = gameState.generateSuccessor(agentIndex=self.index, action=action)
      distance = self.getMazeDistance(pos1=future_state.getAgentPosition(index=self.index), pos2=closest_pellet)
      if distance < upperLimit:
        best_action = action
        upperLimit = distance
    return best_action if best_action != None else Directions.STOP



  def defend(self, gameState):
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
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
