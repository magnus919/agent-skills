"""ArcGIS ImageServer imagery adapter."""

from __future__ import annotations

import json
import urllib.parse
from typing import Any

from raleighlib import core


IMAGE_ROOT = "https://maps.raleighnc.gov/images/rest/services"
MAX_IMAGE_FOLDERS = 50
MAX_IMAGE_SERVICES = 1000


class CapabilityError(Exception):
    """Raised when an operation is requested that the service does not support."""


def _checked_json(data: Any, operation: str) -> dict[str, Any]:
    data = core.require_object(data, operation)
    core.raise_for_arcgis_error(data, operation)
    return data


def list_services(
    root_url: str = IMAGE_ROOT,
    max_folders: int = MAX_IMAGE_FOLDERS,
    max_services: int = MAX_IMAGE_SERVICES,
) -> list[dict[str, Any]]:
    """Recursively discover ImageServer services from the REST directory."""
    if max_folders < 0 or max_services < 1:
        raise ValueError("imagery discovery bounds are invalid")
    sep = "&" if "?" in root_url else "?"
    data = _checked_json(
        core.json_request(f"{root_url}{sep}f=pjson"), "Image service listing"
    )
    root_services = data.get("services", [])
    folders = data.get("folders", [])
    if not isinstance(root_services, list) or any(
        not isinstance(service, dict) for service in root_services
    ):
        raise CapabilityError("Image service listing returned invalid services")
    if not isinstance(folders, list) or any(
        not isinstance(folder, str) or not folder.strip() for folder in folders
    ):
        raise CapabilityError("Image service listing returned invalid folders")
    if len(folders) > max_folders:
        raise CapabilityError(
            f"Image service listing exceeded {max_folders} folders"
        )
    if len(root_services) > max_services:
        raise CapabilityError(
            f"Image service listing exceeded {max_services} services"
        )
    services = list(root_services)
    for folder in folders:
        folder_url = f"{root_url}/{urllib.parse.quote(folder, safe='')}"
        sep = "&" if "?" in folder_url else "?"
        folder_data = _checked_json(
            core.json_request(f"{folder_url}{sep}f=pjson"), "Image folder listing"
        )
        folder_services = folder_data.get("services", [])
        if not isinstance(folder_services, list) or any(
            not isinstance(service, dict) for service in folder_services
        ):
            raise CapabilityError("Image folder listing returned invalid services")
        if len(services) + len(folder_services) > max_services:
            raise CapabilityError(
                f"Image service listing exceeded {max_services} services"
            )
        for svc in folder_services:
            svc = dict(svc)
            svc["folder"] = folder
            services.append(svc)
    return services


def service_info(url: str) -> dict[str, Any]:
    """Fetch ImageServer service metadata."""
    sep = "&" if "?" in url else "?"
    return _checked_json(
        core.json_request(f"{url}{sep}f=pjson"), "Image service metadata"
    )


def supports_capability(info: dict[str, Any], capability: str) -> bool:
    """Return True if the service info advertises the given capability."""
    caps = info.get("capabilities", "")
    return capability.lower() in [c.strip().lower() for c in str(caps).split(",")]


def _bbox_str(bbox: tuple[float, float, float, float]) -> str:
    return ",".join(str(round(c, 6)) for c in bbox)


def export_image(
    url: str,
    bbox: tuple[float, float, float, float],
    size: tuple[int, int] | None = None,
    format_: str = "jpgpng",
    in_sr: int = 4326,
    out_sr: int = 4326,
    **kwargs: Any,
) -> bytes:
    """Export a bounded image from an ImageServer."""
    info = service_info(url)
    if not supports_capability(info, "Image"):
        raise CapabilityError(f"{url} does not advertise Image capability")
    max_width = info.get("maxImageWidth", 4000)
    max_height = info.get("maxImageHeight", 4000)
    if size:
        if size[0] > max_width or size[1] > max_height:
            raise CapabilityError(
                f"Requested image size {size} exceeds server maximum {max_width}x{max_height}"
            )
    base = url.rstrip("/") + "/exportImage"
    params: dict[str, Any] = {
        "bbox": _bbox_str(bbox),
        "bboxSR": in_sr,
        "imageSR": out_sr,
        "format": format_,
        "f": "image",
    }
    if size:
        params["size"] = f"{size[0]},{size[1]}"
    for key, value in kwargs.items():
        params[key] = value
    full_url = f"{base}?{urllib.parse.urlencode(params)}"
    body = core.raw_request(full_url)
    if body.lstrip().startswith(b"{"):
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CapabilityError("Image export returned malformed JSON instead of an image") from exc
        if isinstance(payload, dict):
            core.raise_for_arcgis_error(payload, "Image export")
        raise CapabilityError("Image export returned JSON instead of an image")
    image_signatures = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a", b"II*\x00", b"MM\x00*", b"BM")
    if not any(body.startswith(signature) for signature in image_signatures):
        raise CapabilityError("Image export returned an unrecognized non-image response")
    return body


def identify(
    url: str,
    point: tuple[float, float],
    in_sr: int = 4326,
    out_sr: int = 4326,
    **kwargs: Any,
) -> dict[str, Any]:
    """Identify pixel value at a point on an ImageServer."""
    info = service_info(url)
    if not supports_capability(info, "Image"):
        raise CapabilityError(f"{url} does not advertise Image capability")
    base = url.rstrip("/") + "/identify"
    params: dict[str, Any] = {
        "geometry": json.dumps({"x": point[0], "y": point[1]}),
        "geometryType": "esriGeometryPoint",
        "inSR": in_sr,
        "outSR": out_sr,
        "f": "json",
    }
    for key, value in kwargs.items():
        params[key] = value
    full_url = f"{base}?{urllib.parse.urlencode(params)}"
    return _checked_json(core.json_request(full_url), "Image identify")


def compute_statistics(
    url: str,
    bbox: tuple[float, float, float, float],
    in_sr: int = 4326,
    out_sr: int = 4326,
    **kwargs: Any,
) -> dict[str, Any]:
    """Compute statistics for an extent on an ImageServer."""
    info = service_info(url)
    if not supports_capability(info, "Image"):
        raise CapabilityError(f"{url} does not advertise Image capability")
    base = url.rstrip("/") + "/computeStatisticsHistograms"
    params: dict[str, Any] = {
        "geometry": json.dumps(
            {
                "xmin": bbox[0],
                "ymin": bbox[1],
                "xmax": bbox[2],
                "ymax": bbox[3],
            }
        ),
        "geometryType": "esriGeometryEnvelope",
        "inSR": in_sr,
        "outSR": out_sr,
        "f": "json",
    }
    for key, value in kwargs.items():
        params[key] = value
    full_url = f"{base}?{urllib.parse.urlencode(params)}"
    return _checked_json(core.json_request(full_url), "Image statistics")
