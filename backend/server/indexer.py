import os
import re
from pathlib import Path
from logging import getLogger
from contextlib import contextmanager

from extension import Extension

LEGAL_CHARS = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789' \
              '.*,-+!@$%^&_ '



LOGGER = getLogger("app")


@contextmanager
def ignore_failed_index():
    try:
        yield
    
    except RuntimeError as e:
        LOGGER.warning(str(e))

class Trie:
    def __init__(self):
        self.next = {}
        self.values = set()

    def _add(self, element, string, original_string):
        self.values.add(element)
        if len(string) == 0:
            return

        current_char = string[0]
        if current_char not in self.next:
            if current_char not in LEGAL_CHARS:
                raise RuntimeError(f"Illegal char to add: '{current_char}' in "
                                   f"'{original_string}'")
            self.next[current_char] = Trie()

        self.next[current_char]._add(element, string[1:], original_string)

    def add(self, element, string):
        LOGGER.debug(f"'{string}'")

        self._add(element, string, string)

    def _remove(self, element, string, original_string):
        if element in self.values:
            self.values.remove(element)

        if len(string) == 0:
            return

        current_char = string[0]
        if current_char not in self.next:
            return

        self.next[current_char]._remove(element, string[1:], original_string)
        if len(self.next[current_char].values) == 0:
            del self.next[current_char]

    def remove(self, element, string):
        self._remove(element, string, string)

    def remove_words(self, element, word_list):
        for word in word_list:
            self.remove(element, word_list)

    def add_words(self, element, word_list):
        successes = []
        for word in word_list:
            with ignore_failed_index():
                self.add(element, word)
                successes.append(word)

        return successes

    def _get(self, string, original_string):
        if len(string) == 0:
            return self.values

        current_char = string[0]
        if current_char not in self.next:
            raise RuntimeError(f"String '{original_string}' not in trie!")

        return self.next[current_char]._get(string[1:], original_string)

    def get(self, string):
        return self._get(string, string)


class Indexer:
    def __init__(self, start_dir):
        self.start_dir = start_dir
        self.trie = Trie()
        self.extensions = {}
        self.extensions_set = set()

    def reset(self):
        self.trie = Trie()
        self.extensions = {}
        self.index_packages()
        self.extensions_set = set()

    def index_package_in_paths(self, extension):
        self.extensions_set.add(extension)
        if extension.publisher not in self.extensions:
            self.extensions[extension.publisher] = {}

        if extension.name not in self.extensions[extension.publisher]:
            self.extensions[extension.publisher][extension.name] = {}

        self.extensions[extension.publisher][extension.name][
            extension.version] = extension

    def index_package(self, extension):
        print(f"Indexing {extension.filename}....", flush=True)
        LOGGER.debug("Keywords: ")
        self.trie.add(extension, extension.name)
        self.index_package_in_paths(extension)

        index_list = []
        for sub_name in re.split(r"[ \-,_]", extension.name):
            if len(sub_name) > 0:
                index_list.append(sub_name)

        index_list.append(extension.publisher)
        for tag in extension.tags:
            index_list.append(tag)

        index_list.append(extension.display_name)
        index_list.append(extension.description)
        for sub_name in re.split(r"[ \-,_]", extension.description):
            if len(sub_name) > 0:
                index_list.append(sub_name)

        successes = self.trie.add_words(extension, index_list)
        successes.append(extension.name)
        extension.indexed_by = successes

    def remove_package(self, package):
        print(f"Deleting package {package.filename}", flush=True)
        self.trie.remove_words(package, package.indexed_by)
        package.indexed_by = []

    def index_packages(self):
        extensions = [
            Extension(str(Path(self.start_dir) / package))
            for package in os.listdir(self.start_dir)
        ]

        for extension in extensions:
            try:
                self.index_package(extension)
            except Exception as e:
                LOGGER.warning(
                    f"Failed to index {extension.filename}: {e}")

    def get_extension(self, publisher, name, version):
        return self.extensions[publisher][name][version]
