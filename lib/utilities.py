import argparse
import io
import json
import os
import shlex
import subprocess
import urllib.request
import re
import tarfile
from tempfile import NamedTemporaryFile
import requests
from lib import dateutil

# GitHub OAuth token issuer
TOKENIZER = None

# Map GHTorrent's projects.language to ACK compatible language (if necessary).
ACK_LANGUAGE_MAP = {
    'c': 'cc',
    'c++': 'cpp',
    'c#': 'csharp',
    'objective-c': 'objc',
    'ojective-c++': 'objcpp',
}

_loc_cache = dict()
_cache_hits = 0


def get_cache_hits():
    return _cache_hits


def get_loc(path, files=None):
    """Return the lines-of-code for each language.

    cloc (http://cloc.sourceforge.net/) is used to compute the metrics. The
    method merely parses the output from cloc to return a Python-friendly
    data structure.

    Parameters
    ----------
    path : string
        An absolute path to the source code.
    files : list, optional
        The relative path of file(s) that must used when counting the
        lines-of-code.

    Returns
    -------
    sloc : dictionary
        Dictionary keyed by language with a dictionary containing the metrics
        as the value. The metric dictionary is keyed by 'cloc' for
        comment-lines-of-code and 'sloc' for source-lines-of-code.
    """
    global _loc_cache
    global _cache_hits

    if files is None and path in _loc_cache.keys():
        _cache_hits += 1
        cached = _loc_cache[path]
        if isinstance(cached, Exception):
            raise cached
        else:
            return cached

    if not (os.path.exists(path) or os.path.isdir(path)):
        exception = Exception('%s is an invalid path.' % path)
        if files is None:
            _loc_cache[path] = exception
        raise exception

    sloc = dict()

    tempfile = None
    try:
        command = 'cloc --csv '

        if files:
            tempfile = NamedTemporaryFile()
            tempfile_fi = tempfile.name
            tempfile_fi = tempfile_fi.replace('C:','E:')
            with open(tempfile_fi, 'w') as _tempfile:
                for _file in files:
                    _tempfile.write('{0}\n'.format(_file))
            fp = open('tmp_files.sh','a')
            fp.write("rm "+tempfile_fi+"\n")
            fp.close()
            command += '--list-file={0}'.format(tempfile_fi)
        else:
            command += '.'

        if 'DEBUG' in os.environ:
            print(command)

        process = subprocess.Popen(
            command, cwd=path, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        (out, err) = [x.decode() for x in process.communicate()]

        lines = [
            line for line in out.split('\n') if len(line.strip('\n')) != 0
        ]

        index = -1
        for _index, _line in enumerate(lines):
            if 'files,' in _line:
                index = _index
                break

        if index != -1:
            for _index in range(index + 1, len(lines)):
                components = lines[_index].split(',')
                sloc[components[1]] = {
                    'cloc': int(components[3]),
                    'sloc': int(components[4])
                }

        if files is None:
            _loc_cache[path] = sloc
    except:
        raise
    finally:
        if tempfile is not None and not tempfile.closed:
            tempfile.close()

    return sloc


def search(
    pattern, path, recursive=True, whole=False, ignorecase=False, include=None,
    exclude=None
):
    """Search for the presence of a pattern.

    grep (http://www.gnu.org/software/grep/manual/grep.html) is used to
    recursively search for the pattern in all files within a specified path.

    Parameters
    ----------
    pattern : string
        A non-empty PERL style regular expression to match.
    path : string
        An absolute path to the location to root the search at.
    recursive : bool, optional
        Indicates if the search should be recursively across the entire
        directory tree rooted at path. Default is True.
    whole : bool, optional
        Indicates if the search should use whole word matching. Default is
        False.
    ignorecase : bool, optional
        Indicates if the serach should be insensitive to case.
    include : list, optional
        A list of patterns that specify the files to include in the search.
        Default is None.
    exclude : list, optional
        A list of patterns that specify the files to exclude in the search.
        Default is None.

    Returns
    -------
    files : list
        A list of relative paths to files that contain the matching string. If
        no files were found containing the matching string then None is
        returned.
    """
    if not (os.path.exists(path) or os.path.isdir(path)):
        raise Exception('%s is an invalid path.' % path)

    if not pattern:
        raise Exception('Parameter pattern cannot be emtpy.')

    files = None

    command = 'grep -Plc'
    if recursive:
        command += ' -r'
    if whole:
        command += ' -w'
    if ignorecase:
        command += ' -i'
    if include:
        command += ' --include '
        command += ' --include '.join(shlex.quote(i) for i in include)
    if exclude:
        command += ' --exclude '
        command += ' --exclude '.join(shlex.quote(i) for i in exclude)

    command += ' '
    command += shlex.quote(pattern)

    if 'DEBUG' in os.environ:
        print(command)

    process = subprocess.Popen(
        command, cwd=path, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (out, err) = [x.decode() for x in process.communicate()]

    lines = [
        line.strip('\n')
        for line in out.split('\n') if len(line.strip('\n')) != 0
    ]

    if lines:
        files = lines

    return files


def url_to_json(url, headers={},authentication=[]):
    """Returns the JSON response from the url.

    Args:
        url (string): URL from which to GET the JSON resource.

    Returns:
        dict: JSON of the response or empty dict on error.
    """
    if(len(authentication) == 2):
        result = requests.get(url,auth=(authentication[0],authentication[1]),headers=headers).json()
    elif(len(authentication) == 0):
        result = requests.get(url,headers=headers).json()
    return result



def clone(owner, name, directory, date=None):
    """Clone a GitHub repository and reset its state to a specific commit.

    Parameters
    ----------
    owner : string
        User name of the owner of the repository.
    name : string
        Name of the repository to clone.
    date : string
        A date used to identify the commit to which the state of the repository
        will be reset to.
    directory : string
        Absolute path of a directory to clone the repository to.

    Returns
    -------
    path : string
        Absolute path of the directory containing the repository just cloned.
    """
    (cloneable, reason) = is_cloneable(owner, name)
    if not cloneable:
        raise Exception(reason)

    path = directory
    url = 'https://github.com/{0}/{1}'.format(owner, name)
    print('<<<<<<<< url: ', url)
    # Clone
    command = 'git clone {0}'.format(url)
    if 'DEBUG' in os.environ:
        print(command)

    process = subprocess.Popen(
        command, cwd=path, shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    process.wait()
    if process.returncode != 0:
        raise Exception('Failed to execute {0}'.format(command))

    if date is not None:
        # Reset
        path = os.path.join(path, name)
        command = (
            'git log -1 --before="{0} 23:59:59" --pretty="format:%H"'.format(
                date
            )
        )
        if 'DEBUG' in os.environ:
            print(command)

        process = subprocess.Popen(
            command, cwd=path, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        (out, err) = [i.decode() for i in process.communicate()]

        if process.returncode != 0:
            raise Exception('Failed to execute {0}'.format(command))

        sha = out
        command = 'git reset --hard {0}'.format(sha)
        if 'DEBUG' in os.environ:
            print(command)

        process = subprocess.Popen(
            command, cwd=path, shell=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        process.wait()
        if process.returncode != 0:
            raise Exception('Failed to execute {0}'.format(command))

    return path


def read(jsonfile):
    """Read a JSON file.

    Parameters
    ----------
    jsonfile : file object
        An open file handle to a JSON file.

    Return
    ------
    jsondata : dict
        A dictionary returned by the json.load()
    """
    jsondata = dict()
    try:
        if jsonfile:
            jsondata = json.load(jsonfile)
        return jsondata
    except:
        raise Exception('Failure in loading JSON data {0}'.format(
            jsonfile.name
        ))
    finally:
        jsonfile.close()


def parse_datetime_delta(datetime_delta):
    """Parse specification of datetime delta of the form nynmndnHnMnS

    Parameters
    ----------
    datetime_delta : str
        A string of the form nynmndnHnMnS. All components of the
        specification are optional. Note that the component specifiers are
        case-sensitive.

    Returns
    -------
    relativedelta : lib.dateutil.relativedelta
        An instance of lib.dateutil.relativedelta representing the datetime
        delta specified in the argument to this function. A value of zero is
        set for each component that is not specfied in the argument.
    """
    delta = dateutil.relativedelta()

    match = re.search('(\d+)y', datetime_delta)
    if match:
        delta.years = int(match.group(1))

    match = re.search('(\d+)m', datetime_delta)
    if match:
        delta.months = int(match.group(1))

    match = re.search('(\d+)d', datetime_delta)
    if match:
        delta.days = int(match.group(1))

    match = re.search('(\d+)H', datetime_delta)
    if match:
        delta.hours = int(match.group(1))

    match = re.search('(\d+)M', datetime_delta)
    if match:
        delta.minutes = int(match.group(1))

    match = re.search('(\d+)S', datetime_delta)
    if match:
        delta.seconds = int(match.group(1))

    return delta


def is_cloneable(owner, name):
    """Verify if a repository is clone-able.

    Parameters
    ----------
    owner : string
        User name of the owner of the repository.
    name : string
        Name of the repository to clone.

    Returns
    -------
    cloneablility : 2-tuple
        A 2-tuple indicating the cloneablility of the repository. First element
        is True if the repository is clone-able, False otherwise. Second
        element is a string that describes the reason for a repository for not
        being clone-able.
    """
    is_cloneable = True
    reason = None

    uri = '{0}/{1}'.format(owner, name)
    url = 'https://api.github.com/repos/{0}'.format(uri)
    if TOKENIZER is not None:
        url = TOKENIZER.tokenize(url)
    request = urllib.request.Request(url, method='HEAD')

    try:
        urllib.request.urlopen(request)
    except urllib.error.HTTPError as error:
        is_cloneable = False
        if error.code == 404:
            reason = '{0} is no longer active.'.format(uri)
        elif error.code == 403:
            reason = '{0} may have been deactivated.'.format(uri)
        else:
            reason = '{0} is not clone-able for reasons unknown.'.format(uri)

    return (is_cloneable, reason)


def get_files(path, language):
    """Return list of absolute paths to files in a specified language.

    Parameters
    ----------
    path : str
        Absolute path of the directory to search for files in.
    language : str
        Programming language as stored in GHTorrent's database.

    Returns
    -------
    files : list
        A list of absolute paths to files in a specified programming language
        (if any), None otherwise.
    """
    files = None

    language = language.lower()
    if language in ACK_LANGUAGE_MAP:
        language = ACK_LANGUAGE_MAP[language]

    command = ['ack', '-f', "--{0}".format(language), path]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if 'DEBUG' in os.environ:
        print(' '.join(command))

    out, _ = [x.decode(errors='ignore') for x in process.communicate()]
    files = [line for line in out.split('\n') if line.strip()]

    return files


