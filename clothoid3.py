import numpy as np
import scipy.integrate
import matplotlib.pyplot as plt

#RATE_WHEEL_TURN = 1
#SPEED = 1
#CENTER0_x = 0
#CENTER0_y = 0

# Use scipy.integrate.solve_ivp
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html


def fix_trigger(X0):
    # Prevent triggering on first event
    # https://stackoverflow.com/questions/63453965/scipy-solve-ivp-terminate-trajectory-on-second-occurrence-of-event
    theta,thetadot,x,y,speed = X0
    X0 = (theta + 1.e-5*np.sign(thetadot), thetadot, x, y, speed)
    return X0

class ClothoidState:
    def __init__(self, X0, rate_wheel_turn, rate_accel):
        self.rate_wheel_turn = rate_wheel_turn
        self.rate_accel = rate_accel
        self.X0 = fix_trigger(X0)

        theta,thetadot,x,y,speed = X0
        self.r0 = speed / thetadot

        # Determine center of the ORIGINAL circle
        phi = theta - 0.5*np.pi
        r = speed / thetadot
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

    theta,thetadot,x,y,speed = X
    phi = theta - 0.5*np.pi
    return np.array([
        thetadot,
        state.rate_wheel_turn,
        -speed * np.sin(phi),
        speed * np.cos(phi),
        state.rate_accel * thetadot])       



def at_top(t, X, state):
    """This is an event... it equals 0 when we are at the top of the
    loop and need to reverse course."""

    theta,thetadot,x,y,speed = X
    phi = theta - 0.5*np.pi
    r = speed / thetadot
    center = (x - r * np.cos(phi), y - r * np.sin(phi))
    vel = (speed * np.cos(theta), speed * np.sin(theta))
    rad = (x - state.center0[0], y - state.center0[1])
    # dp determines wheter we are perpindicular to the main circle radius.
    dp = vel[0]*rad[0] + vel[1]*rad[1]
#    print('dp ', theta, dp)
    return dp

at_top.terminal = True


def clothoid(X0, rate_wheel_turn, rate_accel):

    state = ClothoidState(X0, rate_wheel_turn=rate_wheel_turn, rate_accel=rate_accel)
    ret = scipy.integrate.solve_ivp(dX_dt, (0.,10.), state.X0, events=(at_top,), args=(state,), max_step=.01)
    theta1,thetadot1,x1,y1,speed1 = ret.y 

    X0 = fix_trigger((theta1[-1], thetadot1[-1], x1[-1], y1[-1], speed1[-1]))
    state.rate_wheel_turn *= -1
    state.rate_accel *= -1
    ret = scipy.integrate.solve_ivp(dX_dt, (ret.t[-1],ret.t[-1]*2), X0, events=(at_top,), args=(state,), max_step=.01)
    theta2,thetadot2,x2,y2,speed2 = ret.y

    return (
        np.concatenate((theta1, theta2)),
        np.concatenate((thetadot1, thetadot2)),
        np.concatenate((x1, x2)),
        np.concatenate((y1, y2)),
        np.concatenate((speed1, speed2)))



def main():
    fig,ax = plt.subplots()
    ax.set_aspect('equal')
    
#    X0 = (0., 0.2, 0., 0., 1.)
    X0 = (0., 1.27, 0., 0., 1)
    for ix in range(6):
        theta,thetadot,x,y,speed = clothoid(X0, rate_wheel_turn=1, rate_accel=-.15*X0[-1])
        plt.plot(x,y)
        X0 = (theta[-1], thetadot[-1], x[-1], y[-1], speed[-1])

    plt.show()

def mainx():
    fig,ax = plt.subplots()
    ax.set_aspect('equal')


#    X0 = (0., 0.2, 0., 0., 1.)
#    state = ClothoidState(X0, rate_wheel_turn=1, rate_accel=-0)
#    ret = scipy.integrate.solve_ivp(dX_dt, (0.,10.), state.X0, events=(at_top,), args=(state,), max_step=.01)
#    theta,thetadot,x,y,speed = ret.y 
#    plt.plot(x,y)

    X0 = (0., 0.2, 0., 0., 1.)
    state = ClothoidState(X0, rate_wheel_turn=1, rate_accel=-.15)
    ret = scipy.integrate.solve_ivp(dX_dt, (0.,10.), state.X0, events=(at_top,), args=(state,), max_step=.01)
    theta,thetadot,x,y,speed = ret.y 
    plt.plot(x,y)






    X0 = fix_trigger((theta[-1], thetadot[-1], x[-1], y[-1], speed[-1]))
    state.rate_wheel_turn *= -1
    state.rate_accel *= -1
    ret = scipy.integrate.solve_ivp(dX_dt, (ret.t[-1],ret.t[-1]*2), X0, events=(at_top,), args=(state,), max_step=.01)
    theta,thetadot,x,y,speed = ret.y 
    plt.plot(x,y)


    plt.show()  


main()





def prognostics(t, X, state):
    theta,thetadot,x,y,speed = X

    diff = (x - state.center0[0], y - state.center0[1])
    diff_len = np.sqrt(diff[0]*diff[0] + diff[1]*diff[1])
    big_circle[0] = center0[0] + (r0 / diff_len) * diff[0]
    big_circle[1] = center0[1] + (r0 / diff_len) * diff[1]

    diff2[0] = big_circle[0] - x
    diff2[1] = big_circle[1] - y
    offcircle = np.sqrt(diff2[0]*diff2[0] + diff2[1]*diff2[1])

    return [big_circle[0], big_circle[1], offcircle]
    


