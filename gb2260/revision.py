from __future__ import absolute_import
from __future__ import unicode_literals

import gb2260.code as dcode
from gb2260._compat import ensure_text, iteritems
from gb2260.division import Division
from gb2260.exceptions import RevisionNotFound, SourceNotFound


def _import_module(name):
    # this dangerous function call can be replaced by importlib
    # if we drop python 2.6 support
    module = __import__(name, globals(), locals(), [], 0)
    for submodule in name.split('.')[1:]:
        module = getattr(module, submodule)
    return module


class Revision(object):

    __slots__ = ['division_schema', 'name']

    def __init__(self, name, division_schema):
        self.name = name
        self.division_schema = division_schema

    def get(self, code):
        code = ensure_text(code, 'ascii')
        try:
            name = self.division_schema[code]
        except KeyError:
            return None
        return Division(code, name, self)

    def provinces(self):
        return [
            Division(code, name, self)
            for code, name in iteritems(self.division_schema)
            if dcode.PROVINCE_CODE_PATTERN.match(code)
        ]

    def prefectures(self, province_code):
        pattern = dcode.make_prefecture_pattern(province_code)
        return [
            Division(code, name, self)
            for code, name in iteritems(self.division_schema)
            if pattern.match(code)
        ]

    def counties(self, prefecture_code):
        pattern = dcode.make_county_pattern(prefecture_code)
        return [
            Division(code, name, self)
            for code, name in iteritems(self.division_schema)
            if pattern.match(code)
        ]

    def get_province(self, code):
        province_code = dcode.to_province(code)
        return self.get(province_code)

    def get_prefecture(self, code):
        try:
            prefecture_code = dcode.to_prefecture(code)
        except ValueError:  # No corresponding prefecture
            return None
        return self.get(prefecture_code)

    def describe(self, code):
        names = [
            self.division_schema.get(part)
            for part in dcode.split(code)
            if part
        ]
        return ' '.join(names)


class Source(object):

    __slots__ = ['all_revisions', 'name']

    def __init__(self, name):
        module_name = 'gb2260.data.{0}'.format(name)
        try:
            module = _import_module(module_name)
        except ImportError:
            raise SourceNotFound(name)

        self.all_revisions = module.revisions
        self.name = name

    @property
    def latest_revision(self):
        return self.all_revisions[0]

    def load_revision(self, name):
        module_name = 'gb2260.data.{0}.revision_{1}'.format(self.name, name)
        try:
            module = _import_module(module_name)
        except ImportError:
            raise RevisionNotFound(name)

        return Revision(module.name, module.division_schema)
