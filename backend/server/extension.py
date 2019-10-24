"""Extension module."""
import uuid
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime

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

    @property
    def stats(self):
        return Path(self.filename).stat()

    @property
    def created_time(self):
        return datetime.fromtimestamp(self.stats.st_ctime).isoformat(timespec='milliseconds') + "Z"

    @property
    def modified_time(self):
        return datetime.fromtimestamp(self.stats.st_mtime).isoformat(timespec='milliseconds') + "Z"

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
        return BeautifulSoup(self.manifest, "html.parser")

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

    @cached_property 
    def base_url(self):
        return f"https://marketplace.visualstudio.com/extensions" \
               f"/{self.publisher}/{self.name}/{self.version}"

    @cached_property
    def download_url(self):
        return f"https://marketplace.visualstudio.com/serve{self.filename}"

    @property
    def query_data(self):
        properties = []
        for key, value in self.properties.items():
            properties.append({
                "key": key,
                "value": value
            })

        return {
            "version": self.version,
            "flags": "validated",
            "lastUpdated": self.modified_time,
            "files": [
                {
                    "assetType": "Microsoft.VisualStudio.Code.Manifest",
                    "source": f"{self.base_url}/Microsoft.VisualStudio.Code.Manifest"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.Content.Details",
                    "source": f"{self.base_url}/Microsoft.VisualStudio.Services.Content.Details"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.Content.License",
                    "source": f"{self.base_url}/Microsoft.VisualStudio.Services.Content.License"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.Icons.Default",
                    "source":
                        f"{self.base_url}/Microsoft.VisualStudio.Services.Icons.Default"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.Icons.Small",
                    "source": f"{self.base_url}/Microsoft.VisualStudio.Services.Icons.Small"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.VsixManifest",
                    "source": f"{self.base_url}/Microsoft.VisualStudio.Services.VsixManifest"
                },
                {
                    "assetType": "Microsoft.VisualStudio.Services.VSIXPackage",
                    "source": self.download_url
                }
            ],
            "properties": properties,
            "assetUri": self.base_url,
            "fallbackAssetUri": self.base_url
            }