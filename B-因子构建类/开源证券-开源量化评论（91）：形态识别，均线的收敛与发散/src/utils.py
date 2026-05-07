"""
Author: hugo2046 shen.lan123@gmail.com
Date: 2023-12-05 15:38:30
LastEditors: hugo2046 shen.lan123@gmail.com
LastEditTime: 2023-12-05 15:39:39
FilePath: 
Description: 
"""
import ast
import inspect
import re
import warnings
from collections import OrderedDict
from functools import wraps

import pandas as pd


def datetime2str(watch_dt: str, fmt: str = "%Y%m%d") -> str:
    return pd.to_datetime(watch_dt).strftime(fmt)


def str2datetime(watch_dt: str) -> pd.Timestamp:
    return pd.to_datetime(watch_dt)


def ignore_warning(message='', category=Warning, module='', lineno=0, append=False):
    # 忽略 warnings
    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message=message, category=category,
                                        module=module, lineno=lineno, append=append)
                return func(*args, **kwargs)
        return func_wrapper

    return decorator

def _make_assert_message(frame, regex):
    def extract_condition():
        code_context = inspect.getframeinfo(frame)[3]
        if not code_context:
            return ''
        match = re.search(regex, code_context[0])
        if not match:
            return ''
        return match.group(1).strip()

    class ReferenceFinder(ast.NodeVisitor):
        def __init__(self):
            self.names = []

        def find(self, tree, frame):
            self.visit(tree)
            nothing = object()
            deref = OrderedDict()
            for name in self.names:
                value = frame.f_locals.get(name, nothing) or frame.f_globals.get(name, nothing)
                if (value is not nothing and
                        not isinstance(value, (types.ModuleType, types.FunctionType))):
                    deref[name] = repr(value)
            return deref

        def visit_Name(self, node):
            self.names.append(node.id)

    condition = extract_condition()
    if not condition:
        return
    deref = ReferenceFinder().find(ast.parse(condition), frame)
    deref_str = ''
    if deref:
        deref_str = ' with ' + ', '.join('{}={}'.format(k, v) for k, v in deref.items())
    return 'assertion {} failed{}'.format(condition, deref_str)

def affirm(condition, message=None):
    if condition:
        return

    if message:
        raise AssertionError(str(message))

    frame = inspect.currentframe().f_back
    regex = r'affirm\s*\(\s*(.+)\s*\)'
    message = _make_assert_message(frame, regex)

    raise AssertionError(message)

