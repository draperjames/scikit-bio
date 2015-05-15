# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

import os

import pandas as pd
import numpy as np
import numpy.testing as npt

from skbio import OrdinationResults
from skbio.util import get_data_path, assert_ordination_results_equal
from skbio.util._testing import _normalize_signs


def test_get_data_path():
    fn = 'parrot'
    path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(path, 'data', fn)
    data_path_2 = get_data_path(fn)
    npt.assert_string_equal(data_path_2, data_path)


def test_assert_ordination_results_equal():
    minimal1 = OrdinationResults('foo', 'bar', pd.Series([1.0, 2.0]),
                                 pd.DataFrame([[1, 2, 3], [4, 5, 6]]))

    # a minimal set of results should be equal to itself
    assert_ordination_results_equal(minimal1, minimal1)

    # type mismatch
    with npt.assert_raises(AssertionError):
        assert_ordination_results_equal(minimal1, 'foo')

    # numeric values should be checked that they're almost equal
    almost_minimal1 = OrdinationResults(
        'foo', 'bar',
        pd.Series([1.0000001, 1.9999999]),
        pd.DataFrame([[1, 2, 3], [4, 5, 6]]))
    assert_ordination_results_equal(minimal1, almost_minimal1)

    # test each of the optional numeric attributes
    for attr in ('features', 'samples', 'biplot_scores', 'sample_constraints'):
        # missing optional numeric attribute in one, present in the other
        setattr(almost_minimal1, attr, pd.DataFrame([[1, 2], [3, 4]]))
        with npt.assert_raises(AssertionError):
            assert_ordination_results_equal(minimal1, almost_minimal1)
        setattr(almost_minimal1, attr, None)

        # optional numeric attributes present in both, but not almost equal
        setattr(minimal1, attr, pd.DataFrame([[1, 2], [3, 4]]))
        setattr(almost_minimal1, attr, pd.DataFrame([[1, 2], [3.00002, 4]]))
        with npt.assert_raises(AssertionError):
            assert_ordination_results_equal(minimal1, almost_minimal1)
        setattr(minimal1, attr, None)
        setattr(almost_minimal1, attr, None)

        # optional numeric attributes present in both, and almost equal
        setattr(minimal1, attr, pd.DataFrame([[1.0, 2.0], [3.0, 4.0]]))
        setattr(almost_minimal1, attr,
                pd.DataFrame([[1.0, 2.0], [3.00000002, 4]]))
        assert_ordination_results_equal(minimal1, almost_minimal1)
        setattr(minimal1, attr, None)
        setattr(almost_minimal1, attr, None)

    # missing optional numeric attribute in one, present in the other
    almost_minimal1.proportion_explained = pd.Series([1, 2, 3])
    with npt.assert_raises(AssertionError):
        assert_ordination_results_equal(minimal1, almost_minimal1)
    almost_minimal1.proportion_explained = None

    # optional numeric attributes present in both, but not almost equal
    minimal1.proportion_explained = pd.Series([1, 2, 3])
    almost_minimal1.proportion_explained = pd.Series([1, 2, 3.00002])
    with npt.assert_raises(AssertionError):
        assert_ordination_results_equal(minimal1, almost_minimal1)
    almost_minimal1.proportion_explained = None
    almost_minimal1.proportion_explained = None

    # optional numeric attributes present in both, and almost equal
    minimal1.proportion_explained = pd.Series([1, 2, 3])
    almost_minimal1.proportion_explained = pd.Series([1, 2, 3.00000002])
    with npt.assert_raises(AssertionError):
        assert_ordination_results_equal(minimal1, almost_minimal1)
    almost_minimal1.proportion_explained = None
    almost_minimal1.proportion_explained = None


class TestNormalizeSigns(object):
    def test_shapes_and_nonarray_input(self):
        with npt.assert_raises(ValueError):
            _normalize_signs([[1, 2], [3, 5]], [[1, 2]])

    def test_works_when_different(self):
        """Taking abs value of everything would lead to false
        positives."""
        a = np.array([[1, -1],
                      [2, 2]])
        b = np.array([[-1, -1],
                      [2, 2]])
        with npt.assert_raises(AssertionError):
            npt.assert_equal(*_normalize_signs(a, b))

    def test_easy_different(self):
        a = np.array([[1, 2],
                      [3, -1]])
        b = np.array([[-1, 2],
                      [-3, -1]])
        npt.assert_equal(*_normalize_signs(a, b))

    def test_easy_already_equal(self):
        a = np.array([[1, -2],
                      [3, 1]])
        b = a.copy()
        npt.assert_equal(*_normalize_signs(a, b))

    def test_zeros(self):
        a = np.array([[0, 3],
                      [0, -1]])
        b = np.array([[0, -3],
                      [0, 1]])
        npt.assert_equal(*_normalize_signs(a, b))

    def test_hard(self):
        a = np.array([[0, 1],
                      [1, 2]])
        b = np.array([[0, 1],
                      [-1, 2]])
        npt.assert_equal(*_normalize_signs(a, b))

    def test_harder(self):
        """We don't want a value that might be negative due to
        floating point inaccuracies to make a call to allclose in the
        result to be off."""
        a = np.array([[-1e-15, 1],
                      [5, 2]])
        b = np.array([[1e-15, 1],
                      [5, 2]])
        # Clearly a and b would refer to the same "column
        # eigenvectors" but a slopppy implementation of
        # _normalize_signs could change the sign of column 0 and make a
        # comparison fail
        npt.assert_almost_equal(*_normalize_signs(a, b))

    def test_column_zeros(self):
        a = np.array([[0, 1],
                      [0, 2]])
        b = np.array([[0, -1],
                      [0, -2]])
        npt.assert_equal(*_normalize_signs(a, b))

    def test_column_almost_zero(self):
        a = np.array([[1e-15, 3],
                      [-2e-14, -6]])
        b = np.array([[0, 3],
                      [-1e-15, -6]])
        npt.assert_almost_equal(*_normalize_signs(a, b))


if __name__ == '__main__':
    import nose
    nose.runmodule()
