# util/compat.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""Handle Python version/platform incompatibilities."""

import collections
import contextlib
import inspect
import operator
import platform
import sys

py39 = sys.version_info >= (3, 9)
py38 = sys.version_info >= (3, 8)
py37 = sys.version_info >= (3, 7)
py3k = sys.version_info >= (3, 0)
py2k = sys.version_info < (3, 0)
pypy = platform.python_implementation() == "PyPy"


cpython = platform.python_implementation() == "CPython"
win32 = sys.platform.startswith("win")
osx = sys.platform.startswith("darwin")
arm = "aarch" in platform.machine().lower()

has_refcount_gc = bool(cpython)

contextmanager = contextlib.contextmanager
dottedgetter = operator.attrgetter
namedtuple = collections.namedtuple
next = next  # noqa

FullArgSpec = collections.namedtuple(
    "FullArgSpec",
    [
        "args",
        "varargs",
        "varkw",
        "defaults",
        "kwonlyargs",
        "kwonlydefaults",
        "annotations",
    ],
)


class nullcontext(object):
    """Context manager that does no additional processing.

    Vendored from Python 3.7.

    """

    def __init__(self, enter_result=None):
        self.enter_result = enter_result

    def __enter__(self):
        return self.enter_result

    def __exit__(self, *excinfo):
        pass


try:
    import threading
except ImportError:
    import dummy_threading as threading  # noqa


def inspect_getfullargspec(func):
    """Fully vendored version of getfullargspec from Python 3.3."""

    if inspect.ismethod(func):
        func = func.__func__
    if not inspect.isfunction(func):
        raise TypeError("{!r} is not a Python function".format(func))

    co = func.__code__
    if not inspect.iscode(co):
        raise TypeError("{!r} is not a code object".format(co))

    nargs = co.co_argcount
    names = co.co_varnames
    nkwargs = co.co_kwonlyargcount if py3k else 0
    args = list(names[:nargs])
    kwonlyargs = list(names[nargs : nargs + nkwargs])

    nargs += nkwargs
    varargs = None
    if co.co_flags & inspect.CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = None
    if co.co_flags & inspect.CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]

    return FullArgSpec(
        args,
        varargs,
        varkw,
        func.__defaults__,
        kwonlyargs,
        func.__kwdefaults__ if py3k else None,
        func.__annotations__ if py3k else {},
    )


if py38:
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata  # noqa


def importlib_metadata_get(group):
    ep = importlib_metadata.entry_points()
    if hasattr(ep, "select"):
        return ep.select(group=group)
    else:
        return ep.get(group, ())


if py3k:
    import base64
    import builtins
    import configparser
    import itertools
    import pickle

    from functools import reduce
    from io import BytesIO as byte_buffer
    from io import StringIO
    from itertools import zip_longest
    from time import perf_counter
    from urllib.parse import (
        quote_plus,
        unquote_plus,
        parse_qsl,
        quote,
        unquote,
    )

    string_types = (str,)
    binary_types = (bytes,)
    binary_type = bytes
    text_type = str
    int_types = (int,)
    iterbytes = iter
    long_type = int

    itertools_filterfalse = itertools.filterfalse
    itertools_filter = filter
    itertools_imap = map

    exec_ = getattr(builtins, "exec")
    import_ = getattr(builtins, "__import__")
    print_ = getattr(builtins, "print")

    def b(s):
        return s.encode("latin-1")

    def b64decode(x):
        return base64.b64decode(x.encode("ascii"))

    def b64encode(x):
        return base64.b64encode(x).decode("ascii")

    def decode_backslashreplace(text, encoding):
        return text.decode(encoding, errors="backslashreplace")

    def cmp(a, b):
        return (a > b) - (a < b)

    def raise_(
        exception, with_traceback=None, replace_context=None, from_=False
    ):
        r"""implement "raise" with cause support.

        :param exception: exception to raise
        :param with_traceback: will call exception.with_traceback()
        :param replace_context: an as-yet-unsupported feature.  This is
         an exception object which we are "replacing", e.g., it's our
         "cause" but we don't want it printed.    Basically just what
         ``__suppress_context__`` does but we don't want to suppress
         the enclosing context, if any.  So for now we make it the
         cause.
        :param from\_: the cause.  this actually sets the cause and doesn't
         hope to hide it someday.

        """
        if with_traceback is not None:
            exception = exception.with_traceback(with_traceback)

        if from_ is not False:
            exception.__cause__ = from_
        elif replace_context is not None:
            # no good solution here, we would like to have the exception
            # have only the context of replace_context.__context__ so that the
            # intermediary exception does not change, but we can't figure
            # that out.
            exception.__cause__ = replace_context

        try:
            raise exception
        finally:
            # credit to
            # https://cosmicpercolator.com/2016/01/13/exception-leaks-in-python-2-and-3/
            # as the __traceback__ object creates a cycle
            del exception, replace_context, from_, with_traceback

    def u(s):
        return s

    def ue(s):
        return s

    from typing import TYPE_CHECKING

    # Unused. Kept for backwards compatibility.
    callable = callable  # noqa

    from abc import ABC

    def _qualname(fn):
        return fn.__qualname__


else:
    import base64
    import ConfigParser as configparser  # noqa
    import itertools

    from StringIO import StringIO  # noqa
    from cStringIO import StringIO as byte_buffer  # noqa
    from itertools import izip_longest as zip_longest  # noqa
    from time import clock as perf_counter  # noqa
    from urllib import quote  # noqa
    from urllib import quote_plus  # noqa
    from urllib import unquote  # noqa
    from urllib import unquote_plus  # noqa
    from urlparse import parse_qsl  # noqa

    from abc import ABCMeta

    class ABC(object):
        __metaclass__ = ABCMeta

    try:
        import cPickle as pickle
    except ImportError:
        import pickle  # noqa

    string_types = (basestring,)  # noqa
    binary_types = (bytes,)
    binary_type = str
    text_type = unicode  # noqa
    int_types = int, long  # noqa
    long_type = long  # noqa

    callable = callable  # noqa
    cmp = cmp  # noqa
    reduce = reduce  # noqa

    b64encode = base64.b64encode
    b64decode = base64.b64decode

    itertools_filterfalse = itertools.ifilterfalse
    itertools_filter = itertools.ifilter
    itertools_imap = itertools.imap

    def b(s):
        return s

    def exec_(func_text, globals_, lcl=None):
        if lcl is None:
            exec("exec func_text in globals_")
        else:
            exec("exec func_text in globals_, lcl")

    def iterbytes(buf):
        return (ord(byte) for byte in buf)

    def import_(*args):
        if len(args) == 4:
            args = args[0:3] + ([str(arg) for arg in args[3]],)
        return __import__(*args)

    def print_(*args, **kwargs):
        fp = kwargs.pop("file", sys.stdout)
        if fp is None:
            return
        for arg in enumerate(args):
            if not isinstance(arg, basestring):  # noqa
                arg = str(arg)
            fp.write(arg)

    def u(s):
        # this differs from what six does, which doesn't support non-ASCII
        # strings - we only use u() with
        # literal source strings, and all our source files with non-ascii
        # in them (all are tests) are utf-8 encoded.
        return unicode(s, "utf-8")  # noqa

    def ue(s):
        return unicode(s, "unicode_escape")  # noqa

    def decode_backslashreplace(text, encoding):
        try:
            return text.decode(encoding)
        except UnicodeDecodeError:
            # regular "backslashreplace" for an incompatible encoding raises:
            # "TypeError: don't know how to handle UnicodeDecodeError in
            # error callback"
            return repr(text)[1:-1].decode()

    def safe_bytestring(text):
        # py2k only
        if not isinstance(text, string_types):
            return unicode(text).encode(  # noqa: F821
                "ascii", errors="backslashreplace"
            )
        elif isinstance(text, unicode):  # noqa: F821
            return text.encode("ascii", errors="backslashreplace")
        else:
            return text

    exec(
        "def raise_(exception, with_traceback=None, replace_context=None, "
        "from_=False):\n"
        "    if with_traceback:\n"
        "        raise type(exception), exception, with_traceback\n"
        "    else:\n"
        "        raise exception\n"
    )

    TYPE_CHECKING = False

    def _qualname(meth):
        """return __qualname__ equivalent for a method on a class"""

        for cls in meth.im_class.__mro__:
            if meth.__name__ in cls.__dict__:
                break
        else:
            return meth.__name__

        return "%s.%s" % (cls.__name__, meth.__name__)


if py3k:

    def _formatannotation(annotation, base_module=None):
        """vendored from python 3.7"""

        if getattr(annotation, "__module__", None) == "typing":
            return repr(annotation).replace("typing.", "")
        if isinstance(annotation, type):
            if annotation.__module__ in ("builtins", base_module):
                return annotation.__qualname__
            return annotation.__module__ + "." + annotation.__qualname__
        return repr(annotation)

    def inspect_formatargspec(
        args,
        varargs=None,
        varkw=None,
        defaults=None,
        kwonlyargs=(),
        kwonlydefaults={},
        annotations={},
        formatarg=str,
        formatvarargs=lambda name: "*" + name,
        formatvarkw=lambda name: "**" + name,
        formatvalue=lambda value: "=" + repr(value),
        formatreturns=lambda text: " -> " + text,
        formatannotation=_formatannotation,
    ):
        """Copy formatargspec from python 3.7 standard library.

        Python 3 has deprecated formatargspec and requested that Signature
        be used instead, however this requires a full reimplementation
        of formatargspec() in terms of creating Parameter objects and such.
        Instead of introducing all the object-creation overhead and having
        to reinvent from scratch, just copy their compatibility routine.

        Ultimately we would need to rewrite our "decorator" routine completely
        which is not really worth it right now, until all Python 2.x support
        is dropped.

        """

        kwonlydefaults = kwonlydefaults or {}
        annotations = annotations or {}

        def formatargandannotation(arg):
            result = formatarg(arg)
            if arg in annotations:
                result += ": " + formatannotation(annotations[arg])
            return result

        specs = []
        if defaults:
            firstdefault = len(args) - len(defaults)
        for i, arg in enumerate(args):
            spec = formatargandannotation(arg)
            if defaults and i >= firstdefault:
                spec = spec + formatvalue(defaults[i - firstdefault])
            specs.append(spec)

        if varargs is not None:
            specs.append(formatvarargs(formatargandannotation(varargs)))
        else:
            if kwonlyargs:
                specs.append("*")

        if kwonlyargs:
            for kwonlyarg in kwonlyargs:
                spec = formatargandannotation(kwonlyarg)
                if kwonlydefaults and kwonlyarg in kwonlydefaults:
                    spec += formatvalue(kwonlydefaults[kwonlyarg])
                specs.append(spec)

        if varkw is not None:
            specs.append(formatvarkw(formatargandannotation(varkw)))

        result = "(" + ", ".join(specs) + ")"
        if "return" in annotations:
            result += formatreturns(formatannotation(annotations["return"]))
        return result


else:
    from inspect import formatargspec as _inspect_formatargspec

    def inspect_formatargspec(*spec, **kw):
        # convert for a potential FullArgSpec from compat.getfullargspec()
        return _inspect_formatargspec(*spec[0:4], **kw)  # noqa


# Fix deprecation of accessing ABCs straight from collections module
# (which will stop working in 3.8).
if py3k:
    import collections.abc as collections_abc
else:
    import collections as collections_abc  # noqa


if py37:
    import dataclasses

    def dataclass_fields(cls):
        """Return a sequence of all dataclasses.Field objects associated
        with a class."""

        if dataclasses.is_dataclass(cls):
            return dataclasses.fields(cls)
        else:
            return []

    def local_dataclass_fields(cls):
        """Return a sequence of all dataclasses.Field objects associated with
        a class, excluding those that originate from a superclass."""

        if dataclasses.is_dataclass(cls):
            super_fields = set()
            for sup in cls.__bases__:
                super_fields.update(dataclass_fields(sup))
            return [
                f for f in dataclasses.fields(cls) if f not in super_fields
            ]
        else:
            return []


else:

    def dataclass_fields(cls):
        return []

    def local_dataclass_fields(cls):
        return []


def raise_from_cause(exception, exc_info=None):
    r"""legacy.  use raise\_()"""

    if exc_info is None:
        exc_info = sys.exc_info()
    exc_type, exc_value, exc_tb = exc_info
    cause = exc_value if exc_value is not exception else None
    reraise(type(exception), exception, tb=exc_tb, cause=cause)


def reraise(tp, value, tb=None, cause=None):
    r"""legacy.  use raise\_()"""

    raise_(value, with_traceback=tb, from_=cause)


def with_metaclass(meta, *bases, **kw):
    """Create a base class with a metaclass.

    Drops the middle class upon creation.

    Source: https://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/

    """

    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                cls = type.__new__(cls, name, (), d)
            else:
                cls = meta(name, bases, d)

            if hasattr(cls, "__init_subclass__") and hasattr(
                cls.__init_subclass__, "__func__"
            ):
                cls.__init_subclass__.__func__(cls, **kw)
            return cls

    return metaclass("temporary_class", None, {})


if py3k:
    from datetime import timezone
else:
    from datetime import datetime
    from datetime import timedelta
    from datetime import tzinfo

    class timezone(tzinfo):
        """Minimal port of python 3 timezone object"""

        __slots__ = "_offset"

        def __init__(self, offset):
            if not isinstance(offset, timedelta):
                raise TypeError("offset must be a timedelta")
            if not self._minoffset <= offset <= self._maxoffset:
                raise ValueError(
                    "offset must be a timedelta "
                    "strictly between -timedelta(hours=24) and "
                    "timedelta(hours=24)."
                )
            self._offset = offset

        def __eq__(self, other):
            if type(other) != timezone:
                return False
            return self._offset == other._offset

        def __hash__(self):
            return hash(self._offset)

        def __repr__(self):
            return "sqlalchemy.util.%s(%r)" % (
                self.__class__.__name__,
                self._offset,
            )

        def __str__(self):
            return self.tzname(None)

        def utcoffset(self, dt):
            return self._offset

        def tzname(self, dt):
            return self._name_from_offset(self._offset)

        def dst(self, dt):
            return None

        def fromutc(self, dt):
            if isinstance(dt, datetime):
                if dt.tzinfo is not self:
                    raise ValueError("fromutc: dt.tzinfo " "is not self")
                return dt + self._offset
            raise TypeError(
                "fromutc() argument must be a datetime instance" " or None"
            )

        @staticmethod
        def _timedelta_to_microseconds(timedelta):
            """backport of timedelta._to_microseconds()"""
            return (
                timedelta.days * (24 * 3600) + timedelta.seconds
            ) * 1000000 + timedelta.microseconds

        @staticmethod
        def _divmod_timedeltas(a, b):
            """backport of timedelta.__divmod__"""

            q, r = divmod(
                timezone._timedelta_to_microseconds(a),
                timezone._timedelta_to_microseconds(b),
            )
            return q, timedelta(0, 0, r)

        @staticmethod
        def _name_from_offset(delta):
            if not delta:
                return "UTC"
            if delta < timedelta(0):
                sign = "-"
                delta = -delta
            else:
                sign = "+"
            hours, rest = timezone._divmod_timedeltas(
                delta, timedelta(hours=1)
            )
            minutes, rest = timezone._divmod_timedeltas(
                rest, timedelta(minutes=1)
            )
            result = "UTC%s%02d:%02d" % (sign, hours, minutes)
            if rest.seconds:
                result += ":%02d" % (rest.seconds,)
            if rest.microseconds:
                result += ".%06d" % (rest.microseconds,)
            return result

        _maxoffset = timedelta(hours=23, minutes=59)
        _minoffset = -_maxoffset

    timezone.utc = timezone(timedelta(0))
