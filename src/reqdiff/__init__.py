"""reqdiff: Detect unused and undeclared Python dependencies."""

from reqdiff.core import run_check
from reqdiff.models import ReqcheckConfig, ScanResult

__version__ = "0.1.0"
__all__ = ["run_check", "ScanResult", "ReqcheckConfig", "__version__"]
