from __future__ import absolute_import, division, print_function

from datetime import date, datetime

from blaze.compute.core import (compute_up, compute_down, optimize, compute,
        bottom_up_until_type_break, top_then_bottom_then_top_again_etc)
from blaze.expr import by, Symbol, Expr
from blaze.dispatch import dispatch
from blaze.compatibility import raises

import numpy as np


def test_errors():
    t = Symbol('t', 'var * {foo: int}')
    with raises(NotImplementedError):
        compute_up(by(t, t.count()), 1)


def test_optimize():
    class Foo(object):
        pass

    s = Symbol('s', '5 * {x: int, y: int}')

    @dispatch(Expr, Foo)
    def compute_down(expr, foo):
        return str(expr)

    assert compute(s.x * 2, Foo()) == "s.x * 2"

    @dispatch(Expr, Foo)
    def optimize(expr, foo):
        return expr + 1

    assert compute(s.x * 2, Foo()) == "(s.x * 2) + 1"


def test_bottom_up_until_type_break():

    s = Symbol('s', 'var * {name: string, amount: int}')
    data = np.array([('Alice', 100), ('Bob', 200), ('Charlie', 300)],
                    dtype=[('name', 'S7'), ('amount', 'i4')])

    e = (s.amount + 1).distinct()
    expr, scope = bottom_up_until_type_break(e, {s: data})
    amount = Symbol('amount', 'var * real', token=1)
    assert expr.isidentical(amount)
    assert len(scope) == 1
    assert amount in scope
    assert (scope[amount] == np.array([101, 201, 301], dtype='i4')).all()

    # This computation has a type change midstream, so we stop and get the
    # unfinished computation.

    e = s.amount.sum() + 1
    expr, scope = bottom_up_until_type_break(e, {s: data})
    amount_sum = Symbol('amount_sum', 'int')
    assert expr.isidentical(amount_sum + 1)
    assert len(scope) == 1
    assert amount_sum in scope
    assert scope[amount_sum] == 600

    # ensure that we work on binops with one child
    x = Symbol('x', 'real')
    expr, scope = bottom_up_until_type_break(x + x, {x: 1})
    x2 = Symbol('_', 'real')
    assert expr.isidentical(x2)
    assert len(scope) == 1
    assert x2 in scope
    assert scope[x2] == 2


def test_top_then_bottom_then_top_again_etc():
    s = Symbol('s', 'var * {name: string, amount: int}')
    data = np.array([('Alice', 100), ('Bob', 200), ('Charlie', 300)],
                    dtype=[('name', 'S7'), ('amount', 'i4')])

    e = s.amount.sum() + 1
    assert top_then_bottom_then_top_again_etc(e, {s: data}) == 601
