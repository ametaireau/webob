import cgi
from webob import html_escape
from webob.multidict import *
from nose.tools import eq_ as eq, assert_raises


def test_html_escape():
    for v, s in [
        (None, ''),
        (' ', ' '),
        ('&egrave;', '&amp;egrave;'),
        (u'\xe9', '&#233;'),
        (t_esc_HTML(), '<div>hello</div>'),
        (t_esc_Unicode(), '&#233;'),
        (t_esc_UnsafeAttrs(), '&lt;UnsafeAttrs&gt;'),
    ]:
        eq(html_escape(v), s)


class t_esc_HTML(object):
    def __html__(self):
        return '<div>hello</div>'


class t_esc_Unicode(object):
    def __unicode__(self):
        return u'\xe9'

class t_esc_UnsafeAttrs(object):
    attr = 'value'
    def __getattr__(self):
        return self.attr
    def __repr__(self):
        return '<UnsafeAttrs>'




def test_multidict():
    d = MultiDict(a=1, b=2)
    eq(d['a'], 1)
    eq(d.getall('c'), [])

    d.add('a', 2)
    eq(d['a'], 2)
    eq(d.getall('a'), [1, 2])

    d['b'] = 4
    eq(d.getall('b'), [4])
    eq(d.keys(), ['a', 'a', 'b'])
    eq(d.items(), [('a', 1), ('a', 2), ('b', 4)])
    eq(d.mixed(), {'a': [1, 2], 'b': 4})

    # test getone

    # KeyError: "Multiple values match 'a': [1, 2]"
    assert_raises(KeyError, d.getone, 'a')
    eq(d.getone('b'), 4)
    # KeyError: "Key not found: 'g'"
    assert_raises(KeyError, d.getone, 'g')

    eq(d.dict_of_lists(), {'a': [1, 2], 'b': [4]})
    assert 'b' in d
    assert 'e' not in d
    d.clear()
    assert 'b' not in d
    d['a'] = 4
    d.add('a', 5)
    e = d.copy()
    assert 'a' in e
    e.clear()
    e['f'] = 42
    d.update(e)
    eq(d, MultiDict([('a', 4), ('a', 5), ('f', 42)]))
    f = d.pop('a')
    eq(f, 4)
    eq(d['a'], 5)


    eq(d.pop('g', 42), 42)
    assert_raises(KeyError, d.pop, 'n')
    # TypeError: pop expected at most 2 arguments, got 3
    assert_raises(TypeError, d.pop, 4, 2, 3)
    d.setdefault('g', []).append(4)
    eq(d, MultiDict([('a', 5), ('f', 42), ('g', [4])]))



def test_multidict_init():
    d = MultiDict([('a', 'b')], c=2)
    eq(repr(d), "MultiDict([('a', 'b'), ('c', 2)])")
    eq(d, MultiDict([('a', 'b')], c=2))

    # TypeError: MultiDict can only be called with one positional argument
    assert_raises(TypeError, MultiDict, 1, 2, 3)

    # TypeError: MultiDict.view_list(obj) takes only actual list objects, not None
    assert_raises(TypeError, MultiDict.view_list, None)



def test_multidict_cgi():
    fs = cgi.FieldStorage()
    fs.filename = '\xc3\xb8'
    plain = MultiDict(key='\xc3\xb8', fs=fs)
    ua = UnicodeMultiDict(multi=plain, encoding='utf-8')
    eq(ua.getall('key'), [u'\xf8'])
    eq(ua.getall('fs'), [cgi.FieldStorage(None, u'\xf8', [])])
    ub = UnicodeMultiDict(multi=ua, encoding='utf-8')
    eq(ub.getall('key'), [u'\xf8'])
    eq(ub.getall('fs'), [cgi.FieldStorage(None, u'\xf8', [])])
