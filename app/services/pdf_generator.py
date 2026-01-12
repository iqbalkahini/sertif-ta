import os
import re
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from weasyprint import HTML


class PDFGenerator:
    """Service for generating PDF letters using Jinja2 templates and WeasyPrint."""

    # Maximum PDF file size (10MB) to prevent disk exhaustion
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB in bytes

    # Regex pattern for safe filenames (alphanumeric, underscore, hyphen, spaces, dots)
    SAFE_FILENAME_PATTERN = re.compile(r'^[\w\s.-]+$')

    SUPPORTED_TEMPLATES = [
        "surat_dinas",
        "surat_edaran",
        "surat_pemberitahuan"
    ]

    def __init__(
        self,
        templates_dir: str | None = None,
        output_dir: str = "output"
    ):
        """
        Initialize the PDF generator.

        Args:
            templates_dir: Path to templates directory. Defaults to app/templates.
            output_dir: Path to output directory for generated PDFs.
        """
        if templates_dir is None:
            # Default to app/templates relative to this file
            current_dir = Path(__file__).parent.parent
            templates_dir = current_dir / "templates"

        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        # Define allowed static directory for logos
        self.static_dir = Path(__file__).parent.parent / "static"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment with autoescape enabled for security
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate(
        self,
        template_name: str,
        data: Dict[str, Any],
        logo_path: str | None = None
    ) -> bytes:
        """
        Generate a PDF from a template and data.

        Args:
            template_name: Name of the template (without .html extension).
            data: Dictionary of data to pass to the template.
            logo_path: Optional path to logo image.

        Returns:
            PDF file as bytes.

        Raises:
            ValueError: If template is not found or not supported.
        """
        template_file = f"{template_name}.html"

        if template_name not in self.SUPPORTED_TEMPLATES:
            raise ValueError(
                f"Template '{template_name}' is not supported. "
                f"Supported templates: {', '.join(self.SUPPORTED_TEMPLATES)}"
            )

        try:
            template = self.env.get_template(template_file)
        except TemplateNotFound:
            raise ValueError(
                f"Template file '{template_file}' not found in {self.templates_dir}"
            )

        # Prepare context for template
        context = data.copy()
        if logo_path:
            # Validate logo path - only allow files within app/static/ directory
            try:
                # Resolve the logo path to check for traversal attempts
                logo_path_obj = Path(logo_path).resolve()

                # Resolve static directory path
                static_dir_resolved = self.static_dir.resolve()

                # Check if the resolved logo path is within static directory
                if logo_path_obj.exists() and logo_path_obj.is_file():
                    # Verify the path is within static directory using relative_to
                    # This will raise ValueError if path is outside static_dir
                    logo_path_obj.relative_to(static_dir_resolved)
                    # Store relative path from templates dir for WeasyPrint
                    context["logo_path"] = logo_path
                else:
                    # Try relative path from static dir
                    relative_path = self.static_dir / logo_path
                    if relative_path.exists() and relative_path.is_file():
                        # Verify again after resolution
                        relative_path.resolve().relative_to(static_dir_resolved)
                        context["logo_path"] = f"static/{logo_path}"
                    else:
                        # File doesn't exist or is invalid - don't set logo_path
                        # Fail closed: no logo path if validation fails
                        pass
            except (OSError, ValueError):
                # Path traversal attempt or invalid path - fail closed, don't set logo
                pass

        # Render HTML
        html_string = template.render(data=context)

        # Convert to PDF using WeasyPrint
        html = HTML(string=html_string, base_url=str(self.templates_dir))
        pdf_bytes = html.write_pdf()

        return pdf_bytes

    def save_pdf(
        self,
        pdf_bytes: bytes,
        filename: str
    ) -> str:
        """
        Save PDF bytes to a file.

        Args:
            pdf_bytes: PDF file content as bytes.
            filename: Name of the file to save (without .pdf extension).

        Returns:
            Full path to the saved PDF file.

        Raises:
            ValueError: If filename is invalid or PDF size exceeds limit.
        """
        # Validate PDF size before writing
        if len(pdf_bytes) > self.MAX_PDF_SIZE:
            raise ValueError(
                f"PDF size ({len(pdf_bytes)} bytes) exceeds maximum allowed size "
                f"({self.MAX_PDF_SIZE} bytes)"
            )

        # Check for path traversal attempts BEFORE applying basename
        # This prevents inputs like "../../../etc/passwd" from becoming "passwd"
        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError(
                f"Invalid filename '{filename}'. "
                f"Path traversal attempts are not allowed."
            )

        # Sanitize filename to prevent path traversal attacks
        # Extract only the basename to remove any directory components
        safe_filename = os.path.basename(filename)

        # Remove .pdf extension if present for validation
        name_without_ext = safe_filename.replace(".pdf", "")

        # Validate filename contains only safe characters
        if not self.SAFE_FILENAME_PATTERN.match(name_without_ext):
            raise ValueError(
                f"Invalid filename '{filename}'. "
                f"Filename must contain only alphanumeric characters, spaces, "
                f"underscores, hyphens, and dots."
            )

        # Ensure .pdf extension
        if not safe_filename.endswith(".pdf"):
            safe_filename = f"{safe_filename}.pdf"

        # Final validation that filename is not empty
        if not safe_filename or safe_filename == ".pdf":
            raise ValueError("Invalid filename: filename cannot be empty")

        file_path = self.output_dir / safe_filename

        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        return str(file_path)
