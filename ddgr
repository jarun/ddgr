#!/usr/bin/env python3

# Copyright (C) 2016-2020 Arun Prakash Jana <engineerarun@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import codecs
import collections
import functools
import gzip
import html.entities
import html.parser
import json
import locale
import logging
import os
import platform
import shutil
import signal
from subprocess import Popen, PIPE, DEVNULL
import sys
import tempfile
import textwrap
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

try:
    import readline
except ImportError:
    pass

try:
    import setproctitle
    setproctitle.setproctitle('ddgr')
except (ImportError, Exception):
    pass

# Basic setup

logging.basicConfig(format='[%(levelname)s] %(message)s')
LOGGER = logging.getLogger()
LOGDBG = LOGGER.debug
LOGERR = LOGGER.error


def sigint_handler(signum, frame):
    print('\nInterrupted.', file=sys.stderr)
    sys.exit(1)


try:
    signal.signal(signal.SIGINT, sigint_handler)
except ValueError:
    # signal only works in main thread
    pass

# Constants

_VERSION_ = '1.8.1'

COLORMAP = {k: '\x1b[%sm' % v for k, v in {
    'a': '30', 'b': '31', 'c': '32', 'd': '33',
    'e': '34', 'f': '35', 'g': '36', 'h': '37',
    'i': '90', 'j': '91', 'k': '92', 'l': '93',
    'm': '94', 'n': '95', 'o': '96', 'p': '97',
    'A': '30;1', 'B': '31;1', 'C': '32;1', 'D': '33;1',
    'E': '34;1', 'F': '35;1', 'G': '36;1', 'H': '37;1',
    'I': '90;1', 'J': '91;1', 'K': '92;1', 'L': '93;1',
    'M': '94;1', 'N': '95;1', 'O': '96;1', 'P': '97;1',
    'x': '0', 'X': '1', 'y': '7', 'Y': '7;1',
}.items()}

USER_AGENT = 'ddgr/{} (textmode; Linux x86_64; 1024x768)'.format(_VERSION_)

TEXT_BROWSERS = ['elinks', 'links', 'lynx', 'w3m', 'www-browser']

INDENT = 5

# Global helper functions


def open_url(url):
    """Open an URL in the user's default web browser.

    The string attribute ``open_url.url_handler`` can be used to open URLs
    in a custom CLI script or utility. A subprocess is spawned with url as
    the parameter in this case instead of the usual webbrowser.open() call.

    Whether the browser's output (both stdout and stderr) are suppressed
    depends on the boolean attribute ``open_url.suppress_browser_output``.
    If the attribute is not set upon a call, set it to a default value,
    which means False if BROWSER is set to a known text-based browser --
    elinks, links, lynx, w3m or 'www-browser'; or True otherwise.

    The string attribute ``open_url.override_text_browser`` can be used to
    ignore env var BROWSER as well as some known text-based browsers and
    attempt to open url in a GUI browser available.
    Note: If a GUI browser is indeed found, this option ignores the program
          option `show-browser-logs`
    """
    LOGDBG('Opening %s', url)

    # Custom URL handler gets max priority
    if hasattr(open_url, 'url_handler'):
        pipe = Popen([open_url.url_handler, url], stdin=PIPE)
        pipe.communicate()
        return

    browser = webbrowser.get()
    if open_url.override_text_browser:
        browser_output = open_url.suppress_browser_output
        for name in [b for b in webbrowser._tryorder if b not in TEXT_BROWSERS]:
            browser = webbrowser.get(name)
            LOGDBG(browser)

            # Found a GUI browser, suppress browser output
            open_url.suppress_browser_output = True
            break

    if open_url.suppress_browser_output:
        _stderr = os.dup(2)
        os.close(2)
        _stdout = os.dup(1)
        os.close(1)
        fd = os.open(os.devnull, os.O_RDWR)
        os.dup2(fd, 2)
        os.dup2(fd, 1)
    try:
        browser.open(url, new=2)
    finally:
        if open_url.suppress_browser_output:
            os.close(fd)
            os.dup2(_stderr, 2)
            os.dup2(_stdout, 1)

    if open_url.override_text_browser:
        open_url.suppress_browser_output = browser_output


def https_get(url, headers=None, proxies=None, expected_code=None):
    """Sends an HTTPS GET request; returns the HTTP status code and the
    decoded response payload.

    By default, HTTP 301, 302 and 303 are followed; all other non-2XX
    responses result in a urllib.error.HTTPError. If expected_code is
    supplied, a urllib.error.HTTPError is raised unless the status code
    matches expected_code.
    """
    headers = headers or {}
    proxies = {'https': proxies['https']} if proxies.get('https') else {}
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler,
        urllib.request.ProxyHandler(proxies),
        urllib.request.HTTPRedirectHandler,
    )
    req = urllib.request.Request(
        url,
    )
    resp = opener.open(req)
    code = resp.getcode()
    if expected_code is not None and code != expected_code:
        raise urllib.error.HTTPError(resp.geturl(), code, resp.msg, resp.info(), resp)
    payload = resp.read()
    try:
        payload = gzip.decompress(payload)
    except OSError:
        pass
    finally:
        payload = payload.decode('utf-8')
    return code, payload


def https_post(url, data=None, headers=None, proxies=None, expected_code=None):
    """Sends an HTTPS POST request; returns the HTTP status code and the
    decoded response payload.

    By default, HTTP 301, 302 and 303 are followed; all other non-2XX
    responses result in a urllib.error.HTTPError. If expected_code is
    supplied, a urllib.error.HTTPError is raised unless the status code
    matches expected_code.
    """
    data = data or {}
    headers = headers or {}
    proxies = {'https': proxies['https']} if proxies.get('https') else {}
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler,
        urllib.request.ProxyHandler(proxies),
        urllib.request.HTTPRedirectHandler,
    )
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode('ascii'),
        headers=headers,
    )
    resp = opener.open(req)
    code = resp.getcode()
    if expected_code is not None and code != expected_code:
        raise urllib.error.HTTPError(resp.geturl(), code, resp.msg, resp.info(), resp)
    payload = resp.read()
    try:
        payload = gzip.decompress(payload)
    except OSError:
        pass
    finally:
        payload = payload.decode('utf-8')
    return code, payload


def unwrap(text):
    """Unwrap text."""
    lines = text.split('\n')
    result = ''
    for i in range(len(lines) - 1):
        result += lines[i]
        if not lines[i]:
            # Paragraph break
            result += '\n\n'
        elif lines[i + 1]:
            # Next line is not paragraph break, add space
            result += ' '
    # Handle last line
    result += lines[-1] if lines[-1] else '\n'
    return result


def check_stdout_encoding():
    """Make sure stdout encoding is utf-8.

    If not, print error message and instructions, then exit with
    status 1.

    This function is a no-op on win32 because encoding on win32 is
    messy, and let's just hope for the best. /s
    """
    if sys.platform == 'win32':
        return

    # Use codecs.lookup to resolve text encoding alias
    encoding = codecs.lookup(sys.stdout.encoding).name
    if encoding != 'utf-8':
        locale_lang, locale_encoding = locale.getlocale()
        if locale_lang is None:
            locale_lang = '<unknown>'
        if locale_encoding is None:
            locale_encoding = '<unknown>'
        ioencoding = os.getenv('PYTHONIOENCODING', 'not set')
        sys.stderr.write(unwrap(textwrap.dedent("""\
        stdout encoding '{encoding}' detected. ddgr requires utf-8 to
        work properly. The wrong encoding may be due to a non-UTF-8
        locale or an improper PYTHONIOENCODING. (For the record, your
        locale language is {locale_lang} and locale encoding is
        {locale_encoding}; your PYTHONIOENCODING is {ioencoding}.)

        Please set a UTF-8 locale (e.g., en_US.UTF-8) or set
        PYTHONIOENCODING to utf-8.
        """.format(
            encoding=encoding,
            locale_lang=locale_lang,
            locale_encoding=locale_encoding,
            ioencoding=ioencoding,
        ))))
        sys.exit(1)


def printerr(msg):
    """Print message, verbatim, to stderr.

    ``msg`` could be any stringifiable value.
    """
    print(msg, file=sys.stderr)


# Monkeypatch textwrap for CJK wide characters.
def monkeypatch_textwrap_for_cjk():
    try:
        if textwrap.wrap.patched:
            return
    except AttributeError:
        pass
    psl_textwrap_wrap = textwrap.wrap

    def textwrap_wrap(text, width=70, **kwargs):
        if width <= 2:
            width = 2
        # We first add a U+0000 after each East Asian Fullwidth or East
        # Asian Wide character, then fill to width - 1 (so that if a NUL
        # character ends up on a new line, we still have one last column
        # to spare for the preceding wide character). Finally we strip
        # all the NUL characters.
        #
        # East Asian Width: https://www.unicode.org/reports/tr11/
        return [
            line.replace('\0', '')
            for line in psl_textwrap_wrap(
                ''.join(
                    ch + '\0' if unicodedata.east_asian_width(ch) in ('F', 'W') else ch
                    for ch in unicodedata.normalize('NFC', text)
                ),
                width=width - 1,
                **kwargs
            )
        ]

    def textwrap_fill(text, width=70, **kwargs):
        return '\n'.join(textwrap_wrap(text, width=width, **kwargs))
    textwrap.wrap = textwrap_wrap
    textwrap.fill = textwrap_fill
    textwrap.wrap.patched = True
    textwrap.fill.patched = True


monkeypatch_textwrap_for_cjk()


# Classes

class DdgUrl:
    """
    This class constructs the DuckDuckGo Search/News URL.

    This class is modeled on urllib.parse.ParseResult for familiarity,
    which means it supports reading of all six attributes -- scheme,
    netloc, path, params, query, fragment -- of
    urllib.parse.ParseResult, as well as the geturl() method.

    However, the attributes (properties) and methods listed below should
    be the preferred methods of access to this class.

    Parameters
    ----------
    opts : dict or argparse.Namespace, optional
        See the ``opts`` parameter of `update`.

    Other Parameters
    ----------------
    See "Other Parameters" of `update`.

    Attributes
    ----------
    hostname : str
        Read-write property.
    keywords : str or list of strs
        Read-write property.
    news : bool
        Read-only property.
    url : str
        Read-only property.

    Methods
    -------
    full()
    update(opts=None, **kwargs)
    set_queries(**kwargs)
    unset_queries(*args)
    next_page()
    prev_page()
    first_page()

    """

    def __init__(self, opts=None, **kwargs):
        self.scheme = 'https'
        # self.netloc is a calculated property
        self.path = '/html/'
        self.params = ''
        # self.query is a calculated property
        self.fragment = ''

        self._duration = ''  # duration as day, week, month or unlimited
        self._region = ''  # Region code
        self._qrycnt = 0  # Number of search results fetched in most recent query
        self._curindex = 1  # Index of total results in pages fetched so far + 1
        self._page = 0  # Current page number
        self._keywords = []
        self._sites = None
        self._safe = 1  # Safe search parameter value
        self.np_prev = ''  # nextParams from last html page Previous button
        self.np_next = ''  # nextParams from last html page Next button
        self._query_dict = {
        }
        self.update(opts, **kwargs)

    def __str__(self):
        return self.url

    @property
    def url(self):
        """The full DuckDuckGo URL you want."""
        return self.full()

    @property
    def hostname(self):
        """The hostname."""
        return self.netloc

    @hostname.setter
    def hostname(self, hostname):
        self.netloc = hostname

    @property
    def keywords(self):
        """The keywords, either a str or a list of strs."""
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        self._keywords = keywords

    @property
    def news(self):
        """Whether the URL is for DuckDuckGo News."""
        return 'tbm' in self._query_dict and self._query_dict['tbm'] == 'nws'

    def full(self):
        """Return the full URL.

        Returns
        -------
        str

        """
        q = ''
        if self._keywords:
            if isinstance(self._keywords, list):
                q += '+'.join(list(self._keywords))
            else:
                q += self._keywords

        url = (self.scheme + ':') if self.scheme else ''
        url += '//' + self.netloc + '/?q=' + q
        return url

    def update(self, opts=None, **kwargs):
        """Update the URL with the given options.

        Parameters
        ----------
        opts : dict or argparse.Namespace, optional
            Carries options that affect the DuckDuckGo Search/News URL. The
            list of currently recognized option keys with expected value
            types:

                keywords: str or list of strs
                num: int

        Other Parameters
        ----------------
        kwargs
            The `kwargs` dict extends `opts`, that is, options can be
            specified either way, in `opts` or as individual keyword
            arguments.

        """

        if opts is None:
            opts = {}
        if hasattr(opts, '__dict__'):
            opts = opts.__dict__
        opts.update(kwargs)

        if 'keywords' in opts:
            self._keywords = opts['keywords']
        self._duration = opts['duration']
        if 'region' in opts:
            self._region = opts['region']
        if 'num' in opts:
            self._qrycnt = 0
        if 'sites' in opts:
            self._sites = opts['sites']
        if 'unsafe' in opts and opts['unsafe']:
            self._safe = -2

    def set_queries(self, **kwargs):
        """Forcefully set queries outside the normal `update` mechanism.

        Other Parameters
        ----------------
        kwargs
            Arbitrary key value pairs to be set in the query string. All
            keys and values should be stringifiable.

            Note that certain keys, e.g., ``q``, have their values
            constructed on the fly, so setting those has no actual
            effect.

        """
        for k, v in kwargs.items():
            self._query_dict[k] = v

    def unset_queries(self, *args):
        """Forcefully unset queries outside the normal `update` mechanism.

        Other Parameters
        ----------------
        args
            Arbitrary keys to be unset. No exception is raised if a key
            does not exist in the first place.

            Note that certain keys, e.g., ``q``, are always included in
            the resulting URL, so unsetting those has no actual effect.

        """
        for k in args:
            self._query_dict.pop(k, None)

    def next_page(self):
        """Navigate to the next page."""
        self._page = self._page + 1

        if self._curindex > 0:
            self._curindex = self._curindex + self._qrycnt
        else:
            self._curindex = -self._curindex

    def prev_page(self):
        """Navigate to the previous page.

        Raises
        ------
        ValueError
            If already at the first page (``page=0`` in the current
            query string).

        """
        if self._page == 0:
            raise ValueError('Already at the first page.')

        self._page = self._page - 1

        if self._curindex > 0:
            self._curindex = -self._curindex  # A negative index is used when fetching previous page
        else:
            self._curindex = self._curindex + self._qrycnt

    def first_page(self):
        """Navigate to the first page.

        Raises
        ------
        ValueError
            If already at the first page (``page=0`` in the current
            query string).

        """
        if self._page == 0:
            raise ValueError('Already at the first page.')
        self._page = 0
        self._qrycnt = 0
        self._curindex = 1

    @property
    def netloc(self):
        """The hostname."""
        return 'duckduckgo.com'

    def query(self):
        """The query string."""
        qd = {}
        qd.update(self._query_dict)
        qd['duration'] = self._duration
        qd['region'] = self._region
        qd['curindex'] = self._curindex
        qd['page'] = self._page
        qd['safe'] = self._safe
        if self._curindex < 0:
            qd['nextParams'] = self.np_prev
        else:
            qd['nextParams'] = self.np_next

        # Construct the q query
        q = ''
        keywords = self._keywords
        sites = self._sites
        if keywords:
            if isinstance(keywords, list):
                q += ' '.join(list(keywords))
            else:
                q += keywords
        if sites:
            q += ' site:' + ','.join(urllib.parse.quote_plus(site) for site in sites)
        qd['q'] = q

        return qd

    def update_num(self, count):
        self._qrycnt = count


class DdgAPIUrl:
    """
    This class constructs the DuckDuckGo Instant Answer API URL.

    Attributes
    ----------
    hostname : str
        Read-write property.
    keywords : str or list of strs
        Read-write property.
    url : str
        Read-only property.
    netloc : str
        Read-only property.

    Methods
    -------
    full()

    """

    def __init__(self, keywords):
        self.scheme = 'https'
        self.path = '/'
        self.params = ''
        self._format = 'format=json'
        self._keywords = keywords

    def __str__(self):
        return self.url

    @property
    def url(self):
        """The full DuckDuckGo URL you want."""
        return self.full()

    @property
    def hostname(self):
        """The hostname."""
        return self.netloc

    @hostname.setter
    def hostname(self, hostname):
        self.netloc = hostname

    @property
    def keywords(self):
        """The keywords, either a str or a list of strs."""
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        self._keywords = keywords

    @property
    def netloc(self):
        """The hostname."""
        return 'api.duckduckgo.com'

    def full(self):
        """Return the full URL.

        Returns
        -------
        str

        """
        q = ''
        if self._keywords:
            if isinstance(self._keywords, list):
                q += '+'.join(list(self._keywords))
            else:
                q += self._keywords

        url = (self.scheme + ':') if self.scheme else ''
        url += '//' + self.netloc + '/?q=' + q + "&" + self._format
        return url


class DDGConnectionError(Exception):
    pass


class DdgConnection:
    """
    This class facilitates connecting to and fetching from DuckDuckGo.

    Parameters
    ----------
    See http.client.HTTPSConnection for documentation of the
    parameters.

    Raises
    ------
    DDGConnectionError

    Methods
    -------
    fetch_page(url)

    """

    def __init__(self, proxy=None, ua=''):
        self._u = 'https://duckduckgo.com/html'

        self._proxies = {
            'https': proxy if proxy is not None else (os.getenv('https_proxy')
                                                      if os.getenv('https_proxy') is not None
                                                      else os.getenv('HTTPS_PROXY'))
        }
        self._ua = ua

    def fetch_page(self, url):
        """Fetch a URL.

        Allows one reconnection and one redirection before failing and
        raising DDGConnectionError.

        Parameters
        ----------
        url : str
            The URL to fetch, relative to the host.

        Raises
        ------
        DDGConnectionError
            When not getting HTTP 200 even after the allowed one
            reconnection and/or one redirection, or when DuckDuckGo is
            blocking query due to unsual activity.

        Returns
        -------
        str
            Response payload, gunzipped (if applicable) and decoded (in UTF-8).

        """
        dic = url.query()
        page = dic['page']
        LOGDBG('q:%s, region:%s, page:%d, curindex:%d, safe:%d', dic['q'], dic['region'], page, dic['curindex'], dic['safe'])
        LOGDBG('nextParams:%s', dic['nextParams'])
        LOGDBG('proxy:%s', self._proxies)
        LOGDBG('ua:%s', self._ua)

        try:
            if page == 0:
                _, r = https_post(self._u,
                                  headers={
                                      'Accept-Encoding': 'gzip',
                                      'User-Agent': self._ua,
                                      'DNT': '1',
                                  },
                                  data={
                                      'q': dic['q'],
                                      'b': '',
                                      'df': dic['duration'],
                                      'kf': '-1',
                                      'kh': '1',
                                      'kl': dic['region'],
                                      'kp': dic['safe'],
                                      'k1': '-1',
                                  },
                                  proxies=self._proxies,
                                  expected_code=200)
            else:
                _, r = https_post(self._u,
                                  headers={
                                      'Accept-Encoding': 'gzip',
                                      'User-Agent': self._ua,
                                      'DNT': '1',
                                  },
                                  data={
                                      'q': dic['q'],  # The query string
                                      's': str(50 * (page - 1) + 30),  # Page index
                                      'nextParams': dic['nextParams'],  # nextParams from last visited page
                                      'v': 'l',
                                      'o': 'json',
                                      'dc': str(dic['curindex']),  # Start from total fetched result index
                                      'df': dic['duration'],
                                      'api': '/d.js',
                                      'kf': '-1',  # Disable favicons
                                      'kh': '1',  # HTTPS always ON
                                      'kl': dic['region'],  # Region code
                                      'kp': dic['safe'],  # Safe search
                                      'k1': '-1',  # Advertisements off
                                  },
                                  proxies=self._proxies,
                                  expected_code=200)
        except Exception as e:
            LOGERR(e)
            return None

        return r


def annotate_tag(annotated_starttag_handler):
    # See parser logic within the DdgParser class for documentation.
    #
    # annotated_starttag_handler(self, tag: str, attrsdict: dict) -> annotation
    # Returns: HTMLParser.handle_starttag(self, tag: str, attrs: list) -> None

    def handler(self, tag, attrs):
        attrs = dict(attrs)
        annotation = annotated_starttag_handler(self, tag, attrs)
        self.insert_annotation(tag, annotation)

    return handler


def retrieve_tag_annotation(annotated_endtag_handler):
    # See parser logic within the DdgParser class for documentation.
    #
    # annotated_endtag_handler(self, tag: str, annotation) -> None
    # Returns: HTMLParser.handle_endtag(self, tag: str) -> None

    def handler(self, tag):
        try:
            annotation = self.tag_annotations[tag].pop()
        except IndexError:
            # Malformed HTML -- more close tags than open tags
            annotation = None
        annotated_endtag_handler(self, tag, annotation)

    return handler


class DdgParser(html.parser.HTMLParser):
    """The members of this class parse the result HTML
    page fetched from DuckDuckGo server for a query.

    The custom parser looks for tags enclosing search
    results and extracts the URL, title and text for
    each search result.

    After parsing the complete HTML page results are
    returned in a list of objects of class Result.
    """

    # Parser logic:
    #
    # - Guiding principles:
    #
    #   1. Tag handlers are contextual;
    #
    #   2. Contextual starttag and endtag handlers should come in pairs
    #      and have a clear hierarchy;
    #
    #   3. starttag handlers should only yield control to a pair of
    #      child handlers (that is, one level down the hierarchy), and
    #      correspondingly, endtag handlers should only return control
    #      to the parent (that is, the pair of handlers that gave it
    #      control in the first place).
    #
    #   Principle 3 is meant to enforce a (possibly implicit) stack
    #   structure and thus prevent careless jumps that result in what's
    #   essentially spaghetti code with liberal use of GOTOs.
    #
    # - HTMLParser.handle_endtag gives us a bare tag name without
    #   context, which is not good for enforcing principle 3 when we
    #   have, say, nested div tags.
    #
    #   In order to precisely identify the matching opening tag, we
    #   maintain a stack for each tag name with *annotations*. Important
    #   opening tags (e.g., the ones where child handlers are
    #   registered) can be annotated so that when we can watch for the
    #   annotation in the endtag handler, and when the appropriate
    #   annotation is popped, we perform the corresponding action (e.g.,
    #   switch back to old handlers).
    #
    #   To facilitate this, each starttag handler is decorated with
    #   @annotate_tag, which accepts a return value that is the
    #   annotation (None by default), and additionally converts attrs to
    #   a dict, which is much easier to work with; and each endtag
    #   handler is decorated with @retrieve_tag_annotation which sends
    #   an additional parameter that is the retrieved annotation to the
    #   handler.
    #
    #   Note that some of our tag annotation stacks leak over time: this
    #   happens to tags like <img> and <hr> which are not
    #   closed. However, these tags play no structural role, and come
    #   only in small quantities, so it's not really a problem.
    #
    # - All textual data (result title, result abstract, etc.) are
    #   processed through a set of shared handlers. These handlers store
    #   text in a shared buffer self.textbuf which can be retrieved and
    #   cleared at appropriate times.
    #
    #   Data (including charrefs and entityrefs) are ignored initially,
    #   and when data needs to be recorded, the start_populating_textbuf
    #   method is called to register the appropriate data, charref and
    #   entityref handlers so that they append to self.textbuf. When
    #   recording ends, pop_textbuf should be called to extract the text
    #   and clear the buffer. stop_populating_textbuf returns the
    #   handlers to their pristine state (ignoring data).
    #
    #   Methods:
    #   - start_populating_textbuf(self, data_transformer: Callable[[str], str]) -> None
    #   - pop_textbuf(self) -> str
    #   - stop_populating_textbuf(self) -> None
    #
    # - Outermost starttag and endtag handler methods: root_*. The whole
    #   parser starts and ends in this state.
    #
    # - Each result is wrapped in a <div> tag with class "links_main".
    #
    #   <!-- within the scope of root_* -->
    #   <div class="links_main">  <!-- annotate as 'result', hand over to result_* -->
    #   </div>                    <!-- hand back to root_*, register result -->
    #
    # - For each result, the first <h2> tag with class "result__title" contains the
    #   hyperlinked title.
    #
    #   <!-- within the scope of result_* -->
    #   <h2 class="result__title">  <!-- annotate as 'title', hand over to title_* -->
    #   </h2>                       <!-- hand back to result_* -->
    #
    # - Abstracts are within the scope of <div> tag with class "links_main". Links in
    #   abstract are ignored as they are available within <h2> tag.
    #
    #   <!-- within the scope of result_* -->
    #   <a class="result__snippet">  <!-- annotate as 'abstract', hand over to abstract_* -->
    #   </a>                         <!-- hand back to result_* -->
    #
    # - Each title looks like
    #
    #   <h2 class="result__title">
    #     <!-- within the scope of title_* -->
    #     <a href="result url">  <!-- register self.url, annotate as 'title_link',
    #                                 start_populating_textbuf -->
    #       result title
    #       <span>               <!-- filetype (optional), annotate as title_filetype,
    #                                 start_populating_textbuf -->
    #         file type (e.g. [PDF])
    #       </span>              <!-- stop_populating_textbuf, update self.filetype,
    #                                 start_populating_tetbuf -->
    #     </a>                   <!-- stop_populating_textbuf, pop to self.title
    #                                 prepend self.filetype, if available -->
    #   </h2>

    def __init__(self, offset=0):
        html.parser.HTMLParser.__init__(self)

        self.title = ''
        self.url = ''
        self.abstract = ''
        self.filetype = ''

        self.results = []
        self.index = offset
        self.textbuf = ''
        self.click_result = ''
        self.tag_annotations = {}
        self.np_prev_button = ''
        self.np_next_button = ''
        self.npfound = False  # First next params found
        self.set_handlers_to('root')

    # Tag handlers

    @annotate_tag
    def root_start(self, tag, attrs):
        if tag == 'div':
            if 'zci__result' in self.classes(attrs):
                self.start_populating_textbuf()
                return 'click_result'

            if 'links_main' in self.classes(attrs):
                # Initialize result field registers
                self.title = ''
                self.url = ''
                self.abstract = ''
                self.filetype = ''

                self.set_handlers_to('result')
                return 'result'

            if 'nav-link' in self.classes(attrs):
                self.set_handlers_to('input')
                return 'input'
        return ''

    @retrieve_tag_annotation
    def root_end(self, tag, annotation):
        if annotation == 'click_result':
            self.stop_populating_textbuf()
            self.click_result = self.pop_textbuf()
            self.set_handlers_to('root')

    @annotate_tag
    def result_start(self, tag, attrs):
        if tag == 'h2' and 'result__title' in self.classes(attrs):
            self.set_handlers_to('title')
            return 'title'

        if tag == 'a' and 'result__snippet' in self.classes(attrs) and 'href' in attrs:
            self.start_populating_textbuf()
            return 'abstract'

        return ''

    @retrieve_tag_annotation
    def result_end(self, tag, annotation):
        if annotation == 'abstract':
            self.stop_populating_textbuf()
            self.abstract = self.pop_textbuf()
        elif annotation == 'result':
            if self.url:
                self.index += 1
                result = Result(self.index, self.title, self.url, self.abstract, None)
                self.results.append(result)
            self.set_handlers_to('root')

    @annotate_tag
    def title_start(self, tag, attrs):
        if tag == 'span':
            # Print a space after the filetype indicator
            self.start_populating_textbuf(lambda text: '[' + text + ']')
            return 'title_filetype'

        if tag == 'a' and 'href' in attrs:
            # Skip 'News for', 'Images for' search links
            if attrs['href'].startswith('/search'):
                return ''

            self.url = attrs['href']
            try:
                start = self.url.index('?q=') + len('?q=')
                end = self.url.index('&sa=', start)
                self.url = urllib.parse.unquote_plus(self.url[start:end])
            except ValueError:
                pass
            self.start_populating_textbuf()
            return 'title_link'

        return ''

    @retrieve_tag_annotation
    def title_end(self, tag, annotation):
        if annotation == 'title_filetype':
            self.stop_populating_textbuf()
            self.filetype = self.pop_textbuf()
            self.start_populating_textbuf()
        elif annotation == 'title_link':
            self.stop_populating_textbuf()
            self.title = self.pop_textbuf()
            if self.filetype != '':
                self.title = self.filetype + self.title
        elif annotation == 'title':
            self.set_handlers_to('result')

    @annotate_tag
    def abstract_start(self, tag, attrs):
        if tag == 'span' and 'st' in self.classes(attrs):
            self.start_populating_textbuf()
            return 'abstract_text'
        return ''

    @retrieve_tag_annotation
    def abstract_end(self, tag, annotation):
        if annotation == 'abstract_text':
            self.stop_populating_textbuf()
            self.abstract = self.pop_textbuf()
        elif annotation == 'abstract':
            self.set_handlers_to('result')

    @annotate_tag
    def input_start(self, tag, attrs):
        if tag == 'input' and 'name' in attrs:
            if attrs['name'] == 'nextParams' and attrs['value'] != '':
                # The previous button always shows before next button
                # If there's only 1 button (page 1), it's the next button
                if self.npfound is True:
                    self.np_prev_button = self.np_next_button
                else:
                    self.npfound = True

                self.np_next_button = attrs['value']
                return

    @retrieve_tag_annotation
    def input_end(self, tag, annotation):
        return

    # Generic methods

    # Set handle_starttag to SCOPE_start, and handle_endtag to SCOPE_end.
    def set_handlers_to(self, scope):
        self.handle_starttag = getattr(self, scope + '_start')
        self.handle_endtag = getattr(self, scope + '_end')

    def insert_annotation(self, tag, annotation):
        if tag not in self.tag_annotations:
            self.tag_annotations[tag] = []
        self.tag_annotations[tag].append(annotation)

    def start_populating_textbuf(self, data_transformer=None):
        if data_transformer is None:
            # Record data verbatim
            self.handle_data = self.record_data
        else:
            def record_transformed_data(data):
                self.textbuf += data_transformer(data)

            self.handle_data = record_transformed_data

        self.handle_entityref = self.record_entityref
        self.handle_charref = self.record_charref

    def pop_textbuf(self):
        text = self.textbuf
        self.textbuf = ''
        return text

    def stop_populating_textbuf(self):
        self.handle_data = lambda data: None
        self.handle_entityref = lambda ref: None
        self.handle_charref = lambda ref: None

    def record_data(self, data):
        self.textbuf += data

    def record_entityref(self, ref):
        try:
            self.textbuf += chr(html.entities.name2codepoint[ref])
        except KeyError:
            # Entity name not found; most likely rather sloppy HTML
            # where a literal ampersand is not escaped; For instance,
            # containing the following tag
            #
            #     <p class="_e4b"><a href="...">expected market return s&p 500</a></p>
            #
            # where &p is interpreted by HTMLParser as an entity (this
            # behaviour seems to be specific to Python 2.7).
            self.textbuf += '&' + ref

    def record_charref(self, ref):
        if ref.startswith('x'):
            char = chr(int(ref[1:], 16))
        else:
            char = chr(int(ref))
        self.textbuf += char

    @staticmethod
    def classes(attrs):
        """Get tag's classes from its attribute dict."""
        return attrs.get('class', '').split()

    def error(self, message):
        raise NotImplementedError("subclasses of ParserBase must override error()")


Colors = collections.namedtuple('Colors', 'index, title, url, metadata, abstract, prompt, reset')


class Result:
    """
    Container for one search result, with output helpers.

    Parameters
    ----------
    index : int or str
    title : str
    url : str
    abstract : str
    metadata : str, optional
        Only applicable to DuckDuckGo News results, with publisher name and
        publishing time.

    Attributes
    ----------
    index : str
    title : str
    url : str
    abstract : str
    metadata : str or None

    Class Variables
    ---------------
    colors : str

    Methods
    -------
    print()
    jsonizable_object()
    urltable()

    """

    # Class variables
    colors = None
    urlexpand = False

    def __init__(self, index, title, url, abstract, metadata=None):
        index = str(index)
        self.index = index
        self.title = title
        self.url = url
        self.abstract = abstract
        self.metadata = metadata

        self._urltable = {index: url}

    def _print_title_and_url(self, index, title, url):
        indent = INDENT - 2
        colors = self.colors

        if not self.urlexpand:
            url = '[' + urllib.parse.urlparse(url).netloc + ']'

        if colors:
            # Adjust index to print result index clearly
            print(" %s%-*s%s" % (colors.index, indent, index + '.', colors.reset), end='')
            if not self.urlexpand:
                print(' ' + colors.title + title + colors.reset + ' ' + colors.url + url + colors.reset)
            else:
                print(' ' + colors.title + title + colors.reset)
                print(' ' * (INDENT) + colors.url + url + colors.reset)
        else:
            if self.urlexpand:
                print(' %-*s %s' % (indent, index + '.', title))
                print(' %s%s' % (' ' * (indent + 1), url))
            else:
                print(' %-*s %s %s' % (indent, index + '.', title, url))

    def _print_metadata_and_abstract(self, abstract, metadata=None):
        colors = self.colors
        try:
            columns, _ = os.get_terminal_size()
        except OSError:
            columns = 0

        if metadata:
            if colors:
                print(' ' * INDENT + colors.metadata + metadata + colors.reset)
            else:
                print(' ' * INDENT + metadata)

        if colors:
            print(colors.abstract, end='')
        if columns > INDENT + 1:
            # Try to fill to columns
            fillwidth = columns - INDENT - 1
            for line in textwrap.wrap(abstract.replace('\n', ''), width=fillwidth):
                print('%s%s' % (' ' * INDENT, line))
            print('')
        else:
            print('%s\n' % abstract.replace('\n', ' '))
        if colors:
            print(colors.reset, end='')

    def print(self):
        """Print the result entry."""

        self._print_title_and_url(self.index, self.title, self.url)
        self._print_metadata_and_abstract(self.abstract, metadata=self.metadata)

    def print_paginated(self, display_index):
        """Print the result entry with custom index."""

        self._print_title_and_url(display_index, self.title, self.url)
        self._print_metadata_and_abstract(self.abstract, metadata=self.metadata)

    def jsonizable_object(self):
        """Return a JSON-serializable dict representing the result entry."""
        obj = {
            'title': self.title,
            'url': self.url,
            'abstract': self.abstract
        }
        if self.metadata:
            obj['metadata'] = self.metadata
        return obj

    def urltable(self):
        """Return a index-to-URL table for the current result.

        Normally, the table contains only a single entry, but when the result
        contains sitelinks, all sitelinks are included in this table.

        Returns
        -------
        dict
            A dict mapping indices (strs) to URLs (also strs).

        """
        return self._urltable


class DdgCmdException(Exception):
    pass


class NoKeywordsException(DdgCmdException):
    pass


def require_keywords(method):
    # Require keywords to be set before we run a DdgCmd method. If
    # no keywords have been set, raise a NoKeywordsException.
    @functools.wraps(method)
    def enforced_method(self, *args, **kwargs):
        if not self.keywords:
            raise NoKeywordsException('No keywords.')
        method(self, *args, **kwargs)

    return enforced_method


def no_argument(method):
    # Normalize a do_* method of DdgCmd that takes no argument to
    # one that takes an arg, but issue a warning when an nonempty
    # argument is given.
    @functools.wraps(method)
    def enforced_method(self, arg):
        if arg:
            method_name = arg.__name__
            command_name = method_name[3:] if method_name.startswith('do_') else method_name
            LOGGER.warning("Argument to the '%s' command ignored.", command_name)
        method(self)

    return enforced_method


class DdgCmd:
    """
    Command line interpreter and executor class for ddgr.

    Inspired by PSL cmd.Cmd.

    Parameters
    ----------
    opts : argparse.Namespace
        Options and/or arguments.

    Attributes
    ----------
    options : argparse.Namespace
        Options that are currently in effect. Read-only attribute.
    keywords : str or list or strs
        Current keywords. Read-only attribute

    Methods
    -------
    fetch()
    display_results(prelude='\n', json_output=False)
    fetch_and_display(prelude='\n', json_output=False)
    read_next_command()
    help()
    cmdloop()

    """

    def __init__(self, opts, ua):
        super().__init__()
        self.cmd = ''
        self.index = 0
        self._opts = opts

        self._ddg_url = DdgUrl(opts)
        proxy = opts.proxy if hasattr(opts, 'proxy') else None
        self._conn = DdgConnection(proxy=proxy, ua=ua)

        self.results = []
        self._urltable = {}

        colors = self.colors
        message = 'ddgr (? for help)'
        self.prompt = ((colors.prompt + message + colors.reset + ' ')
                       if (colors and os.getenv('DISABLE_PROMPT_COLOR') is None) else (message + ': '))

    @property
    def options(self):
        """Current options."""
        return self._opts

    @property
    def keywords(self):
        """Current keywords."""
        return self._ddg_url.keywords

    @require_keywords
    def fetch(self, json_output=False):
        """Fetch a page and parse for results.

        Results are stored in ``self.results``.

        Parameters
        ----------
        json_output : bool, optional
            Whether to dump results in JSON format. Default is False.

        Raises
        ------
        DDGConnectionError

        See Also
        --------
        fetch_and_display

        """
        # This method also sets self._urltable.
        page = self._conn.fetch_page(self._ddg_url)

        if page is None:
            return

        if LOGGER.isEnabledFor(logging.DEBUG):
            fd, tmpfile = tempfile.mkstemp(prefix='ddgr-response-')
            os.close(fd)
            with open(tmpfile, 'w', encoding='utf-8') as fp:
                fp.write(page)
            LOGDBG("Response body written to '%s'.", tmpfile)

        if self._opts.num:
            _index = len(self._urltable)
        else:
            _index = 0
            self._urltable = {}

        parser = DdgParser(offset=_index)
        parser.feed(page)

        if self._opts.num:
            self.results.extend(parser.results)
        else:
            self.results = parser.results

        for r in parser.results:
            self._urltable.update(r.urltable())

        self._ddg_url.np_prev = parser.np_prev_button
        self._ddg_url.np_next = parser.np_next_button

        # Show instant answer
        if self.index == 0 and parser.click_result and not json_output:
            if self.colors:
                print(self.colors.abstract)

            try:
                columns, _ = os.get_terminal_size()
            except OSError:
                columns = 0

            fillwidth = columns - INDENT
            for line in textwrap.wrap(parser.click_result.strip(), width=fillwidth):
                print('%s%s' % (' ' * INDENT, line))

            if self.colors:
                print(self.colors.reset, end='')
        LOGDBG('Prev nextParams: %s', self._ddg_url.np_prev)
        LOGDBG('Next nextParams: %s', self._ddg_url.np_next)

        self._ddg_url.update_num(len(parser.results))

    @require_keywords
    def display_results(self, prelude='\n', json_output=False):
        """Display results stored in ``self.results``.

        Parameters
        ----------
        See `fetch_and_display`.

        """

        if self._opts.num:
            results = self.results[self.index:(self.index + self._opts.num)]
        else:
            results = self.results

        if json_output:
            # JSON output
            results_object = [r.jsonizable_object() for r in results]
            print(json.dumps(results_object, indent=2, sort_keys=True, ensure_ascii=False))
        elif not results:
            print('No results.', file=sys.stderr)
        elif self._opts.num:  # Paginated output
            sys.stderr.write(prelude)
            for i, r in enumerate(results):
                r.print_paginated(str(i + 1))
        else:  # Regular output
            sys.stderr.write(prelude)
            for r in results:
                r.print()

    @require_keywords
    def fetch_and_display(self, prelude='\n', json_output=False):
        """Fetch a page and display results.

        Results are stored in ``self.results``.

        Parameters
        ----------
        prelude : str, optional
            A string that is written to stderr before showing actual results,
            usually serving as a separator. Default is an empty line.
        json_output : bool, optional
            Whether to dump results in JSON format. Default is False.

        Raises
        ------
        DDGConnectionError

        See Also
        --------
        fetch
        display_results

        """
        self.fetch()
        self.display_results(prelude=prelude, json_output=json_output)

    def read_next_command(self):
        """Show omniprompt and read user command line.

        Command line is always stripped, and each consecutive group of
        whitespace is replaced with a single space character. If the
        command line is empty after stripping, when ignore it and keep
        reading. Exit with status 0 if we get EOF or an empty line
        (pre-strip, that is, a raw <enter>) twice in a row.

        The new command line (non-empty) is stored in ``self.cmd``.

        """
        enter_count = 0
        while True:
            try:
                cmd = input(self.prompt)
            except EOFError:
                sys.exit(0)

            if not cmd:
                enter_count += 1
                if enter_count == 2:
                    # Double <enter>
                    sys.exit(0)
            else:
                enter_count = 0

            cmd = ' '.join(cmd.split())
            if cmd:
                self.cmd = cmd
                break

    @staticmethod
    def help():
        DdgArgumentParser.print_omniprompt_help(sys.stderr)
        printerr('')

    @require_keywords
    @no_argument
    def do_first(self):
        if self._opts.num:
            if self.index < self._opts.num:
                print('Already at the first page.', file=sys.stderr)
            else:
                self.index = 0
                self.display_results()
            return

        try:
            self._ddg_url.first_page()
        except ValueError as e:
            print(e, file=sys.stderr)
            return

        self.fetch_and_display()

    def do_ddg(self, arg):
        if self._opts.num:
            self.index = 0
            self.results = []
            self._urltable = {}
        # Update keywords and reconstruct URL
        self._opts.keywords = arg
        self._ddg_url = DdgUrl(self._opts)
        # If there is a Bang, let DuckDuckGo do the work
        if arg[0] == '!' or (len(arg) > 1 and arg[1] == '!'):
            open_url(self._ddg_url.full())
        else:
            self.fetch_and_display()

    @require_keywords
    @no_argument
    def do_next(self):
        if self._opts.num:
            count = len(self.results)
            if self._ddg_url._qrycnt == 0 and self.index >= count:
                print('No results.', file=sys.stderr)
                return

            self.index += self._opts.num
            if count - self.index < self._opts.num:
                self._ddg_url.next_page()
                self.fetch_and_display()
            else:
                self.display_results()
        elif self._ddg_url._qrycnt == 0:
            # If no results were fetched last time, we have hit the last page already
            print('No results.', file=sys.stderr)
        else:
            self._ddg_url.next_page()
            self.fetch_and_display()

    def handle_range(self, nav, low, high):
        try:
            if self._opts.num:
                vals = [int(x) + self.index for x in nav.split('-')]
            else:
                vals = [int(x) for x in nav.split('-')]

            if len(vals) != 2:
                printerr('Invalid range %s.' % nav)
                return

            if vals[0] > vals[1]:
                vals[0], vals[1] = vals[1], vals[0]

            for _id in range(vals[0], vals[1] + 1):
                if self._opts.num and _id not in range(low, high):
                    printerr('Invalid index %s.' % (_id - self.index))
                    continue

                if str(_id) in self._urltable:
                    open_url(self._urltable[str(_id)])
                else:
                    printerr('Invalid index %s.' % _id)
        except ValueError:
            printerr('Invalid range %s.' % nav)

    @require_keywords
    def do_open(self, low, high, *args):
        if not args:
            printerr('Index or range missing.')
            return

        for nav in args:
            if nav == 'a':
                for key, _ in sorted(self._urltable.items()):
                    if self._opts.num and int(key) not in range(low, high):
                        continue
                    open_url(self._urltable[key])
            elif nav in self._urltable:
                if self._opts.num:
                    nav = str(int(nav) + self.index)
                    if int(nav) not in range(low, high):
                        printerr('Invalid index %s.' % (int(nav) - self.index))
                        continue
                open_url(self._urltable[nav])
            elif '-' in nav:
                self.handle_range(nav, low, high)
            else:
                printerr('Invalid index %s.' % nav)

    @require_keywords
    @no_argument
    def do_previous(self):
        if self._opts.num:
            if self.index < self._opts.num:
                print('Already at the first page.', file=sys.stderr)
            else:
                self.index -= self._opts.num
                self.display_results()
            return

        try:
            self._ddg_url.prev_page()
        except ValueError as e:
            print(e, file=sys.stderr)
            return

        self.fetch_and_display()

    def copy_url(self, idx):
        try:
            content = self._urltable[str(idx)].encode('utf-8')

            # try copying the url to clipboard using native utilities
            copier_params = []
            if sys.platform.startswith(('linux', 'freebsd', 'openbsd')):
                if shutil.which('xsel') is not None:
                    copier_params = ['xsel', '-b', '-i']
                elif shutil.which('xclip') is not None:
                    copier_params = ['xclip', '-selection', 'clipboard']
                # If we're using Termux (Android) use its 'termux-api'
                # add-on to set device clipboard.
                elif shutil.which('termux-clipboard-set') is not None:
                    copier_params = ['termux-clipboard-set']
            elif sys.platform == 'darwin':
                copier_params = ['pbcopy']
            elif sys.platform == 'win32':
                copier_params = ['clip']
            elif sys.platform.startswith('haiku'):
                copier_params = ['clipboard', '-i']

            if copier_params:
                Popen(copier_params, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL).communicate(content)
                return

            # If native clipboard utilities are absent, try to use terminal multiplexers
            # tmux
            if os.getenv('TMUX_PANE'):
                copier_params = ['tmux', 'set-buffer']
                Popen(copier_params + [content], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL).communicate()
                print('URL copied to tmux buffer.')
                return

            # GNU Screen paste buffer
            if os.getenv('STY'):
                copier_params = ['screen', '-X', 'readbuf', '-e', 'utf8']
                tmpfd, tmppath = tempfile.mkstemp()
                try:
                    with os.fdopen(tmpfd, 'wb') as fp:
                        fp.write(content)
                    copier_params.append(tmppath)
                    Popen(copier_params, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL).communicate()
                finally:
                    os.unlink(tmppath)
                return

            printerr('failed to locate suitable clipboard utility')
        except Exception:
            raise NoKeywordsException

    def cmdloop(self):
        """Run REPL."""
        if self.keywords:
            if self.keywords[0][0] == '!' or (
                    len(self.keywords[0]) > 1 and self.keywords[0][1] == '!'
            ):
                open_url(self._ddg_url.full())
            else:
                self.fetch_and_display()

        while True:
            self.read_next_command()
            # Automatic dispatcher
            #
            # We can't write a dispatcher for now because that could
            # change behaviour of the prompt. However, we have already
            # laid a lot of ground work for the dispatcher, e.g., the
            # `no_argument' decorator.

            _num = self._opts.num
            try:
                cmd = self.cmd
                if cmd == 'f':
                    self.do_first('')
                elif cmd.startswith('d '):
                    self.do_ddg(cmd[2:])
                elif cmd == 'n':
                    self.do_next('')
                elif cmd.startswith('o '):
                    self.do_open(self.index + 1, self.index + self._opts.num + 1, *cmd[2:].split())
                elif cmd.startswith('O '):
                    open_url.override_text_browser = True
                    self.do_open(self.index + 1, self.index + self._opts.num + 1, *cmd[2:].split())
                    open_url.override_text_browser = False
                elif cmd == 'p':
                    self.do_previous('')
                elif cmd == 'q':
                    break
                elif cmd == '?':
                    self.help()
                elif _num and cmd.isdigit() and int(cmd) in range(1, _num + 1):
                    open_url(self._urltable[str(int(cmd) + self.index)])
                elif _num == 0 and cmd in self._urltable:
                    open_url(self._urltable[cmd])
                elif self.keywords and cmd.isdigit() and int(cmd) < 100:
                    printerr('Index out of bound. To search for the number, use d.')
                elif cmd == 'x':
                    Result.urlexpand = not Result.urlexpand
                    self.display_results()
                elif cmd.startswith('c ') and cmd[2:].isdigit():
                    idx = int(cmd[2:])
                    if 0 < idx <= min(self._opts.num, len(self._urltable)):
                        self.copy_url(int(self.index) + idx)
                    else:
                        printerr("invalid index")
                else:
                    self.do_ddg(cmd)
            except KeyError:
                printerr('Index out of bound. To search for the number, use d.')
            except NoKeywordsException:
                printerr('Initiate a query first.')


class DdgArgumentParser(argparse.ArgumentParser):
    """Custom argument parser for ddgr."""

    # Print omniprompt help
    @staticmethod
    def print_omniprompt_help(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent("""
        omniprompt keys:
          n, p, f               fetch the next, prev or first set of search results
          index                 open the result corresponding to index in browser
          o [index|range|a ...] open space-separated result indices, ranges or all
          O [index|range|a ...] like key 'o', but try to open in a GUI browser
          d keywords            new DDG search for 'keywords' with original options
                                should be used to search omniprompt keys and indices
          x                     toggle url expansion
          c index               copy url to clipboard
          q, ^D, double Enter   exit ddgr
          ?                     show omniprompt help
          *                     other inputs are considered as new search keywords
        """))

    # Print information on ddgr
    @staticmethod
    def print_general_info(file=None):
        file = sys.stderr if file is None else file
        file.write(textwrap.dedent("""
        Version %s
        Copyright © 2016-2020 Arun Prakash Jana <engineerarun@gmail.com>
        License: GPLv3
        Webpage: https://github.com/jarun/ddgr
        """ % _VERSION_))

    # Augment print_help to print more than synopsis and options
    def print_help(self, file=None):
        super().print_help(file)
        self.print_omniprompt_help(file)
        self.print_general_info(file)

    # Automatically print full help text on error
    def error(self, message):
        sys.stderr.write('%s: error: %s\n\n' % (self.prog, message))
        self.print_help(sys.stderr)
        self.exit(2)

    # Type guards
    @staticmethod
    def positive_int(arg):
        """Try to convert a string into a positive integer."""
        try:
            n = int(arg)
            assert n > 0
            return n
        except (ValueError, AssertionError):
            raise argparse.ArgumentTypeError('%s is not a positive integer' % arg)

    @staticmethod
    def nonnegative_int(arg):
        """Try to convert a string into a nonnegative integer <= 25."""
        try:
            n = int(arg)
            assert n >= 0
            assert n <= 25
            return n
        except (ValueError, AssertionError):
            raise argparse.ArgumentTypeError('%s is not a non-negative integer <= 25' % arg)

    @staticmethod
    def is_duration(arg):
        """Check if a string is a valid duration accepted by DuckDuckGo.

        A valid duration is of the form dNUM, where d is a single letter h
        (hour), d (day), w (week), m (month), or y (year), and NUM is a
        non-negative integer.
        """
        try:
            if arg[0] not in ('h', 'd', 'w', 'm', 'y') or int(arg[1:]) < 0:
                raise ValueError
        except (TypeError, IndexError, ValueError):
            raise argparse.ArgumentTypeError('%s is not a valid duration' % arg)
        return arg

    @staticmethod
    def is_colorstr(arg):
        """Check if a string is a valid color string."""
        try:
            assert len(arg) == 6
            for c in arg:
                assert c in COLORMAP
        except AssertionError:
            raise argparse.ArgumentTypeError('%s is not a valid color string' % arg)
        return arg


# Miscellaneous functions

def python_version():
    return '%d.%d.%d' % sys.version_info[:3]


def get_colorize(colorize):
    if colorize == 'always':
        return True

    if colorize == 'auto':
        return sys.stdout.isatty()

    # colorize = 'never'
    return False


def set_win_console_mode():
    # VT100 control sequences are supported on Windows 10 Anniversary Update and later.
    # https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
    # https://docs.microsoft.com/en-us/windows/console/setconsolemode
    if platform.release() == '10':
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        try:
            from ctypes import windll, wintypes, byref
            kernel32 = windll.kernel32
            for nhandle in (STD_OUTPUT_HANDLE, STD_ERROR_HANDLE):
                handle = kernel32.GetStdHandle(nhandle)
                old_mode = wintypes.DWORD()
                if not kernel32.GetConsoleMode(handle, byref(old_mode)):
                    raise RuntimeError('GetConsoleMode failed')
                new_mode = old_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                if not kernel32.SetConsoleMode(handle, new_mode):
                    raise RuntimeError('SetConsoleMode failed')
            # Note: No need to restore at exit. SetConsoleMode seems to
            # be limited to the calling process.
        except Exception:
            pass


# Query autocompleter

# This function is largely experimental and could raise any exception;
# you should be prepared to catch anything. When it works though, it
# returns a list of strings the prefix could autocomplete to (however,
# it is not guaranteed that they start with the specified prefix; for
# instance, they won't if the specified prefix ends in a punctuation
# mark.)
def completer_fetch_completions(prefix):
    # One can pass the 'hl' query param to specify the language. We
    # ignore that for now.
    api_url = ('https://duckduckgo.com/ac/?q=%s&kl=wt-wt' %
               urllib.parse.quote(prefix, safe=''))
    # A timeout of 3 seconds seems to be overly generous already.
    resp = urllib.request.urlopen(api_url, timeout=3)
    respobj = json.loads(resp.read().decode('utf-8'))

    return [entry['phrase'] for entry in respobj]


def completer_run(prefix):
    if prefix:
        completions = completer_fetch_completions('+'.join(prefix.split()))
        if completions:
            print('\n'.join(completions))
    sys.exit(0)


def parse_args(args=None, namespace=None):
    """Parse ddgr arguments/options.

    Parameters
    ----------
    args : list, optional
        Arguments to parse. Default is ``sys.argv``.
    namespace : argparse.Namespace
        Namespace to write to. Default is a new namespace.

    Returns
    -------
    argparse.Namespace
        Namespace with parsed arguments / options.

    """

    colorstr_env = os.getenv('DDGR_COLORS')

    argparser = DdgArgumentParser(description='DuckDuckGo from the terminal.')
    addarg = argparser.add_argument
    addarg('-n', '--num', type=argparser.nonnegative_int, default=10, metavar='N',
           help='show N (0<=N<=25) results per page (default 10); N=0 shows actual number of results fetched per page')
    addarg('-r', '--reg', dest='region', default='us-en', metavar='REG',
           help="region-specific search e.g. 'us-en' for US (default); visit https://duckduckgo.com/params")
    addarg('--colorize', nargs='?', choices=['auto', 'always', 'never'],
           const='always', default='auto',
           help="""whether to colorize output; defaults to 'auto', which enables
           color when stdout is a tty device; using --colorize without an argument
           is equivalent to --colorize=always""")
    addarg('-C', '--nocolor', action='store_true', help='equivalent to --colorize=never')
    addarg('--colors', dest='colorstr', type=argparser.is_colorstr, default=colorstr_env if colorstr_env else 'oCdgxy', metavar='COLORS',
           help='set output colors (see man page for details)')
    addarg('-j', '--ducky', action='store_true', help='open the first result in a web browser; implies --np')
    addarg('-t', '--time', dest='duration', metavar='SPAN', default='', choices=('d', 'w', 'm', 'y'), help='time limit search '
           '[d (1 day), w (1 wk), m (1 month), y (1 year)]')
    addarg('-w', '--site', dest='sites', action='append', metavar='SITE', help='search sites using DuckDuckGo')
    addarg('-x', '--expand', action='store_true', help='Show complete url in search results')
    addarg('-p', '--proxy', metavar='URI', help='tunnel traffic through an HTTPS proxy; URI format: [http[s]://][user:pwd@]host[:port]')
    addarg('--unsafe', action='store_true', help='disable safe search')
    addarg('--noua', action='store_true', help='disable user agent')
    addarg('--json', action='store_true', help='output in JSON format; implies --np')
    addarg('--gb', '--gui-browser', dest='gui_browser', action='store_true', help='open a bang directly in gui browser')
    addarg('--np', '--noprompt', dest='noninteractive', action='store_true', help='perform search and exit, do not prompt')
    addarg('--url-handler', metavar='UTIL', help='custom script or cli utility to open results')
    addarg('--show-browser-logs', action='store_true', help='do not suppress browser output (stdout and stderr)')
    addarg('-v', '--version', action='version', version=_VERSION_)
    addarg('-d', '--debug', action='store_true', help='enable debugging')
    addarg('keywords', nargs='*', metavar='KEYWORD', help='search keywords')
    addarg('--complete', help=argparse.SUPPRESS)

    parsed = argparser.parse_args(args, namespace)
    if parsed.nocolor:
        parsed.colorize = 'never'

    return parsed


def main():
    opts = parse_args()

    # Set logging level
    if opts.debug:
        LOGGER.setLevel(logging.DEBUG)
        LOGDBG('ddgr version %s Python version %s', _VERSION_, python_version())

    # Handle query completer
    if opts.complete is not None:
        completer_run(opts.complete)

    check_stdout_encoding()

    # Add cmdline args to readline history
    if opts.keywords:
        try:
            readline.add_history(' '.join(opts.keywords))
        except Exception:
            pass

    # Set colors
    colorize = get_colorize(opts.colorize)

    colors = Colors(*[COLORMAP[c] for c in opts.colorstr], reset=COLORMAP['x']) if colorize else None
    Result.colors = colors
    Result.urlexpand = opts.expand
    DdgCmd.colors = colors

    # Try to enable ANSI color support in cmd or PowerShell on Windows 10
    if sys.platform == 'win32' and sys.stdout.isatty() and colorize:
        set_win_console_mode()

    if opts.url_handler is not None:
        open_url.url_handler = opts.url_handler
    else:
        open_url.override_text_browser = bool(opts.gui_browser)

        # Handle browser output suppression
        open_url.suppress_browser_output = not (opts.show_browser_logs or (os.getenv('BROWSER') in TEXT_BROWSERS))

    try:
        repl = DdgCmd(opts, '' if opts.noua else USER_AGENT)

        if opts.json or opts.ducky or opts.noninteractive:
            # Non-interactive mode
            if repl.keywords and (
                    repl.keywords[0][0] == '!' or
                    (len(repl.keywords[0]) > 1 and repl.keywords[0][1] == '!')
            ):
                # Handle bangs
                open_url(repl._ddg_url.full())
            else:
                repl.fetch(opts.json)
                if opts.ducky:
                    if repl.results:
                        open_url(repl.results[0].url)
                    else:
                        print('No results.', file=sys.stderr)
                else:
                    repl.display_results(prelude='', json_output=opts.json)

            sys.exit(0)

        # Interactive mode
        repl.cmdloop()
    except Exception as e:
        # If debugging mode is enabled, let the exception through for a traceback;
        # otherwise, only print the exception error message.
        if LOGGER.isEnabledFor(logging.DEBUG):
            raise

        LOGERR(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
