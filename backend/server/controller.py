import uuid
from collections import defaultdict


def count(exts):
    counts = defaultdict(int)
    for ext in exts:
        print(ext)
        for cat in ext.categories:
            counts[cat] += 1

    to_ret = []
    for key, value in counts.items():
        to_ret.append({
            "name": key,
            "count": value
        })

    return to_ret


def create_wrapper(extension):
    base_url = \
        f"https://marketplace.visualstudio.com/extensions" \
        "/{extension.publisher}/{extension.name}/{extension.version}"


    properties = []
    for key, value in extension.properties.items():
        properties.append({
            "key": key,
            "value": value
        })

    return \
        {
            "publisher": {
                "publisherId": uuid.uuid3(
                    uuid.NAMESPACE_OID, extension.publisher
                ),
                "publisherName": extension.publisher,
                "displayName": extension.publisher,
                "flags": "none"
            },
            "extensionId": uuid.uuid3(uuid.NAMESPACE_OID, extension.name),
            "extensionName": extension.name,
            "displayName": extension.display_name,
            "flags": "validated, public",
            "lastUpdated": "2019-08-22T11:39:45.023Z",
            "publishedDate": "2016-07-14T21:02:33.24Z",
            "releaseDate": "2016-07-14T21:02:33.24Z",
            "shortDescription": extension.description,
            "versions": [
                {
                    "version": extension.version,
                    "flags": "validated",
                    "lastUpdated": "2019-08-22T11:42:07.267Z",
                    "files": [
                        {
                            "assetType": "Microsoft.VisualStudio.Code.Manifest",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Code.Manifest"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.Content.Details",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.Content.Details"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.Content.License",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.Content.License"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.Icons.Default",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.Icons.Default"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.Icons.Small",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.Icons.Small"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.VsixManifest",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.VsixManifest"
                        },
                        {
                            "assetType":
                                "Microsoft.VisualStudio.Services.VSIXPackage",
                            "source":
                                f"{base_url}/Microsoft.VisualStudio.Services.VSIXPackage"
                        }
                    ],
                    "properties": properties,
                    "assetUri": base_url,
                    "fallbackAssetUri": base_url
                }
            ],
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
