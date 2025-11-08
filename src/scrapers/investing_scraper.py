"""Investing.com scraper for Brazilian CDS data."""
import io
import re
from typing import Optional

import pandas as pd
import requests
from lxml import html as lxhtml
from requests.adapters import HTTPAdapter, Retry

from config import settings
from src.utils import get_logger

logger = get_logger()


def _clean_number(s: str) -> Optional[float]:
    """Clean and convert string to float.
    
    Handles Brazilian number format (1.234,56) and percentages.
    
    Args:
        s: String to convert
        
    Returns:
        Float value divided by 100, or None if conversion fails
    """
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() in {"nan", "none", "null", "-"}:
        return None
    # troca vírgula por ponto (pt-BR)
    s = s.replace(".", "").replace(",", ".")  # "1.234,56" -> "1234.56"
    # remove % se houver
    s = s.replace("%", "")
    try:
        return float(s) / 100
    except ValueError:
        return None


def _parse_change_pct(s: str) -> Optional[float]:
    """Parse percentage change string.
    
    Maintains sign correctly and removes the '%' symbol.
    
    Args:
        s: String to parse
        
    Returns:
        Float percentage value, or None if parsing fails
    """
    if s is None:
        return None
    s = s.strip().replace(" ", "")
    s = s.replace("%", "")
    # vírgula decimal -> ponto
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        # tenta capturar algo como "+1.56%" já sem %, mas com unicode
        m = re.search(r"([+-]?\d+(?:\.\d+)?)", s)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        return None


def _requests_session_with_retries(
    total: Optional[int] = None,
    backoff_factor: Optional[float] = None
) -> requests.Session:
    """Create a requests session with retry configuration.
    
    Args:
        total: Total number of retries
        backoff_factor: Backoff factor between retries
        
    Returns:
        Configured requests Session
    """
    if total is None:
        total = settings.REQUEST_RETRIES
    if backoff_factor is None:
        backoff_factor = settings.REQUEST_BACKOFF_FACTOR

    s = requests.Session()
    retries = Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def fetch_html(url: str) -> str:
    """Fetch HTML content from URL.
    
    Args:
        url: URL to fetch
        
    Returns:
        HTML content as string
        
    Raises:
        requests.HTTPError: If request fails
    """
    session = _requests_session_with_retries()
    r = session.get(url, headers=settings.request_headers, timeout=settings.REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.text


def _normalize_investing_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize Investing.com table structure.
    
    Converts column names to standard format (OHLC) and cleans data.
    
    Args:
        df_raw: Raw DataFrame from Investing.com
        
    Returns:
        Normalized DataFrame with date, open, high, low, close, change_pct columns
    """
    df = df_raw.copy()
    # normaliza nomes de coluna
    lower_cols = {c: str(c).strip().lower() for c in df.columns}
    df.rename(columns=lower_cols, inplace=True)

    # mapeia colunas esperadas
    # em pt: data, último, abertura, máxima, mínima, var%
    # em en pode vir: date, price/last, open, high, low, change %
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if "data" in cl or "date" in cl:
            col_map[c] = "date"
        elif "abert" in cl or "open" in cl:
            col_map[c] = "open"
        elif "máxima" in cl or "maxima" in cl or "high" in cl:
            col_map[c] = "high"
        elif "mínima" in cl or "minima" in cl or "low" in cl:
            col_map[c] = "low"
        elif "último" in cl or "ultimo" in cl or "close" in cl or "price" in cl or "fech" in cl:
            col_map[c] = "close"
        elif "var" in cl and "%" in cl:
            col_map[c] = "change_pct"

    df.rename(columns=col_map, inplace=True)

    expected = ["date", "open", "high", "low", "close", "change_pct"]
    # mantém apenas as que temos
    keep = [c for c in expected if c in df.columns]
    df = df[keep].copy()

    # converte tipos
    # datas vêm em "dd.mm.yyyy" no HTML (e podem vir "dd/mm/yyyy" em outras versões)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True, format=None)
    if "close" in df.columns:
        df["close"] = df["close"].apply(_clean_number)
    if "open" in df.columns:
        df["open"] = df["open"].apply(_clean_number)
    if "high" in df.columns:
        df["high"] = df["high"].apply(_clean_number)
    if "low" in df.columns:
        df["low"] = df["low"].apply(_clean_number)
    if "change_pct" in df.columns:
        df["change_pct"] = df["change_pct"].apply(_parse_change_pct)

    # ordena colunas para formato OHLC
    col_order = ['date', 'open', 'high', 'low', 'close', 'change_pct']
    df = df[[c for c in col_order if c in df.columns]]

    # remove linhas sem data ou sem preço
    df = df.dropna(subset=["date"])
    if "close" in df.columns:
        df = df.dropna(subset=["close"])

    # ordena do mais antigo para o mais recente (facilita merges)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def parse_table_with_read_html(page_html: str) -> Optional[pd.DataFrame]:
    """Parse table using pandas read_html.
    
    Args:
        page_html: HTML content to parse
        
    Returns:
        Normalized DataFrame or None if parsing fails
    """
    try:
        tables = pd.read_html(io.StringIO(page_html))
    except ValueError:
        return None

    candidates = []
    for t in tables:
        cols = [str(c).lower() for c in t.columns]
        if any("data" in c for c in cols) and (
            any("último" in c for c in cols) or any("ultimo" in c for c in cols) or any("close" in c for c in cols)
        ):
            candidates.append(t)

    if not candidates:
        return None

    # Pega a primeira candidata
    df = candidates[0].copy()
    return _normalize_investing_table(df)


def parse_table_with_xpath(page_html: str) -> Optional[pd.DataFrame]:
    """Parse table using XPath.
    
    Fallback method when pandas read_html fails.
    
    Args:
        page_html: HTML content to parse
        
    Returns:
        Normalized DataFrame or None if parsing fails
    """
    try:
        root = lxhtml.fromstring(page_html)
        tables = root.xpath(settings.TABLE_XPATH)
        if not tables:
            return None
        table_el = tables[0]

        # Extrai cabeçalhos
        headers = [("".join(th.itertext())).strip() for th in table_el.xpath(".//thead//th")]
        rows = []
        for tr in table_el.xpath(".//tbody//tr"):
            cells = [("".join(td.itertext())).strip() for td in tr.xpath("./td")]
            if cells:
                rows.append(cells)
        if not headers or not rows:
            return None

        df = pd.DataFrame(rows, columns=headers)
        return _normalize_investing_table(df)
    except Exception as e:
        logger.error(f"Falha no parsing por XPath: {e}")
        return None


def fetch_investing_cds() -> pd.DataFrame:
    """Fetch Brazilian CDS data from Investing.com.
    
    Tries multiple parsing methods (read_html, then XPath) to extract the data.
    
    Returns:
        DataFrame with CDS historical data
        
    Raises:
        RuntimeError: If all parsing methods fail
    """
    logger.info("Baixando página do Investing…")
    html = fetch_html(settings.INVESTING_URL)

    # 1) tenta read_html
    df = parse_table_with_read_html(html)
    if df is not None and not df.empty:
        logger.success(f"Tabela capturada com read_html: {len(df)} linhas.")
        return df

    # 2) fallback: XPath
    logger.warning("read_html não encontrou a tabela; tentando XPath…")
    df = parse_table_with_xpath(html)
    if df is not None and not df.empty:
        logger.success(f"Tabela capturada com XPath: {len(df)} linhas.")
        return df

    raise RuntimeError("Não foi possível capturar a tabela do Investing.")
