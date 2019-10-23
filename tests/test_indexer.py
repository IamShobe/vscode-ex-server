import pytest

from backend.server.indexer import Indexer
from stub.extension import MockedExtension


@pytest.fixture
def indexer():
    indexer = Indexer("ext")
    return indexer


def test_index_package(indexer):
    ext1 = MockedExtension()

    indexer.index_package(ext1)

    assert len(indexer.extension_packs) == 1
    extension_pack = list(indexer.extension_packs)[0]

    assert indexer.extensions[ext1.publisher][ext1.name] == extension_pack
    assert extension_pack.latest_package == ext1
    assert extension_pack.latest_package.version == ext1.version
    assert extension_pack.name == ext1.name
    assert extension_pack.publisher == ext1.publisher
    assert len(extension_pack.indexed_by) > 0

    assert indexer.search(ext1.name) == {extension_pack}


def test_different_file_name_same_extension(indexer):
    ext1 = MockedExtension()
    ext1.filename = "one_file.vsix"
    ext2 = MockedExtension()
    ext2.filename = "other_file.vsix"

    indexer.index_package(ext1)
    indexer.index_package(ext2)

    assert len(indexer.extension_packs) == 1
    extension_pack = list(indexer.extension_packs)[0]
    assert len(extension_pack.packages) == 1


def test_same_package_2_versions(indexer):
    ext1 = MockedExtension()
    ext1.filename = "one_file.vsix"
    ext1.version = "0.2.0"
    ext2 = MockedExtension()
    ext2.filename = "other_file.vsix"
    ext2.version = "3.1.0"

    indexer.index_package(ext1)
    indexer.index_package(ext2)

    assert len(indexer.extension_packs) == 1
    extension_pack = list(indexer.extension_packs)[0]

    assert extension_pack.latest_package == ext2
    assert len(extension_pack.packages) == 2


def test_same_publisher_2_packages(indexer):
    ext1 = MockedExtension()
    ext1.filename = "one_file.vsix"
    ext1.name = "package1"
    ext1.publisher = "elran"
    ext2 = MockedExtension()
    ext2.filename = "other_file.vsix"
    ext2.name = "package2"
    ext2.publisher = "elran"

    indexer.index_package(ext1)
    indexer.index_package(ext2)

    assert len(indexer.extension_packs) == 2
    assert len(indexer.extensions["elran"]) == 2


def test_search_2_packages(indexer):
    ext1 = MockedExtension()
    ext1.filename = "one_file.vsix"
    ext1.name = "package1"
    ext1.publisher = "elran"
    ext2 = MockedExtension()
    ext2.filename = "other_file.vsix"
    ext2.name = "package2"
    ext2.publisher = "elran"

    indexer.index_package(ext1)
    indexer.index_package(ext2)

    assert indexer.search("package") == indexer.extension_packs


def test_different_publishers(indexer):
    ext1 = MockedExtension()
    ext1.filename = "one_file.vsix"
    ext1.name = "package1"
    ext1.publisher = "elran"
    ext2 = MockedExtension()
    ext2.filename = "other_file.vsix"
    ext2.name = "package2"
    ext2.publisher = "david"

    indexer.index_package(ext1)
    indexer.index_package(ext2)

    assert len(indexer.extension_packs) == 2
    assert len(indexer.extensions["elran"]) == 1
    assert len(indexer.extensions["david"]) == 1
