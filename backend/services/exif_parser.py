import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

import piexif
from PIL import Image

logger = logging.getLogger(__name__)


class ExifParser:
    """Extract EXIF metadata from image files using PIL and piexif."""

    # EXIF tag constants
    TAG_DATETIME_ORIGINAL = 36867   # DateTimeOriginal
    TAG_DATETIME_DIGITIZED = 36868  # DateTimeDigitized
    TAG_EXPOSURE_TIME = 33434       # ExposureTime (Rational)
    TAG_F_NUMBER = 33437            # FNumber (Rational)
    TAG_ISO = 34855                 # ISOSpeedRatings
    TAG_FOCAL_LENGTH = 37386        # FocalLength (Rational)
    TAG_LENS_MODEL = 42036          # LensModel

    @staticmethod
    def parse(file_path: str | Path) -> dict:
        file_path = Path(file_path)
        result = {
            "date_taken": None, "camera_make": None, "camera_model": None,
            "lens_model": None, "f_number": None, "exposure_time": None,
            "iso": None, "focal_length": None,
            "gps_latitude": None, "gps_longitude": None,
            "orientation": 1, "width": None, "height": None,
            "date_modified": None,
        }
        try:
            result["date_modified"] = datetime.fromtimestamp(os.path.getmtime(file_path))
        except OSError:
            pass

        try:
            img = Image.open(file_path)
            result["width"], result["height"] = img.size
        except Exception:
            return result

        exif_dict = ExifParser._load_exif_dict(img)
        if exif_dict is None:
            result["date_taken"] = ExifParser._parse_date_taken(img, None, file_path)
            return result

        # Orientation
        try:
            ifd0 = exif_dict.get("0th", {})
            orientation_val = ifd0.get(piexif.ImageIFD.Orientation)
            if orientation_val is not None:
                result["orientation"] = int(orientation_val)
        except (KeyError, ValueError, TypeError):
            pass

        # Camera make / model
        try:
            result["camera_make"] = ExifParser._safe_decode(ifd0, piexif.ImageIFD.Make)
        except Exception:
            pass
        try:
            result["camera_model"] = ExifParser._safe_decode(ifd0, piexif.ImageIFD.Model)
        except Exception:
            pass

        # EXIF IFD
        exif_ifd = exif_dict.get("Exif", {})

        try:
            result["lens_model"] = ExifParser._safe_decode(exif_ifd, ExifParser.TAG_LENS_MODEL)
        except Exception:
            pass

        # F-number
        f_num = ExifParser._safe_get_rational(exif_ifd, ExifParser.TAG_F_NUMBER)
        if f_num is not None:
            result["f_number"] = round(float(f_num), 2)

        # Exposure time
        exp_time = ExifParser._safe_get_rational(exif_ifd, ExifParser.TAG_EXPOSURE_TIME)
        if exp_time is not None:
            result["exposure_time"] = ExifParser._format_exposure_time(exp_time)

        # ISO
        try:
            iso_val = exif_ifd.get(ExifParser.TAG_ISO)
            if iso_val is not None:
                result["iso"] = int(iso_val)
        except (ValueError, TypeError):
            pass

        # Focal length
        focal = ExifParser._safe_get_rational(exif_ifd, ExifParser.TAG_FOCAL_LENGTH)
        if focal is not None:
            result["focal_length"] = round(float(focal), 2)

        # GPS
        lat, lon = ExifParser._parse_gps(exif_dict)
        result["gps_latitude"] = lat
        result["gps_longitude"] = lon

        # Date taken
        result["date_taken"] = ExifParser._parse_date_taken(img, exif_dict, file_path)

        try:
            img.close()
        except Exception:
            pass

        return result

    @staticmethod
    def _load_exif_dict(img: Image.Image) -> dict | None:
        try:
            exif_bytes = img.info.get("exif")
            if exif_bytes:
                return piexif.load(exif_bytes)
        except Exception:
            pass
        return None

    @staticmethod
    def _safe_decode(ifd: dict, tag: int) -> str | None:
        val = ifd.get(tag)
        if val is None:
            return None
        if isinstance(val, bytes):
            try:
                decoded = val.decode("utf-8").strip("\x00").strip()
                if decoded:
                    return decoded
            except UnicodeDecodeError:
                try:
                    decoded = val.decode("latin-1").strip("\x00").strip()
                    if decoded:
                        return decoded
                except UnicodeDecodeError:
                    return None
        if isinstance(val, str):
            stripped = val.strip("\x00").strip()
            if stripped:
                return stripped
        return None

    @staticmethod
    def _safe_get_rational(ifd: dict, tag: int) -> float | None:
        val = ifd.get(tag)
        if val is None:
            return None
        try:
            if isinstance(val, tuple) and len(val) == 2:
                if val[1] != 0:
                    return float(val[0]) / float(val[1])
            if isinstance(val, (int, float)):
                return float(val)
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return None

    @staticmethod
    def _format_exposure_time(value: float) -> str:
        if value <= 0:
            return str(value)
        if value < 1:
            denominator = round(1 / value)
            return f"1/{denominator}"
        return f"{value:.1f}"

    @staticmethod
    def _parse_date_taken(
        img: Image.Image, exif_dict: dict | None, file_path: Path
    ) -> datetime | None:
        # Priority 1: DateTimeOriginal from EXIF
        if exif_dict:
            for tag in [ExifParser.TAG_DATETIME_ORIGINAL, ExifParser.TAG_DATETIME_DIGITIZED]:
                exif_ifd = exif_dict.get("Exif", {})
                date_str = ExifParser._safe_decode(exif_ifd, tag)
                if date_str:
                    parsed = ExifParser._parse_exif_date(date_str)
                    if parsed:
                        return parsed
            # Priority 2: DateTime from IFD0
            ifd0 = exif_dict.get("0th", {})
            date_str = ExifParser._safe_decode(ifd0, piexif.ImageIFD.DateTime)
            if date_str:
                parsed = ExifParser._parse_exif_date(date_str)
                if parsed:
                    return parsed
        # Priority 3: file mtime
        dt = ExifParser._parse_date_from_mtime(file_path)
        if dt:
            return dt
        # Priority 4: folder name pattern
        return ExifParser._parse_date_from_folder(file_path)

    @staticmethod
    def _parse_exif_date(date_str: str) -> datetime | None:
        formats = [
            "%Y:%m:%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_date_from_mtime(file_path: Path) -> datetime | None:
        try:
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        except OSError:
            return None

    @staticmethod
    def _parse_date_from_folder(file_path: Path) -> datetime | None:
        """Parse date from parent folder name like '2023-10-25' or '20231025'."""
        parent_name = file_path.parent.name
        patterns = [
            (r"^(\d{4})[-_](\d{1,2})[-_](\d{1,2})$", [1, 2, 3]),   # 2023-10-25
            (r"^(\d{4})(\d{2})(\d{2})$", [1, 2, 3]),                # 20231025
        ]
        for pattern, indices in patterns:
            m = re.match(pattern, parent_name)
            if m:
                groups = m.groups()
                try:
                    return datetime(
                        int(groups[indices[0] - 1]),
                        int(groups[indices[1] - 1]),
                        int(groups[indices[2] - 1]),
                    )
                except (ValueError, IndexError):
                    continue
        return None

    @staticmethod
    def _parse_gps(exif_dict: dict) -> tuple[float | None, float | None]:
        try:
            gps_ifd = exif_dict.get("GPS", {})
            if not gps_ifd:
                return None, None

            lat = ExifParser._dms_to_decimal(
                gps_ifd.get(piexif.GPSIFD.GPSLatitude),
                ExifParser._safe_decode(gps_ifd, piexif.GPSIFD.GPSLatitudeRef)
            )
            lon = ExifParser._dms_to_decimal(
                gps_ifd.get(piexif.GPSIFD.GPSLongitude),
                ExifParser._safe_decode(gps_ifd, piexif.GPSIFD.GPSLongitudeRef)
            )
            return lat, lon
        except Exception:
            return None, None

    @staticmethod
    def _dms_to_decimal(dms: tuple | None, ref: str | None) -> float | None:
        if dms is None or len(dms) < 3:
            return None
        try:
            degrees = float(dms[0][0]) / float(dms[0][1]) if isinstance(dms[0], tuple) else float(dms[0])
            minutes = float(dms[1][0]) / float(dms[1][1]) if isinstance(dms[1], tuple) else float(dms[1])
            seconds = float(dms[2][0]) / float(dms[2][1]) if isinstance(dms[2], tuple) else float(dms[2])
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            if ref and ref.upper() in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)
        except (ValueError, TypeError, ZeroDivisionError):
            return None
