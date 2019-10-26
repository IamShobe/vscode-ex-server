
import json
from enum import Enum
from typing import List
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from pydantic import BaseModel, Schema
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, Response, RedirectResponse, HTMLResponse

from indexer import Indexer
from controller import count
from extension import Extension


app = FastAPI(title="VSCode Extensions Server", version="0.3.1",
              docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

TEXT_FILTER_TYPE = 10

INDEXER = Indexer("/app/exts")

def index_packages():
    INDEXER.index_packages()

def get_text_filter(criterias):
    for criteria in criterias:
        if criteria.filterType == TEXT_FILTER_TYPE:
            return criteria.value

    return ""


@app.get("/redoc", include_in_schema=False)
async def redoc_html(req: Request) -> HTMLResponse:
    openapi_url = app.openapi_prefix + app.openapi_url
    return get_redoc_html(
        openapi_url=openapi_url,
        title=app.title + " - Redoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png",
        with_google_fonts=False
    )


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html(req: Request) -> HTMLResponse:
    openapi_url = app.openapi_prefix + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png"
    )


@app.get("/extensions/{publisher}/{package}/{version}/Microsoft.VisualStudio.Services.Icons.Default", 
         operation_id="getIcon", responses={200: {'content': {'image/png': {}}}})
async def get_package_icon(publisher: str, package: str, version: str):
    extension = INDEXER.get_extension(publisher, package, version)
    return Response(content=extension.icon,
                    media_type=f'image/{Path(extension.icon_path).suffix[1:]}')


@app.get("/extensions/{publisher}/{package}/{version}/Microsoft.VisualStudio.Code.Manifest",
         operation_id="getManifest")
async def get_package_manifest(publisher: str, package: str, version: str):
    extension = INDEXER.get_extension(publisher, package, version)
    return json.loads(extension.code_manifest)


@app.get("/extensions/{publisher}/{package}/{version}/Microsoft.VisualStudio.Services.Content.Details",
         operation_id="getDetails", responses={200: {'content': {'text/markdown': {}}}})
async def get_package_details(publisher: str, package: str, version: str):
    extension = INDEXER.get_extension(publisher, package, version)
    return Response(content=extension.details,
                    media_type="text/markdown")


@app.get("/extensions/{publisher}/{package}/{version}/Microsoft.VisualStudio.Services.Content.License",
         operation_id="getLicense", responses={200: {'content': {'plain/text': {}}}})
async def get_package_license(publisher: str, package: str, version: str):
    extension = INDEXER.get_extension(publisher, package, version)
    return extension.license

@app.get("/extensions/{publisher}/{package}/{version}/Microsoft.VisualStudio.Services.VSIXPackage",
         operation_id="getPackage")
async def get_package(publisher: str, package: str, version: str):
    extension = INDEXER.get_extension(publisher, package, version)
    print(extension.filename, flush=True)
    return RedirectResponse(url=f'/serve{extension.filename}')
    # FileResponse(extension.filename, media_type="application/zip", filename='Microsoft.VisualStudio.Services.VSIXPackage')


class CriteriaModel(BaseModel):
    filterType: int = TEXT_FILTER_TYPE
    value: str = ""

class FilterModel(BaseModel):
    pageNumber: int = Schema(1, ge=1)
    pageSize: int = 50
    sortBy: int = 0
    sortOrder: int = 0
    criteria: List[CriteriaModel] = [CriteriaModel()]
    flags: int = 914

class QueryModel(BaseModel):
    filters: List[FilterModel] = Schema([FilterModel()], min_items=1, max_items=1)


@app.post("/_apis/public/gallery/extensionquery", 
          operation_id="queryExtensions")
def query_extentions(query: QueryModel):
    if len(query.filters) == 0:
        text_filter = ""
        page_size = 50
        page_number = 1

    else:
        main_filter = query.filters[0]
        page_number = main_filter.pageNumber
        page_size = main_filter.pageSize
        text_filter = get_text_filter(main_filter.criteria)
    
    try:
        exts = INDEXER.search(text_filter)

    except:
        exts = []

    to_display = list(exts)[0 + page_size * (page_number - 1):
                      page_size + page_size * (page_number - 1)]

    return {
        "results": [
            {
                "extensions": [ext.query_data for ext in to_display],
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


class AcceptedTypes(str, Enum):
    in_close_write = "IN_CLOSE_WRITE"
    in_delete = "IN_DELETE"


class Update(BaseModel):
    path: str
    filename: str
    type_names: List[AcceptedTypes] = ["IN_CLOSE_WRITE"]


class StatusResponse(BaseModel):
    status: str


@app.post('/index_new', response_model=StatusResponse,
          operation_id="indexExtension")
def index_new_extension(update: Update):
    """Force Indexing new extension"""
    ext = Extension(Path(update.path) / update.filename)
    if "IN_CLOSE_WRITE" in update.type_names:
        INDEXER.index_package(ext)

    if "IN_DELETE" in update.type_names:
        if ext not in INDEXER.filename_to_extension_pack:
            return {"status": "OK"}

        INDEXER.remove_package(ext)  # get actual copy

    return {"status": "OK"}


@app.post("/reset_index", response_model=StatusResponse)
def reset_indexes():
    """Reset all indexes"""
    INDEXER.reset()
    return {"status": "OK"}
