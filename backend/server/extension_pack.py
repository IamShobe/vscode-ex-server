import uuid
from distutils.version import LooseVersion

class ExtensionPack:
    def __init__(self, publisher, name):
        self.publisher = publisher
        self.name = name

        self.packages = {}
        self.filename_to_version = {}
        self.indexed_by = set()

    def __len__(self):
        return len(self.packages)

    def __hash__(self):
        return hash((self.publisher, self.name))

    def __getitem__(self, item):
        return self.packages[item]

    def add_package(self, package):
        self.packages[package.version] = package
        self.filename_to_version[package.filename] = package.version

    def remove_package(self, package):
        version = self.filename_to_version[package.filename]
        del self.filename_to_version[package.filename]
        del self.packages[version]

    def category(self):
        return self.latest_package.categories

    @property
    def latest_package(self):
        sorted_versions = sorted(list(self.packages.keys()), key=LooseVersion)
        return self.packages[sorted_versions[-1]]

    @property
    def sorted_packages(self):
        return sorted(list(self.packages.values()),
                      key=lambda package: LooseVersion(package.version), reverse=True)

    def query_data(self):
        return {
            "publisher": {
                "publisherId": uuid.uuid3(
                    uuid.NAMESPACE_OID, self.publisher
                ),
                "publisherName": self.publisher,
                "displayName": self.publisher,
                "flags": "none"
            },
            "extensionId": uuid.uuid3(uuid.NAMESPACE_OID, self.name),
            "extensionName": self.name,
            "displayName": self.latest_package.display_name,
            "flags": "validated, public",
            "lastUpdated": self.latest_package.modified_time,
            "publishedDate": self.latest_package.created_time,
            "releaseDate": self.latest_package.created_time,
            "shortDescription": self.latest_package.description,
            "versions": [package.query_data() for package in self.sorted_packages],
            "statistics": [
                {
                    "statisticName": "install",
                    "value": 0
                },
                {
                    "statisticName": "averagerating",
                    "value": 0
                },
                {
                    "statisticName": "ratingcount",
                    "value": 0
                },
                {
                    "statisticName": "trendingdaily",
                    "value": 0
                },
                {
                    "statisticName": "trendingmonthly",
                    "value": 0
                },
                {
                    "statisticName": "trendingweekly",
                    "value": 0
                },
                {
                    "statisticName": "updateCount",
                    "value": 0
                },
                {
                    "statisticName": "weightedRating",
                    "value": 0
                }
            ],
            "deploymentType": 0
        }
