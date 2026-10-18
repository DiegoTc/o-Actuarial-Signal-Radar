import numpy as np
import pytest

from research.forecasting.robustness.interval_influence import bootstrap


def test_calibration_bootstrap_is_reproducible_and_does_not_mutate():
    points=[100.,110.];residuals=[-2.,3.,40.,4.]
    c=dict(seed=271828,interval_simulations=5000,interval_levels=[.8,.95])
    a=bootstrap(points,residuals,c)
    assert a==bootstrap(points,residuals,c)
    assert residuals==[-2.,3.,40.,4.] and points==[100.,110.]
    assert np.asarray(a['0.95']).shape==(2,2)


def test_no_fabricated_calibration_with_one_residual():
    with pytest.raises(ValueError,match='Insufficient'):
        bootstrap([100],[1],dict(seed=1,interval_simulations=100,interval_levels=[.8,.95]))
