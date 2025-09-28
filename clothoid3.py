import numpy as np
import scipy.integrate
import matplotlib.pyplot as plt

#RATE_WHEEL_TURN = 1
SPEED = 1
#CENTER0_x = 0
#CENTER0_y = 0

# Use scipy.integrate.solve_ivp
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html


def fix_trigger(X0):
    # Prevent triggering on first event
    # https://stackoverflow.com/questions/63453965/scipy-solve-ivp-terminate-trajectory-on-second-occurrence-of-event
    theta,thetadot,x,y = X0
    X0 = (theta + 1.e-15*np.sign(thetadot), thetadot, x, y)
    return X0

class ClothoidState:
    def __init__(self, X0, rate_wheel_turn):
        self.rate_wheel_turn = rate_wheel_turn
        self.X0 = fix_trigger(X0)

        theta,thetadot,x,y = X0
        self.r0 = SPEED / thetadot

        # Determine center of the ORIGINAL circle
        phi = theta - 0.5*np.pi
        r = SPEED / thetadot
        self.center0 = (x - r * np.cos(phi), y - r * np.sin(phi))


def dX_dt(self, X, state):
    """Clothoid Loop is an initial value problem for the vector X with variables:
        theta:
            Direction of travel
        thetadot:
            Rate of change of direction of travel
        x,y:
            Coordinates of current position in Cartesian space.

    This function computes the derivative of X with respect to time,
    and allows for Runge-Kutta integration.

    Returns: np.array
        [dtheata/dt, dthetadot/dt, dx/dt, dy/dt]
    """

    theta,thetadot,x,y = X
    phi = theta - 0.5*np.pi
    return np.array([
        thetadot,
        state.rate_wheel_turn,
        -np.sin(phi),
        np.cos(phi)])       



def at_top(t, X, state):
    """This is an event... it equals 0 when we are at the top of the
    loop and need to reverse course."""

    theta,thetadot,x,y = X
    phi = theta - 0.5*np.pi
    r = SPEED / thetadot
    center = (x - r * np.cos(phi), y - r * np.sin(phi))
    vel = (SPEED * np.cos(theta), SPEED * np.sin(theta))
    rad = (x - state.center0[0], y - state.center0[1])
    # dp determines wheter we are perpindicular to the main circle radius.
    dp = vel[0]*rad[0] + vel[1]*rad[1]
    print('dp ', theta, dp)
    return dp

at_top.terminal = True


def main():
    print('AA1')
#    X0 = (0., 0.2, 0., 0.)
    X0 = (0., 0.2, 0., 0.)
    state = ClothoidState(X0, 1)
    ret = scipy.integrate.solve_ivp(dX_dt, (0.,10.), state.X0, events=(at_top,), args=(state,), max_step=.01)
    print(ret)

    theta,thetadot,x,y = ret.y 
    fig,ax = plt.subplots()
    ax.set_aspect('equal')

    plt.plot(x,y)


    X0 = fix_trigger((theta[-1], thetadot[-1], x[-1], y[-1]))
    state.rate_wheel_turn *= -1
    ret = scipy.integrate.solve_ivp(dX_dt, (ret.t[-1],ret.t[-1]*2), X0, events=(at_top,), args=(state,), max_step=.01)
    theta,thetadot,x,y = ret.y 
    plt.plot(x,y)


    plt.show()  


main()





def prognostics(t, X, state):
    theta,thetadot,x,y = X

    diff = (x - state.center0[0], y - state.center0[1])
    diff_len = np.sqrt(diff[0]*diff[0] + diff[1]*diff[1])
    big_circle[0] = center0[0] + (r0 / diff_len) * diff[0]
    big_circle[1] = center0[1] + (r0 / diff_len) * diff[1]

    diff2[0] = big_circle[0] - x
    diff2[1] = big_circle[1] - y
    offcircle = np.sqrt(diff2[0]*diff2[0] + diff2[1]*diff2[1])

    return [big_circle[0], big_circle[1], offcircle]
    


