
RATE_WHEEL_TURN = 1
SPEED = 1
CENTER0_x = 0
CENTER0_y = 0

# Use scipy.integrate.solve_ivp
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html


class Clothoid:
    def __init__(self, X0):
        self.X0 = X0
        theta0,thetadot0,x0,y0 = X
        self.r0 = SPEED / thetadot0

    def dX_dt(self, X):
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
            RATE_WHEEL_TURN,
            -np.sin(phi),
            cos(phi)])       


    def at_top(t, X):
        """This is an event... it equals 0 when we are at the top of the
        loop and need to reverse course."""

        theta,thetadot,x,y = X
        phi = theta = 0.5*np.pi
        r = SPEED / thetadot
        center_x = x - r * np.cos(phi)
        center_y = y - r * np.sin(phi)
        vel_x = speed * np.cos(theta)
        vel_y = speed * np.sin(theta)
        rad_x = x - CENTER0_x
        rad_y = y - CENTER0_y
        dp = vel_x*rad*x + vel_y*rad_y
        return dp

    def prognostics(t, X):
        theta,thetadot,x,y = X

        diff_x = x - CENTER0_y
        diff_y = y - CENTER0_y
        diff_len = np.sqrt(diff_x*diff_x + diff_y*diff_y)
        big_circle_x = CENTER0_x + (r0 / diff_len) * diff_x
        big_circle_y = CENTER0_y + (r0 / diff_len) * diff_y

        diff2_x = big_circle_x - x
        diff2_y = big_circle_y - y
        offcircle = np.sqrt(diff2_x*diff2_x + diff2_y*diff2_y)

        return [big_circle_x, big_circle_y, offcircle]
    

at_top.terminal = True
