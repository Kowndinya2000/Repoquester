from tokens import *

import distutils.spawn
import importlib
import multiprocessing
import os
import shutil
import sys
import types
import traceback
from datetime import datetime
from time import strptime
from datetime import datetime
import attributes
import requests
from lib import utilities
# def getLastCommitDate(project_id):
#     fp = open('u'+str(project_id),'r')
#     for x in fp:
#         url = x.replace("\n","").replace("api.","").replace("/repos","")
#         break
#     url = url + "/commits"
#     try:
#         page = requests.get(url,auth=(auth_name,e)).json()[0]["commit"]["committer"]["date"].split("T")[0]
#     except:
#         page = requests.get(url).json()[0]["commit"]["committer"]["date"].split("T")[0]
#     return page
class Attribute(object):
    def __init__(self, attribute, **goptions):
        self.name = attribute.get('name', '')
        self.initial = attribute.get('initial', '').lower()
        self.weight = attribute.get('weight', 0.0)
        self.enabled = attribute.get('enabled', True)
        self.requires_source = attribute.get('requires_source', False)
        self.essential = attribute.get('essential', False)
        self.persist = attribute.get('persist', True)
        self.dependencies = attribute.get('dependencies', list())
        self.options = goptions
        self.options.update(attribute.get('options', dict()))
        self.reference = importlib.import_module('{0}.main'.format(self.name))

    def run(self, project_id, repository_path, cursor, outq):
        result = self.reference.run(
            project_id, repository_path, cursor, **self.options
        )
        outq.put(result)

    @property
    def timeout(self):
        return self.options.get('timeout', None)

    def __getstate__(self):
        state = self.__dict__.copy()
        if isinstance(self.reference, types.ModuleType):
            state['reference'] = self.reference.__name__
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if isinstance(self.reference, str):
            self.reference = importlib.import_module(
                '{0}.main'.format(self.name)
            )


class Attributes(object):
    def __init__(
        self, attributes, database, cleanup=False, keystring=None, **goptions
    ):
        self.attributes = None
        self.database = database
        self.today = goptions.get('today', str(datetime.today().date()))
        self.cleanup = cleanup

        self._parse_attributes(attributes, **goptions)
        self._parse_keystring(keystring)

    def global_init(self, samples):
        try:
            if not self._validate_dependencies():
                raise Exception(
                    'Missing dependencies must be installed to continue.'
                )

            self.database.connect()
            for attribute in self.attributes:
                if hasattr(attribute.reference, 'global_init'):
                    with self.database.cursor() as cursor:
                        attribute.reference.global_init(cursor, samples)
        finally:
            self.database.disconnect()

    def run(self, project_id, repository_root):
        rresults = dict()
        repository_home = os.path.join(repository_root, str(project_id))
        outq = multiprocessing.Queue(maxsize=1)

        try:
            self.database.connect()

            repository_path = None
            if self.requires_source:
                repository_path = self._init_repository(
                    project_id, repository_home
                )

            for attribute in self.attributes:
                bresult = False
                rresult = None

                if not attribute.enabled:
                    continue

                with self.database.cursor() as cursor:
                    if hasattr(attribute.reference, 'init'):
                        attribute.reference.init(cursor)

                with self.database.cursor() as cursor:
                    timeout = utilities.parse_datetime_delta(attribute.timeout)

                    process = multiprocessing.Process(
                        target=attribute.run,
                        args=(project_id, repository_path, cursor, outq)
                    )
                    process.start()
                    process.join(timeout=timeout.total_seconds())

                    if not outq.empty():
                        (bresult, rresult) = outq.get()
                    else:
                        sys.stderr.write(
                            (
                                ' \033[91mWARNING\033[0m [{0:10d}] '
                                '{1} timed out\n'
                            ).format(project_id, attribute.name)
                        )
                        if process.is_alive():
                            process.terminate()

                rresults[attribute.name] = rresult
        except:
            sys.stderr.write('Exception\n\n')
            sys.stderr.write('  Project ID   {0}\n'.format(project_id))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
        finally:
            self.database.disconnect()
            if self.cleanup:
                self._cleanup(repository_home)
            return rresults

    def get(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute

    def score(self, rresults):
        score = 0
        for (attribute, rresult) in rresults.items():
            attribute = self.get(attribute)
            bresult = False
            if type(rresult) is not str and rresult is not None:
                if 'threshold' in attribute.options:
                    bresult = (rresult >= attribute.options['threshold'])
                else:
                    bresult = bool(rresult)
            # If an *essential* attribute is missing a ZERO score is assigned
            if attribute.essential and bresult is False:
                print('attr with false output: ',attribute.name)
                score = 0
                break

            score += bresult * attribute.weight

        return score

    @property
    def is_persistence_enabled(self):
        for attribute in self.attributes:
            if attribute.persist:
                return True
        return False

    @property
    def requires_source(self):
        for attribute in self.attributes:
            if attribute.enabled and attribute.requires_source:
                return True
        return False

    def _cleanup(self, repository_home):
        shutil.rmtree(repository_home, ignore_errors=True)

    def _init_repository(self, project_id, repository_home):
        repository_path = repository_home  # Default

        if not os.path.exists(repository_path):
            os.mkdir(repository_path)

        items = os.listdir(repository_path)
        if items:
            for item in os.listdir(repository_path):
                itempath = os.path.join(repository_path, item)
                if os.path.isdir(itempath):
                    repository_path = itempath
                    break
        else:
            fp = open('u'+str(project_id),'r')
            for x in fp:
                url = x.replace("\n","").replace("https://api.github.com/repos/","").split("/")
                break
            fp.close()
            (repo_owner, repo_name) = (url[0],url[1])
            if not (repo_owner or repo_name):
                raise ValueError('Invalid project ID {0}.'.format(project_id))
            
            last_commit_date = getLastCommitDate(project_id)
            if last_commit_date is None:
                last_commit_date = self.today

            repository_path = utilities.clone(
                repo_owner, repo_name, repository_path, last_commit_date
            )

        return repository_path

    def _parse_attributes(self, attributes, **goptions):
        if attributes:
            self.attributes = list()
            for attribute in attributes:
                self.attributes.append(Attribute(attribute, **goptions))

    def _disable_attributes(self):
        for attribute in self.attributes:
            attribute.enabled = False

    def _disable_persistence(self):
        for attribute in self.attributes:
            attribute.persist = False

    def _parse_keystring(self, keystring):
        if keystring:
            # Clean the slate
            self._disable_attributes()
            self._disable_persistence()

            for key in keystring:
                attribute = next(
                    attribute
                    for attribute in self.attributes
                    if attribute.initial == key.lower()
                )
                attribute.enabled = True
                attribute.persist = key.isupper()

    def _validate_dependencies(self):
        valid = True
        for attribute in self.attributes:
            if attribute.enabled and attribute.dependencies:
                for dependency in attribute.dependencies:
                    if not distutils.spawn.find_executable(dependency):
                        sys.stderr.write(
                            '[{0}] Dependency {1} missing\n'.format(
                                attribute.name, dependency
                            )
                        )
                        valid = False
        return valid

