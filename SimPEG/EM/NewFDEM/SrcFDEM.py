import properties
import numpy as np
from scipy.constants import mu_0
import warnings

from SimPEG.Utils import Zero
from SimPEG import Survey, Simulation, Utils

from .. import Utils as emutils
from ..NewBase import BaseEMSrc
from .RxFDEM import BaseFDEMRx

import warnings

__all__ = [
    'RawVec', 'RawVec_m', 'RawVec_e', 'MagDipole', 'MagDipole_Bfield',
    'CircularLoop', 'PrimSecSigma', 'PrimSecMappedSigma'
]


###############################################################################
#                                                                             #
#                            Base FDEM Source                                 #
#                                                                             #
###############################################################################

class BaseFDEMSrc(BaseEMSrc):
    """
    Base source class for FDEM Survey. Inherit this to build your own FDEM
    source.
    """

    frequency = properties.Float(
        "frequency of the source",
        min=0, required=True
    )

    rxList = properties.List(
        "list of FDEM receivers",
        properties.Instance(BaseFDEMRx),
        default=[]
    )

    def __init__(self, **kwargs):
        freq = kwargs.pop('freq', None)
        if freq is not None:
            warnings.warn(
                "the keyword argument 'freq' will be depreciated in favour of "
                "'frequency' please use src(frequency={}) to create the "
                "source".format(freq)
            )
            kwargs['frequency'] = freq
        super(BaseFDEMSrc, self).__init__(**kwargs)

    def bPrimary(self, simulation):
        """
        Primary magnetic flux density

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: primary magnetic flux density
        """
        if getattr(self, '_bPrimary', None) is None:
            self._bPrimary = Utils.Zero()
        return self._bPrimary

    def bPrimaryDeriv(self, simulation, v, adjoint=False):
        """
        Derivative of the primary magnetic flux density

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :param numpy.ndarray v: vector
        :param bool adjoint: adjoint?
        :rtype: numpy.ndarray
        :return: primary magnetic flux density
        """
        return Zero()

    def hPrimary(self, simulation):
        """
        Primary magnetic field

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """
        if getattr(self, '_hPrimary', None) is None:
            self._hPrimary = Utils.Zero()
        return self._hPrimary

    def hPrimaryDeriv(self, simulation, v, adjoint=False):
        """
        Derivative of the primary magnetic field

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :param numpy.ndarray v: vector
        :param bool adjoint: adjoint?
        :rtype: numpy.ndarray
        :return: primary magnetic flux density
        """
        return Zero()

    def ePrimary(self, simulation):
        """
        Primary electric field

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: primary electric field
        """
        if getattr(self, '_ePrimary', None) is None:
            self._ePrimary = Utils.Zero()
        return self._ePrimary

    def ePrimaryDeriv(self, simulation, v, adjoint=False):
        """
        Derivative of the primary electric field

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :param numpy.ndarray v: vector
        :param bool adjoint: adjoint?
        :rtype: numpy.ndarray
        :return: primary magnetic flux density
        """
        return Zero()

    def jPrimary(self, simulation):
        """
        Primary current density

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: primary current density
        """
        if getattr(self, '_jPrimary', None) is None:
            self._jPrimary = Utils.Zero()
        return self._jPrimary

    def jPrimaryDeriv(self, simulation, v, adjoint=False):
        """
        Derivative of the primary current density

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :param numpy.ndarray v: vector
        :param bool adjoint: adjoint?
        :rtype: numpy.ndarray
        :return: primary magnetic flux density
        """
        return Zero()


###############################################################################
#                                                                             #
#                             Raw Vec Sources                                 #
#                                                                             #
###############################################################################

class RawVec_e(BaseFDEMSrc):
    """
    RawVec electric source. It is defined by the user provided vector s_e

    :code:`src = Src.RawVec_e(rxList=rxList, frequency=frequency, vec_m=vec_m)`
    """

    # TODO: Think about this name - not a fan of this at the moment.
    vec_e = properties.Array(
        "vector source term",
        dtype=complex
    )

    def __init__(self, **kwargs):
        s_e = kwargs.pop("s_e", None)
        if s_e is not None:
            warnings.warn(
                "The key word 's_e' will be depreciated. Please use vec_e=s_e"
            )
            self.vec_e = s_e
        super(BaseFDEMSrc, self).__init__(**kwargs)

    def s_e(self, simulation):
        """
        Electric source term

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: electric source term on mesh
        """
        if simulation._formulation == 'EB' and self.integrate is True:
            return simulation.Me * self.vec_e
        return self.vec_e


class RawVec_m(BaseFDEMSrc):
    """
    RawVec magnetic source. It is defined by the user provided vector s_m

    :code:`src = Src.RawVec_m(rxList=rxList, frequency=frequency, vec_m=vec_m)`
    """

    # TODO: Think about this name - not a fan of this at the moment.
    vec_m = properties.Array(
        "vector source term",
        dtype=complex
    )

    def __init__(self, **kwargs):
        s_m = kwargs.pop("s_m", None)
        if s_m is not None:
            warnings.warn(
                "The key word 's_m' will be depreciated. Please use vec_e=s_m"
            )
            self.vec_m = s_m
        super(RawVec_m, self).__init__( **kwargs)

    def s_m(self, simulation):
        """
        Magnetic source term

        :param BaseFDEMSimulation simulation: FDEM Simulation
        :rtype: numpy.ndarray
        :return: magnetic source term on mesh
        """
        if simulation._formulation == 'HJ' and self.integrate is True:
            return simulation.Me * self.vec_m
        return self.vec_m


class RawVec(RawVec_e, RawVec_m):
    """
    RawVec source. It is defined by the user provided vectors vec_m, vec_e

    :code:`src = Src.RawVec(rxList=rxList, frequency=frequency, vec_m=vec_m, vec_e=vec_e)`
    """

    def __init__(self, **kwargs):
        super(RawVec, self).__init__(**kwargs)


###############################################################################
#                                                                             #
#                          Mag Dipole Sources                                 #
#                                                                             #
###############################################################################

class MagDipole(BaseFDEMSrc):
    """
    Point magnetic dipole source calculated by taking the curl of a magnetic
    vector potential. By taking the discrete curl, we ensure that the magnetic
    flux density is divergence free (no magnetic monopoles!).

    This approach uses a primary-secondary in frequency. Here we show the
    derivation for E-B formulation noting that similar steps are followed for
    the H-J formulation.

    .. math::
        \mathbf{C} \mathbf{e} + i \omega \mathbf{b} = \mathbf{s_m} \\\\
        {\mathbf{C}^T \mathbf{M_{\mu^{-1}}^f} \mathbf{b} -
        \mathbf{M_{\sigma}^e} \mathbf{e} = \mathbf{s_e}}

    We split up the fields and :math:`\mu^{-1}` into primary
    (:math:`\mathbf{P}`) and secondary (:math:`\mathbf{S}`) components

    - :math:`\mathbf{e} = \mathbf{e^P} + \mathbf{e^S}`
    - :math:`\mathbf{b} = \mathbf{b^P} + \mathbf{b^S}`
    - :math:`\\boldsymbol{\mu}^{\mathbf{-1}} =
      \\boldsymbol{\mu}^{\mathbf{-1}^\mathbf{P}} +
      \\boldsymbol{\mu}^{\mathbf{-1}^\mathbf{S}}`

    and define a zero-frequency primary problem, noting that the source is
    generated by a divergence free electric current

    .. math::
        \mathbf{C} \mathbf{e^P} = \mathbf{s_m^P} = 0 \\\\
        {\mathbf{C}^T \mathbf{{M_{\mu^{-1}}^f}^P} \mathbf{b^P} -
        \mathbf{M_{\sigma}^e} \mathbf{e^P} = \mathbf{M^e} \mathbf{s_e^P}}

    Since :math:`\mathbf{e^P}` is curl-free, divergence-free, we assume that
    there is no constant field background, the :math:`\mathbf{e^P} = 0`, so our
    primary problem is

    .. math::
        \mathbf{e^P} =  0 \\\\
            {\mathbf{C}^T \mathbf{{M_{\mu^{-1}}^f}^P} \mathbf{b^P} =
            \mathbf{s_e^P}}

    Our secondary problem is then

    .. math::
        \mathbf{C} \mathbf{e^S} + i \omega \mathbf{b^S} =
        - i \omega \mathbf{b^P} \\\\
        {\mathbf{C}^T \mathbf{M_{\mu^{-1}}^f} \mathbf{b^S} -
        \mathbf{M_{\sigma}^e} \mathbf{e^S} =
        -\mathbf{C}^T \mathbf{{M_{\mu^{-1}}^f}^S} \mathbf{b^P}}

    :param list rxList: receiver list
    :param float freq: frequency
    :param numpy.ndarray loc: source location
        (ie: :code:`np.r_[xloc,yloc,zloc]`)
    :param string orientation: 'X', 'Y', 'Z'
    :param float moment: magnetic dipole moment
    :param float mu: background magnetic permeability

    """

    moment = properties.Float(
        "dipole moment of the transmitter", default=1., min=0.
    )

    mu = properties.Float(
        "permeability of the background", default=mu_0, min=0.
    )

    orientation = properties.Vector3(
        "orientation of the source", default='Z', length=1., required=True
    )

    loc = properties.Vector3(
        "Location of the source [x, y, z]", required=True
    )

    def __init__(self, **kwargs):
        super(MagDipole, self).__init__(**kwargs)

    @properties.validator('orientation')
    def _warn_non_axis_aligned_sources(self, change):
        value = change['value']
        axaligned = [
            True for vec in [
                np.r_[1., 0., 0.], np.r_[0., 1., 0.], np.r_[0., 0., 1.]
            ]
            if np.all(value == vec)
        ]
        if len(axaligned) != 1:
            warnings.warn(
                'non-axes aligned orientations {} are not rigorously'
                ' tested'.format(value)
            )

    def _srcFct(self, obsLoc, component):
        return emutils.MagneticDipoleVectorPotential(
            self.loc, obsLoc, component, mu=self.mu, moment=self.moment,
            orientation=self.orientation
        )

    def _get_grids(self, simulation):
        formulation = simulation._formulation

        if formulation == 'EB':
            gridX = simulation.mesh.gridEx
            gridY = simulation.mesh.gridEy
            gridZ = simulation.mesh.gridEz

        elif formulation == 'HJ':
            gridX = simulation.mesh.gridFx
            gridY = simulation.mesh.gridFy
            gridZ = simulation.mesh.gridFz

        return gridX, gridY, gridZ

    def bPrimary(self, simulation):
        """
        The primary magnetic flux density from a magnetic vector potential

        :param BaseFDEMSimulation simulation: FDEM simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """
        formulation = simulation._formulation
        gridX, gridY, gridZ = self._get_grids(simulation)

        if formulation == 'EB':
            C = simulation.mesh.edgeCurl

        elif formulation == 'HJ':
            C = simulation.mesh.edgeCurl.T

        if simulation.mesh._meshType == 'CYL':
            if not simulation.mesh.isSymmetric:
                # TODO ?
                raise NotImplementedError(
                    'Non-symmetric cyl mesh not implemented yet!')
            assert (np.linalg.norm(self.orientation - np.r_[0., 0., 1.]) <
                    1e-6), ('for cylindrical symmetry, the dipole must be '
                            'oriented in the Z direction')
            a = self._srcFct(gridY, 'y')
        else:
            ax = self._srcFct(gridX, 'x')
            ay = self._srcFct(gridY, 'y')
            az = self._srcFct(gridZ, 'z')
            a = np.concatenate((ax, ay, az))

        return C*a

    def hPrimary(self, simulation):
        """
        The primary magnetic field from a magnetic vector potential

        :param BaseFDEMSimulation simulation: FDEM simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """
        b = self.bPrimary(simulation)
        return 1./self.mu * b

    def s_m(self, simulation):
        """
        The magnetic source term

        :param BaseFDEMSimulation simulation: FDEM simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """

        b_p = self.bPrimary(simulation)
        if simulation._formulation == 'HJ':
            b_p = simulation.Me * b_p
        return -1j*emutils.omega(self.freq)*b_p

    def s_e(self, simulation):
        """
        The electric source term

        :param BaseFDEMSimulation simulation: FDEM simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """

        if all(np.r_[self.mu] == np.r_[simulation.mu]):
            return Zero()
        else:
            formulation = simulation._formulation

            if formulation == 'EB':
                mui_s = simulation.mui - 1./self.mu
                MMui_s = simulation.mesh.getFaceInnerProduct(mui_s)
                C = simulation.mesh.edgeCurl
            elif formulation == 'HJ':
                mu_s = simulation.mu - self.mu
                MMui_s = simulation.mesh.getEdgeInnerProduct(mu_s, invMat=True)
                C = simulation.mesh.edgeCurl.T

            return -C.T * (MMui_s * self.bPrimary(simulation))

    def s_eDeriv(self, simulation , v, adjoint=False):
        if not hasattr(simulation , 'muMap') or not hasattr(simulation , 'muiMap'):
            return Zero()
        else:
            formulation = simulation._formulation

            if formulation == 'EB':
                mui_s = simulation.mui - 1./self.mu
                MMui_sDeriv = simulation.mesh.getFaceInnerProductDeriv(mui_s)(
                    self.bPrimary(simulation )
                ) * simulation.muiDeriv
                C = simulation.mesh.edgeCurl

                if adjoint:
                    return -MMui_sDeriv.T * (C * v)

                return -C.T * (MMui_sDeriv * v)

            elif formulation == 'HJ':
                return Zero()
                # raise NotImplementedError
                mu_s = simulation.mu - self.mu
                MMui_s = simulation.mesh.getEdgeInnerProduct(mu_s, invMat=True)
                C = simulation.mesh.edgeCurl.T

                return -C.T * (MMui_s * self.bPrimary(simulation ))


class MagDipole_Bfield(MagDipole):

    """
    Point magnetic dipole source calculated with the analytic solution for the
    fields from a magnetic dipole. No discrete curl is taken, so the magnetic
    flux density may not be strictly divergence free.

    This approach uses a primary-secondary in frequency in the same fashion as
    the MagDipole.
    """

    def __init__(self, **kwargs):
        super(MagDipole_Bfield, self).__init__(**kwargs)

    def _srcFct(self, obsLoc, component):
        return emutils.MagneticDipoleFields(
            self.loc, obsLoc, component, mu=self.mu, moment=self.moment,
            orientation=self.orientation
        )

    def bPrimary(self, simulation):
        """
        The primary magnetic flux density from the analytic solution for
        magnetic fields from a dipole

        :param BaseFDEMSimultation simulation: FDEM simulation
        :rtype: numpy.ndarray
        :return: primary magnetic field
        """

        gridX, gridY, gridZ = self._get_grids(simulation)

        if simulation.mesh._meshType == 'CYL':
            if not simulation.mesh.isSymmetric:
                # TODO ?
                raise NotImplementedError(
                    'Non-symmetric cyl mesh not implemented yet!'
                )
            bx = self._srcfct(gridX, 'x')
            bz = self._srcfct(gridZ, 'z')
            b = np.concatenate((bx, bz))
        else:
            bx = self._srcfct(gridX, 'x')
            by = self._srcfct(gridY, 'y')
            bz = self._srcfct(gridZ, 'z')
            b = np.concatenate((bx, by, bz))

        return Utils.mkvc(b)


class CircularLoop(MagDipole):
    """
    Circular loop magnetic source calculated by taking the curl of a magnetic
    vector potential. By taking the discrete curl, we ensure that the magnetic
    flux density is divergence free (no magnetic monopoles!).

    This approach uses a primary-secondary in frequency in the same fashion as
    the MagDipole.

    :param list rxList: receiver list
    :param float freq: frequency
    :param numpy.ndarray loc: source location
        (ie: :code:`np.r_[xloc,yloc,zloc]`)
    :param string orientation: 'X', 'Y', 'Z'
    :param float moment: magnetic dipole moment
    :param float mu: background magnetic permeability
    """

    radius = properties.Float("radius of the loop", default=1., min=0.)

    def __init__(self, **kwargs):
        super(CircularLoop, self).__init__(**kwargs)

    def _srcFct(self, obsLoc, component):
        return emutils.MagneticLoopVectorPotential(
            self.loc, obsLoc, component, mu=self.mu, radius=self.radius,
            orientation=self.orientation
        )


###############################################################################
#                                                                             #
#                          Primary Secondary Sources                          #
#                                                                             #
###############################################################################

class PrimSecSigma(BaseFDEMSrc):

    # todo this should also allow a vector
    sigma_background = properties.Float(
        "conductivity of the background",
        min=0,
        required=True
    )



    def __init__(self, rxList, freq, sigBack, ePrimary, **kwargs):
        self.sigBack = sigBack

        BaseFDEMSrc.__init__(
            self, rxList, freq=freq, _ePrimary=ePrimary, **kwargs
        )

    def s_e(self, prob):
        return (
            prob.MeSigma - prob.mesh.getEdgeInnerProduct(self.sigBack)
        ) * self.ePrimary(prob)

    def s_eDeriv(self, prob, v, adjoint=False):
        if adjoint:
            return prob.MeSigmaDeriv(self.ePrimary(prob)).T * v
        return prob.MeSigmaDeriv(self.ePrimary(prob)) * v


class PrimSecMappedSigma(BaseFDEMSrc):
    """
    Primary-Secondary Source in which a mapping is provided to put the current
    model onto the primary mesh. This is solved on every model update.
    There are a lot of layers to the derivatives here!

    **Required**
    :param list rxList: Receiver List
    :param float freq: frequency
    :param BaseFDEMProblem primaryProblem: FDEM primary problem
    :param SurveyFDEM primarySurvey: FDEM primary survey

    **Optional**
    :param Mapping map2meshSecondary: mapping current model to act as primary
    model on the secondary mesh
    """

    primary_simulation = properties.Instance(

    )

    def __init__(self, rxList, freq, primaryProblem, primarySurvey,
                 map2meshSecondary=None, **kwargs):

        self.primaryProblem = primaryProblem
        self.primarySurvey = primarySurvey

        if self.primaryProblem.ispaired is False:
            self.primaryProblem.pair(self.primarySurvey)

        self.map2meshSecondary = map2meshSecondary

        BaseFDEMSrc.__init__(self, rxList, freq=freq, **kwargs)

    def _ProjPrimary(self, prob, locType, locTypeTo):
        # TODO: if meshes have not changed, store the projection
        # if getattr(self, '__ProjPrimary', None) is None:

        # TODO: implement for HJ formulation
        if prob._formulation == 'EB':
            pass
        else:
            raise NotImplementedError(
                'PrimSecMappedSigma Source has not been implemented for {} '
                'formulation'.format(prob._formulation)
                )

        # TODO: only set up for tensot meshes (Tree meshes should be easy/done)
        # but have not been tried or tested.
        assert prob.mesh._meshType in ['TENSOR'], (
            'PrimSecMappedSigma source has not been implemented for {}'.format(
                prob.mesh._meshType)
            )

        # if EB formulation, interpolate E, elif HJ interpolate J
        # if self.primaryProblem._formulation == 'EB':
        #     locType = 'E'
        # elif self.primaryProblem._formulation == 'HJ':
        #     locType = 'F'

        # get interpolation mat from primary mesh to secondary mesh
        if self.primaryProblem.mesh._meshType == 'CYL':
            return self.primaryProblem.mesh.getInterpolationMatCartMesh(
                prob.mesh, locType=locType, locTypeTo=locTypeTo
            )
        return self.primaryProblem.mesh.getInterploationMat(
            prob.mesh, locType=locType, locTypeTo=locTypeTo
        )

        # return self.__ProjPrimary

    def _primaryFields(self, prob, fieldType=None, f=None):
        # TODO: cache and check if prob.curModel has changed

        if f is None:
            f = self.primaryProblem.fields(prob.model)

        if fieldType is not None:
            return f[:, fieldType]
        return f

    def _primaryFieldsDeriv(self, prob, v, adjoint=False, f=None):
        # TODO: this should not be hard-coded for j
        # jp = self._primaryFields(prob)[:,'j']

        # TODO: pull apart Jvec so that don't have to copy paste this code in
        # A = self.primaryProblem.getA(self.freq)
        # Ainv = self.primaryProblem.Solver(A, **self.primaryProblem.solverOpts) # create the concept of Ainv (actually a solve)

        if f is None:
            f = self._primaryFields(prob.sigma, f=f)

        freq = self.freq

        A = self.primaryProblem.getA(freq)
        src = self.primarySurvey.srcList[0]
        u_src = Utils.mkvc(f[src, self.primaryProblem._solutionType])

        if adjoint is True:
            Jtv = np.zeros(prob.sigmaMap.nP, dtype=complex)
            ATinv = self.primaryProblem.Solver(
                A.T, **self.primaryProblem.solverOpts
            )
            df_duTFun = getattr(
                f, '_{0}Deriv'.format(
                    'e' if self.primaryProblem._formulation == 'EB' else 'j'
                ),
                None
            )
            df_duT, df_dmT = df_duTFun(src, None, v, adjoint=True)

            ATinvdf_duT = ATinv * df_duT

            dA_dmT = self.primaryProblem.getADeriv(
                freq, u_src, ATinvdf_duT, adjoint=True
            )
            dRHS_dmT = self.primaryProblem.getRHSDeriv(
                freq, src, ATinvdf_duT, adjoint=True
            )

            du_dmT = -dA_dmT + dRHS_dmT

            Jtv += df_dmT + du_dmT

            ATinv.clean()

            return Utils.mkvc(Jtv)

        # create the concept of Ainv (actually a solve)
        Ainv = self.primaryProblem.Solver(A, **self.primaryProblem.solverOpts)

        # for src in self.survey.getSrcByFreq(freq):
        dA_dm_v = self.primaryProblem.getADeriv(freq, u_src, v)
        dRHS_dm_v = self.primaryProblem.getRHSDeriv(freq, src, v)
        du_dm_v = Ainv * (-dA_dm_v + dRHS_dm_v)

        # if self.primaryProblem._formulation == 'EB':
        df_dmFun = getattr(
            f, '_{0}Deriv'.format(
                'e' if self.primaryProblem._formulation == 'EB' else 'j'
            ),
            None
        )
        # elif self.primaryProblem._formulation == 'HJ':
        #     df_dmFun = getattr(f, '_{0}Deriv'.format('j'), None)
        df_dm_v = df_dmFun(src, du_dm_v, v, adjoint=False)
        # Jv[src, rx] = rx.evalDeriv(src, self.mesh, f, df_dm_v)
        Ainv.clean()

        return df_dm_v

        # return self.primaryProblem.Jvec(prob.curModel, v, f=f)

    def ePrimary(self, prob, f=None):
        if f is None:
            f = self._primaryFields(prob)

        if self.primaryProblem._formulation == 'EB':
            ep = self._ProjPrimary(prob, 'E', 'E') * f[:, 'e']
        elif self.primaryProblem._formulation == 'HJ':
            ep = self._ProjPrimary(prob, 'F', 'E') * (
                    self.primaryProblem.MfI * (
                        self.primaryProblem.MfRho * f[:, 'j'])
                    )

        return Utils.mkvc(ep)

    def ePrimaryDeriv(self, prob, v, adjoint=False, f=None):

        if f is None:
            f = self._primaryFields(prob)

        # if adjoint is True:
        #     raise NotImplementedError
        if self.primaryProblem._formulation == 'EB':
            if adjoint is True:
                epDeriv = self._primaryFieldsDeriv(
                    prob, (self._ProjPrimary(prob, 'E', 'E').T * v), f=f,
                    adjoint=adjoint
                )
            else:
                epDeriv = (
                    self._ProjPrimary(prob, 'E', 'E') *
                    self._primaryFieldsDeriv(prob, v, f=f)
                )
        elif self.primaryProblem._formulation == 'HJ':
            if adjoint is True:
                PTv = (
                    self.primaryProblem.MfI.T *
                    (self._ProjPrimary(prob, 'F', 'E').T * v)
                )
                epDeriv = (
                    self.primaryProblem.MfRhoDeriv(f[:, 'j']).T * PTv +
                    self._primaryFieldsDeriv(
                        prob, self.primaryProblem.MfRho.T * PTv,
                        adjoint=adjoint, f=f
                    )
                )
                # epDeriv =(

                #     (self.primaryProblem.MfI.T * PTv)
                #     )
            else:
                epDeriv = (
                    self._ProjPrimary(prob, 'F', 'E') *
                    (
                        self.primaryProblem.MfI *
                        (
                            (self.primaryProblem.MfRhoDeriv(f[:, 'j']) * v) +
                            (
                                self.primaryProblem.MfRho *
                                self._primaryFieldsDeriv(prob, v, f=f)
                            )
                        )
                    )
                )

        return Utils.mkvc(epDeriv)

    def bPrimary(self, prob, f=None):
        if f is None:
            f = self._primaryFields(prob)

        if self.primaryProblem._formulation == 'EB':
            bp = self._ProjPrimary(prob, 'F', 'F') * f[:, 'b']
        elif self.primaryProblem._formulation == 'HJ':
            bp = (
                self._ProjPrimary(prob, 'E', 'F') *
                (
                    self.primaryProblem.MeI *
                    (
                        self.primaryProblem.MeMu * f[:, 'h']
                    )
                )
            )

        return Utils.mkvc(bp)

    def s_e(self, prob, f=None):
        sigmaPrimary = self.map2meshSecondary * prob.model

        return Utils.mkvc(
            (prob.MeSigma - prob.mesh.getEdgeInnerProduct(sigmaPrimary)) *
            self.ePrimary(prob, f=f)
        )

    def s_eDeriv(self, prob, v, adjoint=False):

        sigmaPrimary = self.map2meshSecondary * prob.model
        sigmaPrimaryDeriv = self.map2meshSecondary.deriv(
                prob.model)

        f = self._primaryFields(prob)
        ePrimary = self.ePrimary(prob, f=f)

        if adjoint is True:
            return (
                prob.MeSigmaDeriv(ePrimary).T * v -
                (
                    sigmaPrimaryDeriv.T * prob.mesh.getEdgeInnerProductDeriv(
                        sigmaPrimary
                    )(ePrimary).T * v
                ) +
                self.ePrimaryDeriv(prob, (
                    prob.MeSigma - prob.mesh.getEdgeInnerProduct(
                        sigmaPrimary)).T * v, adjoint=adjoint, f=f)
            )

        return(
            prob.MeSigmaDeriv(ePrimary) * v -
            prob.mesh.getEdgeInnerProductDeriv(sigmaPrimary)(ePrimary) *
            (sigmaPrimaryDeriv * v) +
            (prob.MeSigma - prob.mesh.getEdgeInnerProduct(sigmaPrimary)) *
            self.ePrimaryDeriv(prob, v, adjoint=adjoint, f=f)
        )


