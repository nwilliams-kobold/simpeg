from .....electromagnetics.static.resistivity.simulation import BaseDCSimulation as Sim
from .....utils import Zero, mkvc
from .....data import Data
import dask
import dask.array as da
from dask.distributed import Future
import numpy as np


Sim.sensitivity_path = './sensitivity/'


def dask_fields(self, m=None, return_Ainv=False):
    if m is not None:
        self.model = m


    A = self.getA()
    Ainv = self.solver(A, **self.solver_opts)
    RHS = self.getRHS()

    f = self.fieldsPair(self, shape=RHS.shape)
    f[:, self._solutionType] = Ainv * RHS

    if return_Ainv:
        return (f, Ainv)
    else:
        del Ainv
        return (f,)


Sim.fields = dask_fields


def dask_getJtJdiag(self, m, W=None):
    """
        Return the diagonal of JtJ
    """
    self.model = m
    if self.gtgdiag is None:
        if isinstance(self.Jmatrix, Future):
            self.Jmatrix  # Wait to finish
        # Need to check if multiplying weights makes sense
        if W is None:
            self.gtgdiag = da.sum(self.Jmatrix ** 2, axis=0).compute()
        else:
            w = da.from_array(W.diagonal())[:, None]
            self.gtgdiag = da.sum((w * self.Jmatrix) ** 2, axis=0).compute()

    return self.gtgdiag


Sim.getJtJdiag = dask_getJtJdiag


def dask_Jvec(self, m, v):
    """
        Compute sensitivity matrix (J) and vector (v) product.
    """
    self.model = m
    if isinstance(self.Jmatrix, Future):
        self.Jmatrix  # Wait to finish

    return da.dot(self.Jmatrix, v)


Sim.Jvec = dask_Jvec


def dask_Jtvec(self, m, v):
    """
        Compute adjoint sensitivity matrix (J^T) and vector (v) product.
    """
    self.model = m
    if isinstance(self.Jmatrix, Future):
        self.Jmatrix  # Wait to finish

    return da.dot(v, self.Jmatrix)


Sim.Jtvec = dask_Jtvec


def compute_J(self, f=None, Ainv=None):

    if f is None:
        f, Ainv = self.fields(self.model, return_Ainv=True)

    m_size = self.model.size

    blocks = []
    for source in self.survey.source_list:
        u_source = f[source, self._solutionType]
        for rx in source.receiver_list:
            PTv = rx.getP(self.mesh, rx.projGLoc(f)).toarray().T
            df_duTFun = getattr(f, "_{0!s}Deriv".format(rx.projField), None)
            df_duT, df_dmT = df_duTFun(source, None, PTv, adjoint=True)
            ATinvdf_duT = Ainv * df_duT
            dA_dmT = self.getADeriv(u_source, ATinvdf_duT, adjoint=True)
            dRHS_dmT = self.getRHSDeriv(source, ATinvdf_duT, adjoint=True)
            du_dmT = -dA_dmT
            if not isinstance(dRHS_dmT, Zero):
                du_dmT += dRHS_dmT
            if not isinstance(df_dmT, Zero):
                du_dmT += df_dmT

            blocks += [du_dmT.T]

    Jmatrix = da.to_zarr(
        da.vstack(blocks).rechunk('auto'), self.sensitivity_path + "J.zarr",
        compute=True, return_stored=True, overwrite=True
    )
    del Ainv, f, blocks
    return Jmatrix


Sim.compute_J = compute_J


# This could technically be handled by dask.simulation, but doesn't seem to register
@dask.delayed
def dask_dpred(self, m=None, f=None, compute_J=False):
    """
    dpred(m, f=None)
    Create the projected data from a model.
    The fields, f, (if provided) will be used for the predicted data
    instead of recalculating the fields (which may be expensive!).

    .. math::

        d_\\text{pred} = P(f(m))

    Where P is a projection of the fields onto the data space.
    """
    if self.survey is None:
        raise AttributeError(
            "The survey has not yet been set and is required to compute "
            "data. Please set the survey for the simulation: "
            "simulation.survey = survey"
        )

    if f is None:
        if m is None:
            m = self.model
        f, Ainv = self.fields(m, return_Ainv=True)

    data = Data(self.survey)
    for src in self.survey.source_list:
        for rx in src.receiver_list:
            data[src, rx] = rx.eval(src, self.mesh, f)

    if compute_J:
        Jmatrix = self.compute_J(f=f, Ainv=Ainv)
        del f, Ainv
        return (mkvc(data), Jmatrix)

    del f, Ainv
    return mkvc(data)


Sim.dpred = dask_dpred


def dask_getSourceTerm(self):
    """
    Evaluates the sources, and puts them in matrix form
    :rtype: tuple
    :return: q (nC or nN, nSrc)
    """

    if getattr(self, "_q", None) is None:


        if self._mini_survey is not None:
            Srcs = self._mini_survey.source_list
        else:
            Srcs = self.survey.source_list

        if self._formulation == "EB":
            n = self.mesh.nN
            # return NotImplementedError

        elif self._formulation == "HJ":
            n = self.mesh.nC

        q = np.zeros((n, len(Srcs)), order="F")

        for i, source in enumerate(Srcs):
            q[:, i] = source.eval(self)

        self._q = q

    return self._q

Sim.getSourceTerm = dask_getSourceTerm