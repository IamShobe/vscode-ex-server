"""Extension module."""
import uuid
from zipfile import ZipFile

from bs4 import BeautifulSoup
from cached_property import cached_property

def open_zip(func):
    def inner_function(self, *args, **kwargs):
        with ZipFile(self.filename) as zip_f:
            return func(self, zip_f, *args, **kwargs)

    return inner_function


MANIFEST = "Microsoft.VisualStudio.Code.Manifest"
DETAILS = "Microsoft.VisualStudio.Services.Content.Details"
LICENSE = "Microsoft.VisualStudio.Services.Content.License"
ICON = "Microsoft.VisualStudio.Services.Icons.Default"


class Extension:
    def __init__(self, filename):
        self.filename = filename
        self.indexed_by = []

    @property
    def name(self):
        return self.identity["id"]

    @property
    def version(self):
        return self.identity["version"]

    @property
    def publisher(self):
        return self.identity["publisher"]

    @property
    def identity(self):
        return self.xml_tree.find("metadata").find("identity")

    @property
    def display_name(self):
        return self.xml_tree.find("metadata").find("displayname").text

    @property
    def description(self):
        return self.xml_tree.find("metadata").find("description").text

    @property
    def properties(self):
        return {
            elem["id"]: elem["value"]
            for elem in self.xml_tree.find("properties").find_all("property")
        }

    @cached_property
    def xml_tree(self):
        return BeautifulSoup(self.manifest, "lxml")

    @property
    def icon_path(self):
        return self.xml_tree.find("metadata").find("icon").text

    @property
    def tags(self):
        return self.xml_tree.find("metadata").find("tags").text.split(",")

    @property
    def categories(self):
        return self.xml_tree.find("metadata").find("categories").text\
            .split(",")


    @property
    def assets(self):
        return {
            elem["type"]: elem["path"]
            for elem in self.xml_tree.find("assets").find_all("asset")
        }

    @cached_property
    @open_zip
    def icon(self, zip_file):
        with zip_file.open(self.icon_path) as icon_file:
            return icon_file.read()

    @open_zip
    def read_file(self, zip_file, file_path):
        with zip_file.open(file_path) as f:
            return f.read()

    @cached_property
    @open_zip
    def manifest(self, zip_file):
        with zip_file.open("extension.vsixmanifest") as f:
            manifest = f.read()

        return manifest

    @cached_property
    @open_zip
    def license(self, zip_file):
        with zip_file.open(self.assets[LICENSE]) as f:
            zip_license = f.read()

        return zip_license

    @cached_property
    @open_zip
    def details(self, zip_file):
        with zip_file.open(self.assets[DETAILS]) as f:
            details = f.read()

        return details

    @cached_property
    @open_zip
    def code_manifest(self, zip_file):
        with zip_file.open(self.assets[MANIFEST]) as f:
            manifest = f.read()

        return manifest

    def __hash__(self):
        return hash(uuid.uuid3(uuid.NAMESPACE_OID, str(self.filename)))

    def __eq__(self, other):
        return hash(self) == hash(other)

