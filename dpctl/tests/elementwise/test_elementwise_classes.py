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

import dpctl.tensor as dpt

unary_fn = dpt.negative
binary_fn = dpt.divide


def test_unary_class_getters():
    fn = unary_fn.get_implementation_function()
    assert callable(fn)

    fn = unary_fn.get_type_result_resolver_function()
    assert callable(fn)


def test_unary_class_types_property():
    loop_types = unary_fn.types
    assert isinstance(loop_types, list)
    assert len(loop_types) > 0
    assert all(isinstance(sig, str) for sig in loop_types)
    assert all("->" in sig for sig in loop_types)


def test_unary_class_str_repr():
    s = str(unary_fn)
    r = repr(unary_fn)

    assert isinstance(s, str)
    assert isinstance(r, str)
    kl_n = unary_fn.__name__
    assert kl_n in s
    assert kl_n in r


def test_binary_class_getters():
    fn = binary_fn.get_implementation_function()
    assert callable(fn)

    fn = binary_fn.get_implementation_inplace_function()
    assert callable(fn)

    fn = binary_fn.get_type_result_resolver_function()
    assert callable(fn)

    fn = binary_fn.get_type_promotion_path_acceptance_function()
    assert callable(fn)


def test_binary_class_types_property():
    loop_types = binary_fn.types
    assert isinstance(loop_types, list)
    assert len(loop_types) > 0
    assert all(isinstance(sig, str) for sig in loop_types)
    assert all("->" in sig for sig in loop_types)


def test_binary_class_str_repr():
    s = str(binary_fn)
    r = repr(binary_fn)

    assert isinstance(s, str)
    assert isinstance(r, str)
    kl_n = binary_fn.__name__
    assert kl_n in s
    assert kl_n in r
