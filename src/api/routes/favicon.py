"""Favicon endpoint."""
from fastapi import APIRouter, Response

router = APIRouter(tags=["Static"])


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Serve a favicon as SVG.
    """
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="100" height="100" rx="20" fill="url(#grad)"/>
        <circle cx="30" cy="35" r="15" fill="#48bb78" opacity="0.9"/>
        <circle cx="70" cy="35" r="15" fill="#f6e05e" opacity="0.9"/>
        <rect x="20" y="55" width="60" height="8" rx="4" fill="#4299e1" opacity="0.9"/>
        <path d="M 30 70 Q 50 85 70 70" stroke="#ed8936" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.9"/>
        <text x="50" y="90" font-size="12" text-anchor="middle" fill="white" font-weight="bold">BR</text>
    </svg>"""
    
    return Response(content=svg_content, media_type="image/svg+xml")
