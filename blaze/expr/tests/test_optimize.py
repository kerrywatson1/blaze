from blaze.expr.optimize import lean_projection, _lean
from blaze.expr import *

t = Symbol('t', 'var * {x: int, y: int, z: int, w: int}')


def test_lean_on_Symbol():
    assert _lean(t, fields=['x'])[0] == t[['x']]
    assert _lean(t, fields=['x', 'y', 'z', 'w'])[0] == t


def test_lean_projection():
    assert lean_projection(t[t.x > 0].y)._child._child.isidentical(t[['x', 'y']])


def test_lean_projection_by():
    assert lean_projection(by(t.x, total=t.y.sum()))._child.isidentical(
                    t[['x', 'y']])


def test_lean_by_with_summary():
    assert lean_projection(by(t.x, total=t.y.sum()))._child.isidentical(
                    t[['x', 'y']])

    tt = t[['x', 'y']]
    result = lean_projection(by(t.x, a=t.y.sum(), b=t.z.sum())[['x', 'a']])
    expected = Projection(
                    By(Field(tt, 'x'), summary(a=sum(Field(tt, 'y')))),
                    ('x', 'a'))
    assert result.isidentical(expected)


def test_summary():
    expr, fields = _lean(summary(a=t.x.sum(), b=t.y.sum()), fields=['a'])
    assert expr.isidentical(summary(a=t.x.sum()))

    assert fields == set(['x'])


def test_sort():
    assert lean_projection(t.sort('x').y).isidentical(t[['x','y']].sort('x').y)


def test_head():
    assert lean_projection(t.sort('x').y.head(5)).isidentical(
                t[['x','y']].sort('x').y.head(5))

def test_elemwise_thats_also_a_column():
    t = Symbol('t', 'var * {x: int, time: datetime, y: int}')
    expr = t[t.x > 0].time.truncate(months=1)
    expected = t[['time', 'x']]
    result = lean_projection(expr)
    assert result._child._child._child.isidentical(t[['time', 'x']])

def test_distinct():
    expr = t.distinct()[['x', 'y']]
    assert lean_projection(expr).isidentical(expr)

def test_like():
    t = Symbol('t', 'var * {name: string, x: int, y: int}')
    expr = t.like(name='Alice').y

    result = lean_projection(expr)
    assert result._child._child.isidentical(t[['name', 'y']])
