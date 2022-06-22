import os

from lib import utilities

TEST_DIRECTORIES = ['test', 'tests', 'spec']

TEST_DISCOVERERS = {
    'c': (
        'attributes.unit_test.discoverer.c',
        'CTestDiscoverer'
    ),
    'c++': (
        'attributes.unit_test.discoverer.cpp',
        'CppTestDiscoverer'
    ),
    'c#': (
        'attributes.unit_test.discoverer.csharp',
        'CSharpTestDiscoverer'
    ),
    'javascript': (
        'attributes.unit_test.discoverer.javascript',
        'JavaScriptTestDiscoverer'
    ),
    'java': (
        'attributes.unit_test.discoverer.java',
        'JavaTestDiscoverer'
    ),
    'objective-c': (
        'attributes.unit_test.discoverer.objectivec',
        'ObjectiveCTestDiscoverer'
    ),
    'python': (
        'attributes.unit_test.discoverer.python',
        'PythonTestDiscoverer'
    ),
    'php': (
        'attributes.unit_test.discoverer.php',
        'PhpTestDiscoverer'
    ),
    'ruby': (
        'attributes.unit_test.discoverer.ruby',
        'RubyTestDiscoverer'
    ),
    'swift': (
        'attributes.unit_test.discoverer.swift',
        'SwiftTestDiscoverer'
    )
}

TEST_DISCOVERER_CACHE = dict()


def _load_test_discoverer(module_, class_):
    mod = __import__(module_, None, None, ['__all__'])
    TEST_DISCOVERER_CACHE[class_] = getattr(mod, class_)()


def get_test_discoverer(language):
    """Return an instance of an appropriate test discover.

    Parameters
    ----------
    language : string
        The programming language for which a test discoverer is needed.

    Returns
    -------
    discoverer : *TestDiscoverer
        A reference to a test discoverer appropriate for the programming
        language.
    """
    _language = language.lower()
    if _language in TEST_DISCOVERERS:
        (module_, class_) = TEST_DISCOVERERS[_language]
        if class_ not in TEST_DISCOVERER_CACHE:
            _load_test_discoverer(module_, class_)
        return TEST_DISCOVERER_CACHE[class_]
    else:
        raise Exception('Test discoverer for {0} is not defined.'.format(language))


class TestDiscoverer(object):
    """Base class for all TestDiscoverer classes"""
    def __init__(self):
        self.frameworks = None
        self.languages = None
        self.extensions = None

    def discover(self, path):
        if not (self.frameworks and self.languages and self.extensions):
            raise Exception(
                '{0} is not appropriately configured.'.format(
                    self.__class__.__name__
                )
            )

        # SLOC of source code
        _sloc = utilities.get_loc(path)
        sloc = 0
        for language in self.languages:
            if language in _sloc:
                sloc += _sloc[language]['sloc']

        proportion = 0
        if sloc > 0:
            # Pass 1: Look for a unit testing frameworks
            for framework in self.frameworks:
                proportion += framework(path, sloc)

            # Pass 2: Look for files in conventional test directories
            # NOTE: Second pass is necessary only when the proportion of unit
            # tests from Pass 1 is less than 1%
            if proportion < 0.01:
                _path = None
                done = False
                for (root, dnames, _) in os.walk(path):
                    for item in TEST_DIRECTORIES:
                        if item in dnames:
                            _path = os.path.join(root, item)
                            done = True
                            break
                    if done:
                        break

                files = None
                if _path:
                    files = utilities.get_files(_path, self.language)
                    if files:
                        # SLOC of test code
                        print('path_init: ',path)
                        _slotc = utilities.get_loc(path, files=files)
                        slotc = 0
                        for language in self.languages:
                            if language in _slotc:
                                slotc += _slotc[language]['sloc']
                        proportion = max(proportion, slotc / sloc)

        return proportion

    def measure(self, path, sloc, pattern, whole=False):
        proportion = 0
        files = utilities.search(
            pattern, path, whole=whole, include=self.extensions
        )
        if files:
            # SLOC of test code
            _slotc = utilities.get_loc(path, files=files)
            slotc = 0
            for language in self.languages:
                if language in _slotc:
                    slotc += _slotc[language]['sloc']
            proportion = slotc / sloc

        return proportion
