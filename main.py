import os
from pathlib import Path

import flask
from flask import Response, send_file
from attrdict import AttrDict

from indexer import Indexer
from extension import Extension
from controller import create_wrapper, count

app = flask.Flask(__name__)

TEXT_FILTER_TYPE = 10

INDEXER = Indexer("exts")


def get_text_filter(criterias):
    for criteria in criterias:
        if criteria.filterType == TEXT_FILTER_TYPE:
            return criteria.value

    return ""


@app.route("/extensions/<publisher>/<package>/<"
           "version>/Microsoft.VisualStudio.Services.Icons.Default")
def get_package_icon(publisher, package, version):
    extension = INDEXER.get_extension(publisher, package, version)
    return Response(extension.icon,
                    mimetype=f'image/{Path(extension.icon_path).suffix[1:]}')


@app.route("/extensions/<publisher>/<package>/<"
           "version>/Microsoft.VisualStudio.Code.Manifest")
def get_package_manifest(publisher, package, version):
    extension = INDEXER.get_extension(publisher, package, version)
    return extension.code_manifest


@app.route("/extensions/<publisher>/<package>/<"
           "version>/Microsoft.VisualStudio.Services.Content.Details")
def get_package_details(publisher, package, version):
    extension = INDEXER.get_extension(publisher, package, version)
    return extension.details


@app.route("/extensions/<publisher>/<package>/<"
           "version>/Microsoft.VisualStudio.Services.Content.License")
def get_package_license(publisher, package, version):
    extension = INDEXER.get_extension(publisher, package, version)
    return extension.license


@app.route("/extensions/<publisher>/<package>/<"
           "version>/Microsoft.VisualStudio.Services.VSIXPackage")
def get_package(publisher, package, version):
    extension = INDEXER.get_extension(publisher, package, version)
    return send_file(extension.filename)


@app.route("/_apis/public/gallery/extensionquery", methods=["GET", "POST"])
def query_extentions():
    text_filter = ""
    page_number = 1
    page_size = 50

    try:
        request = AttrDict(flask.request.json)
        main_filter = request.filters[0]
        page_number = main_filter.pageNumber
        page_size = main_filter.pageSize
        text_filter = get_text_filter(main_filter.criteria)

    except:
        pass

    try:
        exts = INDEXER.trie.get(text_filter)

    except:
        exts = []

    to_display = list(exts)[0 + page_size * (page_number - 1):
                      page_size + page_size * (page_number - 1)]

    return {
        "results": [
            {
                "extensions": [create_wrapper(ext) for ext in to_display],
                "pagingToken": None,
                "resultMetadata": [
                    {
                        "metadataType": "ResultCount",
                        "metadataItems": [
                            {
                                "name": "TotalCount",
                                "count": len(exts)
                            }
                        ]
                    },
                    {
                        "metadataType": "Categories",
                        "metadataItems": count(exts)
                    }
                ]
            }
        ]
    }

@app.route('/index_new', methods=["POST"])
def index_new_extension():
    request = AttrDict(flask.request.json)
    if "IN_CREATE" in request.type_names or "IN_MODIFY" in request.type_names:
        ext = extension(path(request.exts) / request.filename)
        INDEXER.index_package(ext)

    if "IN_DELETE" in request.type_names:
        ext = extension(path(request.exts) / request.filename)
        INDEXER.reset()

    print(f"new extension update: {request}")
    return "OK"

def index_packages():
    INDEXER.index_packages()


if __name__ == '__main__':
    index_packages()
    app.run(port=8443, host='0.0.0.0')
            # ssl_context=('server.crt', 'server.key'),
