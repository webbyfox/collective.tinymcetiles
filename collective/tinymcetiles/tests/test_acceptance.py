# -*- coding: utf-8 -*-
import unittest
import robotsuite
from plone.testing import layered
from collective.tinymcetiles.testing import TILES_ROBOT_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('test_acceptance.robot'),
                layer=TILES_ROBOT_TESTING),
    ])
    return suite
