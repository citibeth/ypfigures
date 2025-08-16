class _State(typing.NamedTuple):
#    speed: float
    t: float
    xy: object        # Prognostics
    theta: float
    dtheta_dt: float
    r: float            # Derived
    center: np.array
    vel: np.array
    dp: float
    offcircle: float   # Distance we are in from the center00 circle


def State(t, center00, r00, speed, xy, theta, dtheta_dt):
    phi = theta - 0.5*np.pi
    r = speed / dtheta_dt
    center = xy - r * np.array([np.cos(phi), np.sin(phi)])
    vel = speed * np.array([np.cos(theta), np.sin(theta)])
    rad = xy - center00
    dp = vel[0]*rad[0] + vel[1]*rad[1]

    diff = xy - center00
    diff_len = np.sqrt(diff[0]*diff[0] + diff[1]*diff[1])
    big_circle_xy = center00 + (r00 / diff_len) * diff
    diff = big_circle_xy - xy
    offcircle = np.sqrt(diff[0]*diff[0] + diff[1]*diff[1])
    
    return _State(t, xy, theta, dtheta_dt, r, center, vel, dp, offcircle)

def step_forward(center00, r00, speed, d2theta_dt2, state0, dt):
    # Prognostics for Next Step
    t = state0.t + dt
    theta1 = state0.theta + state0.dtheta_dt * dt
    dtheta_dt1 = state0.dtheta_dt + d2theta_dt2 * dt
    phi0 = state0.theta - 0.5*np.pi
    phi1 = theta1 - 0.5*np.pi
    xy1 = state0.xy + state0.r * np.array([
        np.cos(phi1) - np.cos(phi0),
        np.sin(phi1) - np.sin(phi0)])

    # Update prognostics
    state1 = State(t, center00, r00, speed, xy1, theta1, dtheta_dt1)
    return state1

def add_line(lines, state):
    lines.append((state.t, state.xy[0], state.xy[1], state.theta, state.center[0], state.center[1], state.r, state.dp, state.offcircle))


def spiral(xy0, theta0, dtheta_dt0, d2theta_dt2, t0, t1, dt):
    xy0 = np.array(xy0)
    speed = 1.
    state = State(t0, 0, 1, speed, xy0, theta0, dtheta_dt0)
    center00 = state.center
    r00 = state.r
    state0 = State(t0, center00, r00, speed, xy0, theta0, dtheta_dt0)
    lines = list()

    for nstep,t in enumerate(np.arange(t0, t1, dt)):
        # Diagnostics for this step
        add_line(lines, state0)

        state1 = step_forward(center00, r00, speed, d2theta_dt2, state0, dt)

        # Check to see if we've turned the corner; now find the specific top
        if (state1.r < 0.5*r00) and (np.sign(state1.dp) != np.sign(state0.dp)):
            state_last = state0
            # Now state0 is the last step before the top, and state1 is the
            # last step after the top.  Use bisection method
            direction = np.sign(state1.dp - state0.dp)
            #print('ddd ', direction, state0.dp, state1.dp)
            while np.abs(state1.dp - state0.dp) > 1.e-13:
                #print(state0.t, state1.t, state0.dp, state1.dp)
                _dt = (state1.t - state0.t) * 0.5
                statex = step_forward(center00, r00, speed, d2theta_dt2, state0, _dt)
                if np.sign(statex.dp) == np.sign(state0.dp):
                    state0 = statex
                else:
                    state1 = statex
            print('Top is at ', state1.t)
            add_line(lines, state1)
        
            # Now reverse....
            _dt = state1.t - state_last.t
            print('_dt ', _dt)
            state0 = step_forward(center00, r00, speed, -d2theta_dt2, state1, _dt)
            add_line(lines, state0)
        
            for ix in range(nstep):
                state1 = step_forward(center00, r00, speed, -d2theta_dt2, state0, dt)
                add_line(lines, state1)
                state0 = state1

            break

        state0 = state1


    
    return pd.DataFrame(lines, columns=('t', 'x', 'y', 'theta', 'centerx', 'centery', 'r', 'dp', 'offcircle'))
