from scipy.interpolate import BSpline as scipy_bspline
import numpy as np


class Curve:
    def __init__(
        self,
        knot_vector: list,
        coefficients: list,
        degree: int = 0,
        verbose: bool = False,
    ):
        """Creates a B-Spline curve or its derivatives.

        Args:
            knot_vector (float array): [t0, t1, t2, ... tK]
                len(knot_vector) = len(coef) + (degree + 1)
                (K+1) knots, K knot spans
                must have length of two or more
                must be a non-decreasing sequence
            coefficients (float array):
                spline coefficients [c0, c1, c2, ... cn]
            degree (int >= 0): B-spline polynomial degree
            verbose (bool): prints extended error checking, default False

        Example:
            # This example implements part of the unit test method
            # test_003_curve_basis_recover_bezier_linear in test_bspline.py unit test.
            #
            > cd ~/sibl
            > conda activate siblenv
            > python
            >>> import numpy as np
            >>> import ptg.bspline as bsp
            >>> kv = list(map(float, [0, 0, 1, 1]))
            >>> degree = 1
            >>> coef_N0_p1 = [1.0, 0.0]
            >>> N0_p1 = bsp.Curve(kv, coef_N0_p1, degree)
            >>> N0_p1.is_valid()
            True
            >>> tmin, tmax, npts = 0.0, 1.0, 5
            >>> t = np.linspace(tmin, tmax, npts, endpoint=True)
            >>> y = N0_p1.evaluate(t)
            >>> y
            array([1.  , 0.75, 0.5 , 0.25, 0.  ])
        """
        self.kv = knot_vector
        self.c = coefficients
        self.p = degree
        self.verbose = verbose
        self.valid = False
        self._bspline = None
        # self.is_valid()  # not sure if I want to call or not, to be determined

    def is_valid(self):

        try:
            assert len(self.kv) >= 2, "Error: knot vector mininum length is two."
            assert self.p >= 0, "Error: degree must be non-negative."

            assert (
                len(self.kv) == len(self.c) + self.p + 1
            ), "Error: knot vector length is invalid."

            self.valid = True
            self._bspline = scipy_bspline(self.kv, self.c, self.p, extrapolate=False)
            return self.valid

        except AssertionError as error:
            if self.verbose:
                print(error)
            return error

    def evaluate(self, t):
        """Evaluate the BSpline curve at all points `t`."""

        # y = np.nan_to_num(self._bspline(t), nan=0.0)
        # y = self._bspline(t)
        # return y
        return self._bspline(t)


class Surface:
    def __init__(
        self,
        knot_vector_t: list,
        knot_vector_u: list,
        coefficients: list,
        degree_t: int = 0,
        degree_u: int = 0,
        n_bisection_intervals: int = 1,
        verbose: bool = False,
    ):
        """Creates a B-Spline surface.

        Args:
            knot_vector_t (list): knot vector for curve parameterized by `t`.
            knot_vector_u (list): knot vector for curve parameterized by `u`.
            coefficients (float array): control net/grid of points with
                coordinates (x, y, z), as in
                [
                    [[x, y, z]_c00, [x, y, z]_c02, ... [x, y, z]_c0m],
                    [[x, y, z]_cn0, [x, y, z]_cn1, ... [x, y, z]_cnm]
                ]
            degree_t: (int >=0): B-spline polynomial degree for spline in `t`.
                Defaults to 0.
            degree_u: (int >=0): B-spline polynomial degree for spline in `u`.
                Defaults to 0.
            n_bisection_intervals (int): Number of bisection intervals per knot span.
                Defaults to 1.
            verbose (bool): prints extended error checking, default False

        Example:
            To come.
        """
        # ncp_t: number of control points for the t parameter
        # ncp_u: number of control points for the u parameter
        # nsd: number of space dimensions, typically 2 or 3
        self.valid = False
        self.ncp_t, self.ncp_u, self.nsd = np.array(coefficients).shape

        knots_t_lhs = knot_vector_t[0:-1]  # left-hand-side knot values for t
        knots_t_rhs = knot_vector_t[1:]  # right-hand-side knot values for t
        knot_t_spans = np.array(knots_t_rhs) - np.array(knots_t_lhs)
        dt = knot_t_spans / (2.0 ** n_bisection_intervals)
        assert all([dti >= 0 for dti in dt]), "Error: knot vector T is decreasing."
        num_knots_t = len(knot_vector_t)
        t = [
            knots_t_lhs[k] + j * dt[k]
            for k in np.arange(num_knots_t - 1)
            for j in np.arange(2 ** n_bisection_intervals)
        ]
        t.append(knot_vector_t[-1])
        t = np.array(t)
        # retain only non-repeated evaluation points at beginning and end
        t_repeated_index = 2 ** n_bisection_intervals * degree_t
        t = t[t_repeated_index:-t_repeated_index]

        knots_u_lhs = knot_vector_u[0:-1]  # left-hand-side knot values for u
        knots_u_rhs = knot_vector_u[1:]  # right-hand-side knot values for u
        knot_u_spans = np.array(knots_u_rhs) - np.array(knots_u_lhs)
        du = knot_u_spans / (2.0 ** n_bisection_intervals)
        assert all([duj >= 0 for duj in du]), "Error: knot vector U is decreasing."
        num_knots_u = len(knot_vector_u)
        u = [
            knots_u_lhs[k] + j * du[k]
            for k in np.arange(num_knots_u - 1)
            for j in np.arange(2 ** n_bisection_intervals)
        ]
        u.append(knot_vector_u[-1])
        u = np.array(u)
        # retain only non-repeated evaluation points at beginning and end
        u_repeated_index = 2 ** n_bisection_intervals * degree_u
        u = u[u_repeated_index:-u_repeated_index]

        self.x_of_t_u = np.zeros((len(t), len(u)), dtype=float)
        self.y_of_t_u = np.zeros((len(t), len(u)), dtype=float)
        self.z_of_t_u = np.zeros((len(t), len(u)), dtype=float)

        ix = 0  # x-coordinate index
        iy = 1  # y-coordinate index
        iz = 2  # z-coordinate index

        for i in np.arange(self.ncp_t):
            for j in np.arange(self.ncp_u):
                print(f"(i, j) = ({i}, {j})")

                N_coef_t = np.zeros(self.ncp_t)
                N_coef_u = np.zeros(self.ncp_u)

                N_coef_t[i] = 1.0
                N_coef_u[j] = 1.0

                Ni = Curve(knot_vector_t, N_coef_t, degree_t)
                Nj = Curve(knot_vector_u, N_coef_u, degree_u)

                if Ni.is_valid() and Nj.is_valid():
                    Ni_of_t = Ni.evaluate(t)
                    Nj_of_u = Nj.evaluate(u)
                    Nij = np.outer(Ni_of_t, Nj_of_u)

                    coef_x = coefficients[i][j][ix]
                    coef_y = coefficients[i][j][iy]
                    coef_z = coefficients[i][j][iz]

                    self.x_of_t_u += Nij * coef_x
                    self.y_of_t_u += Nij * coef_y
                    self.z_of_t_u += Nij * coef_z

        self.valid = True
