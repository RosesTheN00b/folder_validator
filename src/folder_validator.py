import os
import json
import re
from pathlib import Path

PATHS = [os.getcwd() + '/../examples']


class Counter:
    count = 0


class Result:
    def __init__(self, is_ok, item, matched_rule=None):
        self.is_ok = is_ok
        self.item = item
        self.matched_rule = matched_rule


class Description:
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath


def _get_type(item):
    if item.is_dir():
        return 'folder'
    return 'file'


def _append_description_name(current_description, current_rule, item):
    if 'description' in current_rule:
        return current_description.name + ' --> ' + current_rule['description'] + '(' + str(item) + ')'
    return current_description.name + ' --> ' + current_rule['name'] + '(' + str(item) + ')'


def _append_description(current_description, current_rule, item):
    return Description(
        _append_description_name(current_description, current_rule, item),
        current_description.filepath)


def _compare_folder(name, item, rule, description):
    if re.search(name, item.name):
        if 'items' not in rule:
            return True
        _check_folder(str(item), rule, _append_description(description, rule, item))
        # Swap comments if the higher-level rule should also break due to lower-level rule breaks.
        #return _check_folder(str(item), rule, _append_description(description, rule, item))
        return True
    return False


def _match(rule, item, description):
    if rule['type'] == 'exclusion':
        return re.search(rule['name'], str(item.absolute()))

    if rule['type'] != _get_type(item):
        return False

    if 'pattern' not in rule:
        return _compare_folder(rule['name'], item, rule, description)
    #print('\n\n\n', item)
    for range_item in range(rule['range_min'], rule['range_max'] + 1):
        #print('checking', range_item, rule, item)
        name = rule['name'].format(number=range_item)
        result = _compare_folder(name, item, rule, description)
        if result:
            #print('match!')
            return True
        #print("unmatched")
    return False


def _match_folder(item, ruleset, description):
    for rule in ruleset:
        if _match(rule, item, description):
            return Result(True, item, rule)
    return Result(False, item)


def _is_required(rule):
    return 'required' in rule and rule['required']

def _rule_description(rule):
    if "pattern" in rule and rule['pattern'] == "multible":
        return rule['type'] + ': ' + rule['name'] + '(range ' + str(rule['range_min']) + '-' + str(rule['range_max']) + ')'
    return rule['type'] + ': ' + rule['name']

def _check_folder(folder, data, description):
    result = True
    current_ruleset = data['items']

    unexpected_files = []
    expected_files = []

    for rule in current_ruleset:
        if _is_required(rule):
            expected_files.append(rule)

    for item in Path(folder).iterdir():
        if str(item).endswith('folder_format'):
            continue

        result = _match_folder(item, current_ruleset, description)

        if not result.is_ok:
            unexpected_files.append(result)
            result = False
        else:
            if _is_required(result.matched_rule):
                if result.matched_rule in expected_files:
                    expected_files.remove(result.matched_rule)

    if unexpected_files != [] or expected_files != []:
        Counter.count += 1
        print('')
        print(str(Counter.count) + ': Violation found on', description.name)
        print('    -> Format file:', description.filepath)
        if unexpected_files != []:
            print('')
            print('  following items were unexpected:')
            for unexpected_file in unexpected_files:
                print('    *', unexpected_file.item)
            print('  because they did not match any of these rules:')
            for rule in data['items']:
                print('    ->', _rule_description(rule))
            print('')

        if expected_files != []:
            print('')
            print('  following items were expected, but could not be found:')
            for expected_file in expected_files:
                print('    *', expected_file['name'])
        print('')
    return result


def _check(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename == '.folder_format':
                format_file_path = dirpath + '/' + '.folder_format'
                json_ruleset = json.load(open(format_file_path))

                print('Checking', json_ruleset['description'], '...')
                _check_folder(dirpath, json_ruleset, Description(json_ruleset['description'], format_file_path))


for path in PATHS:
    _check(path)
