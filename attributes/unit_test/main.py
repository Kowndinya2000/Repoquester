import sys
import os
from attributes.unit_test.discoverer import get_test_discoverer

def run(project_id, repo_path, cursor, **options):
    print("----- METRIC: UNIT TEST -----")
    fp = open('l'+str(project_id),'r')
    for x in fp:
        lang = x.replace("\n","")
        break
    repo_path_abs = str(os.getcwd()) + "/" +repo_path
    discoverer = get_test_discoverer(language=lang)
    proportion = discoverer.discover(repo_path_abs)
    threshold = options['threshold']
    print('proportion: ',proportion)
    return (proportion >= threshold), proportion

if __name__ == '__main__':
    print('Attribute plugins are not meant to be executed directly.')
    sys.exit(1)
