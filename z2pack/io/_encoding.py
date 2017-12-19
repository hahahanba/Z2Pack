"""Defines functions for encoding and decoding Z2Pack objects."""

import numbers
import contextlib
from functools import singledispatch
from collections.abc import Iterable

import numpy as np
from fsc.export import export

# This can create a circular import if it is imported by name (from ... import ...)
# If this is ever an issue, consider splitting the encoding by surface / line
from ..line import LineResult, WccLineData, OverlapLineData, EigenstateLineData
from ..surface._data import SurfaceData, LinePosition
from ..surface._result import SurfaceResult
from ..volume._data import VolumeData, SurfacePosition
from ..volume._result import VolumeResult


@export
@singledispatch
def encode(obj):
    """
    Encodes Z2Pack types into JSON / msgpack - compatible types.
    """
    raise TypeError('cannot JSONify {} object {}'.format(type(obj), obj))


@encode.register(np.bool_)
def _(obj):
    return bool(obj)


@encode.register(numbers.Real)
def _(obj):
    return float(obj)


@encode.register(numbers.Complex)
def _(obj):
    return dict(__complex__=True, real=encode(obj.real), imag=encode(obj.imag))


@encode.register(Iterable)
def _(obj):
    return list(obj)


@encode.register(EigenstateLineData)
def _(obj):
    return dict(
        __eigenstate_line_data__=True,
        eigenstates=encode(obj.eigenstates),
        symm_eigvals=encode(obj.symm_eigvals),
        symm_eigvecs=encode(obj.symm_eigvecs)
    )


@encode.register(OverlapLineData)
def _(obj):
    return dict(
        __overlap_line_data__=True,
        overlaps=encode(obj.overlaps),
        dmn=encode(obj.dmn)
    )


@encode.register(WccLineData)
def _(obj):
    return dict(__wcc_line_data__=True, wcc=encode(obj.wcc))


@encode.register(LineResult)
def _(obj):
    return dict(
        __line_result__=True,
        data=encode(obj.data),
        ctrl_convergence=obj.ctrl_convergence,
        ctrl_states=obj.ctrl_states
    )


@encode.register(LinePosition)
def _(obj):
    return dict(__line_position__=True, t=obj.t, result=encode(obj.result))


@encode.register(SurfaceData)
def _(obj):
    return dict(__surface_data__=True, lines=encode(obj.lines))


@encode.register(SurfaceResult)
def _(obj):
    return dict(
        __surface_result__=True,
        data=encode(obj.data),
        ctrl_convergence=obj.ctrl_convergence,
        ctrl_states=obj.ctrl_states
    )


@encode.register(SurfacePosition)
def _(obj):
    return dict(__surface_position__=True, s=obj.s, result=encode(obj.result))


@encode.register(VolumeData)
def _(obj):
    return dict(__volume_data__=True, surfaces=encode(obj.surfaces))


@encode.register(VolumeResult)
def _(obj):
    return dict(
        __volume_result__=True,
        data=encode(obj.data),
        ctrl_convergence=obj.ctrl_convergence,
        ctrl_states=obj.ctrl_states
    )


# --------------------------------------------------------------------- #


@export
@singledispatch
def decode(obj):
    """
    Decodes JSON / msgpack objects into the corresponding Z2Pack types.
    """
    return obj


def decode_volume_result(obj):
    # The states / convergence of the controls are set manually
    res = VolumeResult(obj['data'], [], [])
    res.ctrl_convergence = decode(obj['ctrl_convergence'])
    res.ctrl_states = decode(obj['ctrl_states'])
    return res


def decode_volume_data(obj):
    return VolumeData(decode(obj['surfaces']))


def decode_surface_position(obj):
    return SurfacePosition(s=obj['s'], result=decode(obj['result']))


def decode_surface_result(obj):
    # The states / convergence of the controls are set manually
    res = SurfaceResult(obj['data'], [], [])
    res.ctrl_convergence = decode(obj['ctrl_convergence'])
    res.ctrl_states = decode(obj['ctrl_states'])
    return res


def decode_surface_data(obj):
    return SurfaceData(decode(obj['lines']))


# Needed for legacy results.
def decode_surface_line(obj):
    return LinePosition(obj['t'], decode(obj['result']))


def decode_line_position(obj):
    return LinePosition(obj['t'], decode(obj['result']))


def decode_line_result(obj):
    # The states / convergence of the controls are set manually
    res = LineResult(obj['data'], [], [])
    res.ctrl_convergence = decode(obj['ctrl_convergence'])
    res.ctrl_states = decode(obj['ctrl_states'])
    return res


def decode_wcc_line_data(obj):
    return WccLineData(obj['wcc'])


def decode_overlap_line_data(obj):
    return OverlapLineData(obj['overlaps'], obj.get('dmn', None))


def decode_eigenstate_line_data(obj):
    return EigenstateLineData(
        obj['eigenstates'],
        obj.get('symm_eigvals', None), obj.get('symm_eigvecs', None)
    )


def decode_complex(obj):
    return complex(obj['real'], obj['imag'])


@decode.register(dict)
def _(obj):  # pylint: disable=missing-docstring
    with contextlib.suppress(AttributeError):
        obj = {k.decode('utf-8'): v for k, v in obj.items()}
    special_markers = [key for key in obj.keys() if key.startswith('__')]
    if len(special_markers) == 1:
        name = special_markers[0].strip('__')
        return globals()['decode_' + name](obj)
    return obj
