import os
import re
from pathlib import Path
from logging import getLogger

from extension import Extension

LEGAL_CHARS = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789' \
              '.*,-+!@$%^&_ '


LOGGER = getLogger("app")

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
                raise RuntimeError(f"Illegal char to add: {current_char} in "
                                   f"{original_string}")
            self.next[current_char] = Trie()

        self.next[current_char]._add(element, string[1:], original_string)

    def add(self, element, string):
        LOGGER.debug(f"'{string}'")

        self._add(element, string, string)

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

    def reset(self):
        self.trie = Trie()
        self.extensions = {}
        self.index_packages()

    def index_package(self, extension):
        LOGGER.info(f"Indexing {extension.name}....")
        LOGGER.debug("Keywords: ")
        self.trie.add(extension, extension.name)
        for sub_name in re.split(r"[ \-,_]", extension.name):
            if len(sub_name) > 0:
                self.trie.add(extension, sub_name)

        self.trie.add(extension, extension.publisher)
        for tag in extension.tags:
            self.trie.add(extension, tag)

        self.trie.add(extension, extension.display_name)
        self.trie.add(extension, extension.description)
        for sub_name in re.split(r"[ \-,_]", extension.description):
            if len(sub_name) > 0:
                self.trie.add(extension, sub_name)

        if extension.publisher not in self.extensions:
            self.extensions[extension.publisher] = {}

        if extension.name not in self.extensions[extension.publisher]:
            self.extensions[extension.publisher][extension.name] = {}

        self.extensions[extension.publisher][extension.name][
            extension.version] = extension

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
