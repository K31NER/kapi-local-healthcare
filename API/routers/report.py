from fastapi import APIRouter, Depends
from fastapi.responses import Response
from Use_cases.report.export_pdf import ExportPDF
from API.depends import get_export_pdf

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/export")
def export_report(uc: ExportPDF = Depends(get_export_pdf)):
    pdf_bytes = uc.execute()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=kapi_historial.pdf"},
    )
