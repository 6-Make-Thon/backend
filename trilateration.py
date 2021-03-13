import scipy
from scipy.optimize import least_squares


class trilateration:
    array = []
    initial_guess = (0, 0, 0)

    def equations(self, guess):
        x, y, r = guess
        returnarray = []
        for item in self.array:
            returnarray.append((x - item['x'])**2 + (y - item['y'])**2 - (item['dist'] - r )**2)
        return returnarray

    def __init__(self, inputdict):

        self.array = inputdict

    def calc(self):
        results = least_squares(self.equations, self.initial_guess)
        return results.x

