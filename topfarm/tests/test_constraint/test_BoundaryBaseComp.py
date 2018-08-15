import unittest

import numpy as np
from topfarm.cost_models.dummy import DummyCost, DummyCostPlotComp
from topfarm import TopFarm
import pytest
from topfarm._topfarm import TurbineXYZOptimizationProblem
from topfarm.constraint_components.boundary_component import BoundaryComp


def testSquare():
    optimal = [(0, 0)]
    boundary = [(0, 0), (1, 3)]
    tf = TopFarm(optimal, DummyCost(optimal), 2, boundary=boundary, boundary_type='square', record_id=None)
    np.testing.assert_array_equal(tf.xy_boundary, [[-1, 0],
                                                   [2, 0],
                                                   [2, 3],
                                                   [-1, 3],
                                                   [-1, 0]])


def testRectangle():
    optimal = [(0, 0)]
    boundary = [(0, 0), (1, 3)]
    tf = TopFarm(optimal, DummyCost(optimal), 2, boundary=boundary, boundary_type='rectangle', record_id=None)
    np.testing.assert_array_equal(tf.xy_boundary, [[0, 0],
                                                   [1, 0],
                                                   [1, 3],
                                                   [0, 3],
                                                   [0, 0]])


def testConvexHull():
    optimal = [(0, 0)]
    boundary = [(0, 0), (1, 1), (2, 0), (2, 2), (0, 2)]
    tf = TopFarm(optimal, DummyCost(optimal), 2, boundary=boundary, boundary_type='convex_hull', record_id=None)
    np.testing.assert_array_equal(tf.xy_boundary, [[0, 0],
                                                   [2, 0],
                                                   [2, 2],
                                                   [0, 2],
                                                   [0, 0]])


def testNotImplemented():
    optimal = [(0, 0)]
    boundary = [(0, 0), (1, 1), (2, 0), (2, 2), (0, 2)]
    with pytest.raises(NotImplementedError, match="Boundary type 'Something' is not implemented"):
        TopFarm(optimal, DummyCost(optimal), 2, boundary=boundary, boundary_type='Something', record_id=None)


def test_z_boundary():
    optimal = [(0, 0)]
    tf = TurbineXYZOptimizationProblem(DummyCost(optimal), optimal, BoundaryComp(2, None, [70, 90]))
    np.testing.assert_array_equal(tf.z_boundary, [[70, 90],
                                                  [70, 90]])


def test_xyz_boundary():
    optimal = [(0, 0)]
    boundary = [(0, 0), (1, 3)]
    tf = TurbineXYZOptimizationProblem(DummyCost(optimal), optimal, BoundaryComp(1, boundary, [70, 90], xy_boundary_type='rectangle'))
    np.testing.assert_array_equal(tf.xy_boundary, [[0, 0],
                                                   [1, 0],
                                                   [1, 3],
                                                   [0, 3],
                                                   [0, 0]])
    np.testing.assert_array_equal(tf.z_boundary, [[70, 90]])