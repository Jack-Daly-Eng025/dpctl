#                       Data Parallel Control (dpctl)
#
#  Copyright 2020-2023 Intel Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import ctypes

import numpy as np
import pytest

import dpctl
import dpctl.tensor as dpt
from dpctl.tests.helper import get_queue_or_skip, skip_if_dtype_not_supported

from .utils import _all_dtypes, _compare_dtypes, _usm_types


@pytest.mark.parametrize("op1_dtype", _all_dtypes)
@pytest.mark.parametrize("op2_dtype", _all_dtypes)
def test_greater_equal_dtype_matrix(op1_dtype, op2_dtype):
    q = get_queue_or_skip()
    skip_if_dtype_not_supported(op1_dtype, q)
    skip_if_dtype_not_supported(op2_dtype, q)

    sz = 127
    ar1 = dpt.zeros(sz, dtype=op1_dtype)
    ar2 = dpt.ones_like(ar1, dtype=op2_dtype)

    r = dpt.greater_equal(ar1, ar2)
    assert isinstance(r, dpt.usm_ndarray)
    expected = np.greater_equal(
        np.zeros(1, dtype=op1_dtype), np.ones(1, dtype=op2_dtype)
    )
    assert _compare_dtypes(r.dtype, expected.dtype, sycl_queue=q)
    assert r.shape == ar1.shape
    assert (dpt.asnumpy(r) == expected.astype(r.dtype)).all()
    assert r.sycl_queue == ar1.sycl_queue

    ar3 = dpt.zeros(sz, dtype=op1_dtype)
    ar4 = dpt.ones(2 * sz, dtype=op2_dtype)

    r = dpt.greater_equal(ar3[::-1], ar4[::2])
    assert isinstance(r, dpt.usm_ndarray)
    expected = np.greater_equal(
        np.zeros(1, dtype=op1_dtype), np.ones(1, dtype=op2_dtype)
    )
    assert _compare_dtypes(r.dtype, expected.dtype, sycl_queue=q)
    assert r.shape == ar3.shape
    assert (dpt.asnumpy(r) == expected.astype(r.dtype)).all()


@pytest.mark.parametrize("op_dtype", ["c8", "c16"])
def test_greater_equal_complex_matrix(op_dtype):
    q = get_queue_or_skip()
    skip_if_dtype_not_supported(op_dtype, q)

    sz = 127
    ar1_np_real = np.random.randint(0, 10, sz)
    ar1_np_imag = np.random.randint(0, 10, sz)
    ar1 = dpt.asarray(ar1_np_real + 1j * ar1_np_imag, dtype=op_dtype)

    ar2_np_real = np.random.randint(0, 10, sz)
    ar2_np_imag = np.random.randint(0, 10, sz)
    ar2 = dpt.asarray(ar2_np_real + 1j * ar2_np_imag, dtype=op_dtype)

    r = dpt.greater_equal(ar1, ar2)
    expected = np.greater_equal(dpt.asnumpy(ar1), dpt.asnumpy(ar2))
    assert _compare_dtypes(r.dtype, expected.dtype, sycl_queue=q)
    assert r.shape == expected.shape
    assert (dpt.asnumpy(r) == expected).all()

    r1 = dpt.greater_equal(ar1[::-2], ar2[::2])
    expected1 = np.greater_equal(dpt.asnumpy(ar1[::-2]), dpt.asnumpy(ar2[::2]))
    assert _compare_dtypes(r.dtype, expected1.dtype, sycl_queue=q)
    assert r1.shape == expected1.shape
    assert (dpt.asnumpy(r1) == expected1).all()

    ar3 = dpt.asarray([1.0 + 9j, 2.0 + 0j, 2.0 + 1j, 2.0 + 2j], dtype=op_dtype)
    ar4 = dpt.asarray([2.0 + 0j, dpt.nan, dpt.inf, -dpt.inf], dtype=op_dtype)
    r2 = dpt.greater_equal(ar3, ar4)
    with np.errstate(invalid="ignore"):
        expected2 = np.greater_equal(dpt.asnumpy(ar3), dpt.asnumpy(ar4))
    assert (dpt.asnumpy(r2) == expected2).all()

    r3 = dpt.greater_equal(ar4, ar4)
    with np.errstate(invalid="ignore"):
        expected3 = np.greater_equal(dpt.asnumpy(ar4), dpt.asnumpy(ar4))
    assert (dpt.asnumpy(r3) == expected3).all()


def test_greater_equal_complex_float():
    get_queue_or_skip()

    ar1 = dpt.asarray([1.0 + 9j, 2.0 + 0j, 2.0 + 1j, 2.0 + 2j], dtype="c8")
    ar2 = dpt.full((4,), 2, dtype="f4")

    r = dpt.greater_equal(ar1, ar2)
    expected = np.greater_equal(dpt.asnumpy(ar1), dpt.asnumpy(ar2))
    assert (dpt.asnumpy(r) == expected).all()

    r1 = dpt.greater_equal(ar2, ar1)
    expected1 = np.greater_equal(dpt.asnumpy(ar2), dpt.asnumpy(ar1))
    assert (dpt.asnumpy(r1) == expected1).all()
    with np.errstate(invalid="ignore"):
        for tp in [dpt.nan, dpt.inf, -dpt.inf]:

            ar3 = dpt.full((4,), tp)
            r2 = dpt.greater_equal(ar1, ar3)
            expected2 = np.greater_equal(dpt.asnumpy(ar1), dpt.asnumpy(ar3))
            assert (dpt.asnumpy(r2) == expected2).all()

            r3 = dpt.greater_equal(ar3, ar1)
            expected3 = np.greater_equal(dpt.asnumpy(ar3), dpt.asnumpy(ar1))
            assert (dpt.asnumpy(r3) == expected3).all()


@pytest.mark.parametrize("op1_usm_type", _usm_types)
@pytest.mark.parametrize("op2_usm_type", _usm_types)
def test_greater_equal_usm_type_matrix(op1_usm_type, op2_usm_type):
    get_queue_or_skip()

    sz = 128
    ar1 = dpt.ones(sz, dtype="i4", usm_type=op1_usm_type)
    ar2 = dpt.ones_like(ar1, dtype="i4", usm_type=op2_usm_type)

    r = dpt.greater_equal(ar1, ar2)
    assert isinstance(r, dpt.usm_ndarray)
    expected_usm_type = dpctl.utils.get_coerced_usm_type(
        (op1_usm_type, op2_usm_type)
    )
    assert r.usm_type == expected_usm_type


def test_greater_equal_order():
    get_queue_or_skip()

    ar1 = dpt.ones((20, 20), dtype="i4", order="C")
    ar2 = dpt.ones((20, 20), dtype="i4", order="C")
    r1 = dpt.greater_equal(ar1, ar2, order="C")
    assert r1.flags.c_contiguous
    r2 = dpt.greater_equal(ar1, ar2, order="F")
    assert r2.flags.f_contiguous
    r3 = dpt.greater_equal(ar1, ar2, order="A")
    assert r3.flags.c_contiguous
    r4 = dpt.greater_equal(ar1, ar2, order="K")
    assert r4.flags.c_contiguous

    ar1 = dpt.ones((20, 20), dtype="i4", order="F")
    ar2 = dpt.ones((20, 20), dtype="i4", order="F")
    r1 = dpt.greater_equal(ar1, ar2, order="C")
    assert r1.flags.c_contiguous
    r2 = dpt.greater_equal(ar1, ar2, order="F")
    assert r2.flags.f_contiguous
    r3 = dpt.greater_equal(ar1, ar2, order="A")
    assert r3.flags.f_contiguous
    r4 = dpt.greater_equal(ar1, ar2, order="K")
    assert r4.flags.f_contiguous

    ar1 = dpt.ones((40, 40), dtype="i4", order="C")[:20, ::-2]
    ar2 = dpt.ones((40, 40), dtype="i4", order="C")[:20, ::-2]
    r4 = dpt.greater_equal(ar1, ar2, order="K")
    assert r4.strides == (20, -1)

    ar1 = dpt.ones((40, 40), dtype="i4", order="C")[:20, ::-2].mT
    ar2 = dpt.ones((40, 40), dtype="i4", order="C")[:20, ::-2].mT
    r4 = dpt.greater_equal(ar1, ar2, order="K")
    assert r4.strides == (-1, 20)


def test_greater_equal_broadcasting():
    get_queue_or_skip()

    m = dpt.ones((100, 5), dtype="i4")
    v = dpt.arange(1, 6, dtype="i4")

    r = dpt.greater_equal(m, v)

    expected = np.greater_equal(
        np.ones((100, 5), dtype="i4"), np.arange(1, 6, dtype="i4")
    )
    assert (dpt.asnumpy(r) == expected.astype(r.dtype)).all()

    r2 = dpt.greater_equal(v, m)
    expected2 = np.greater_equal(
        np.arange(1, 6, dtype="i4"), np.ones((100, 5), dtype="i4")
    )
    assert (dpt.asnumpy(r2) == expected2.astype(r2.dtype)).all()


@pytest.mark.parametrize("arr_dt", _all_dtypes)
def test_greater_equal_python_scalar(arr_dt):
    q = get_queue_or_skip()
    skip_if_dtype_not_supported(arr_dt, q)

    X = dpt.ones((10, 10), dtype=arr_dt, sycl_queue=q)
    py_ones = (
        bool(1),
        int(1),
        float(1),
        complex(1),
        np.float32(1),
        ctypes.c_int(1),
    )
    for sc in py_ones:
        R = dpt.greater_equal(X, sc)
        assert isinstance(R, dpt.usm_ndarray)
        R = dpt.greater_equal(sc, X)
        assert isinstance(R, dpt.usm_ndarray)


class MockArray:
    def __init__(self, arr):
        self.data_ = arr

    @property
    def __sycl_usm_array_interface__(self):
        return self.data_.__sycl_usm_array_interface__


def test_greater_equal_mock_array():
    get_queue_or_skip()
    a = dpt.arange(10)
    b = dpt.ones(10)
    c = MockArray(b)
    r = dpt.greater_equal(a, c)
    assert isinstance(r, dpt.usm_ndarray)


def test_greater_equal_canary_mock_array():
    get_queue_or_skip()
    a = dpt.arange(10)

    class Canary:
        def __init__(self):
            pass

        @property
        def __sycl_usm_array_interface__(self):
            return None

    c = Canary()
    with pytest.raises(ValueError):
        dpt.greater_equal(a, c)
