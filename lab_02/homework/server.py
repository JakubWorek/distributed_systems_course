from fastapi import FastAPI, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import asyncio
import ccxt
from datetime import datetime, timedelta
import io
import base64
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.dates as mdates
import pandas as pd
from pydantic import BaseModel, Field, field_validator
from typing import List
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import APIKeyHeader

app = FastAPI(title="Crypto Price API", version="1.0")
templates = Jinja2Templates(directory="templates")

SUPPORTED_CRYPTOS = ["BTC", "ETH", "LTC", "BNB", "XRP", "ADA", "SOL", "DOT"]
SUPPORTED_EXCHANGES = ["binance", "cryptocom", "coinbasepro", "kraken"]

# --- Authentication ---
API_KEY = "kielbasa_krakowska_podsuszana"
API_KEY_NAME = "Crypto-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    """Dependency to validate the API key."""
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# --- Models ---
class PriceComparisonRequest(BaseModel):
    crypto: str = Field(..., example="BTC", description="Cryptocurrency symbol (e.g., BTC)")
    exchange1: str = Field(..., example="binance", description="First exchange ID")
    exchange2: str = Field(..., example="kraken", description="Second exchange ID")

    @field_validator("crypto")
    @classmethod
    def crypto_must_be_supported(cls, v):
        if v not in SUPPORTED_CRYPTOS:
            raise ValueError(f"Unsupported cryptocurrency: {v}")
        return v

    @field_validator("exchange1", "exchange2")
    @classmethod
    def exchange_must_be_supported(cls, v):
        if v not in SUPPORTED_EXCHANGES:
            raise ValueError(f"Unsupported exchange: {v}")
        return v

class PriceComparisonResponse(BaseModel):
    crypto: str
    exchange1: str
    price1: float
    exchange2: str
    price2: float
    difference: float = Field(..., description="Percentage difference between prices (price2 - price1) / price1 * 100")

class ErrorResponse(BaseModel):
    detail: str

class ChartRequest(BaseModel):
    crypto: str = Field(..., example="BTC")
    exchange: str = Field(..., example="binance")
    period: str = Field(..., example="1d", description="Time period (1d, 1w, 1m)")

    @field_validator("crypto")
    @classmethod
    def crypto_must_be_supported(cls, v):
        if v not in SUPPORTED_CRYPTOS:
            raise ValueError(f"Unsupported cryptocurrency: {v}")
        return v

    @field_validator("exchange")
    @classmethod
    def exchange_must_be_supported(cls, v):
        if v not in SUPPORTED_EXCHANGES:
            raise ValueError(f"Unsupported exchange: {v}")
        return v
    
    @field_validator("period")
    @classmethod
    def period_check(cls, v):
        if v not in ["1d", "1w", "1m"]:
            raise ValueError("Period must be one of: 1d, 1w, 1m")
        return v

class ChartResponse(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded PNG image of the chart")
    crypto: str
    exchange: str
    period: str

class OHLCVData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class OHLCVResponse(BaseModel):
    data: List[OHLCVData]


# --- Helper Functions ---
async def fetch_crypto_price(exchange_id: str, symbol: str):
    """Fetches the latest price of a cryptocurrency from an exchange."""
    try:
        exchange = getattr(ccxt, exchange_id)()
        loop = asyncio.get_event_loop()
        ticker = await loop.run_in_executor(None, lambda: exchange.fetch_ticker(symbol))
        return ticker['last']
    except AttributeError:
        raise HTTPException(status_code=500, detail=f"Exchange {exchange_id} is not supported.")
    except ccxt.NetworkError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except ccxt.ExchangeError as e:
        raise HTTPException(status_code=500, detail=f"Exchange error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Other error: {str(e)}")

async def fetch_ohlcv(exchange_id: str, crypto: str, since: datetime, timeframe: str) -> List[List]:
    """Fetches OHLCV (open, high, low, close, volume) data for a cryptocurrency from an exchange."""
    symbol = f"{crypto}/USDT"
    try:
        exchange = getattr(ccxt, exchange_id)()
        since_ms = int(since.timestamp() * 1000)
        loop = asyncio.get_event_loop()
        ohlcv = await loop.run_in_executor(None, lambda: exchange.fetch_ohlcv(symbol, timeframe, since_ms))
        return ohlcv
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching OHLCV data from {exchange_id}: {str(e)}")

def generate_candlestick_chart(ohlcv: List[List]) -> str:
    """Generates candlestick chart."""
    if not ohlcv:
        raise ValueError("No OHLCV data available.")

    df = [
        [
            mdates.date2num(datetime.fromtimestamp(item[0] / 1000)),
            item[1],
            item[2],
            item[3],
            item[4],
            item[5]
        ] for item in ohlcv
    ]
    df = pd.DataFrame(df, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Date'] = pd.to_datetime(df['Date'], unit='D')
    df = df.set_index('Date')
    kwargs = dict(type='candle', style='yahoo', volume=True, figratio=(12, 8), title='Candlestick Chart')
    fig, ax = mpf.plot(df, **kwargs, returnfig=True)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data


# --- API Routers ---
router = InferringRouter()

@cbv(router)
class CryptoRoutes:
    @router.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def read_root(self, request: Request):
        """Displays the main form."""
        return templates.TemplateResponse("form.html", {"request": request, "cryptos": SUPPORTED_CRYPTOS, "exchanges": SUPPORTED_EXCHANGES})

    @router.post("/compare_prices/", response_model=PriceComparisonResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
    async def compare_prices_api(self, comparison_request: PriceComparisonRequest, api_key: str = Depends(get_api_key)):
        """Compares prices of a cryptocurrency on two exchanges."""
        symbol = f"{comparison_request.crypto}/USDT"
        try:
            price1, price2 = await asyncio.gather(
                fetch_crypto_price(comparison_request.exchange1, symbol),
                fetch_crypto_price(comparison_request.exchange2, symbol)
            )
            difference = ((price2 - price1) / price1) * 100
            return PriceComparisonResponse(
                crypto=comparison_request.crypto,
                exchange1=comparison_request.exchange1,
                price1=price1,
                exchange2=comparison_request.exchange2,
                price2=price2,
                difference=difference
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/compare", response_class=HTMLResponse, include_in_schema=False)
    async def compare_prices_form(self, request: Request):
        """Displays the price comparison form."""
        return templates.TemplateResponse("form.html", {"request": request, "cryptos": SUPPORTED_CRYPTOS, "exchanges": SUPPORTED_EXCHANGES})

    @router.post("/compare", response_class=HTMLResponse, include_in_schema=False)
    async def compare_prices_form_post(self, request: Request, crypto: str = Form(...), exchange1: str = Form(...), exchange2: str = Form(...)):
        """Handles form submission for price comparison, redirects to the API endpoint."""
        try:
            comparison_request = PriceComparisonRequest(crypto=crypto, exchange1=exchange1, exchange2=exchange2)
            api_response = await self.compare_prices_api(comparison_request, API_KEY)

            return templates.TemplateResponse("comparison.html", {
                "request": request,
                "crypto": api_response.crypto,
                "exchange1": api_response.exchange1,
                "price1": api_response.price1,
                "exchange2": api_response.exchange2,
                "price2": api_response.price2,
                "difference": api_response.difference
            })

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    @router.get("/get_chart/", response_model=ChartResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
    async def get_chart_api(self, chart_request: ChartRequest, api_key: str = Depends(get_api_key)):
        """Generates a candlestick chart for a cryptocurrency."""
        try:
            if chart_request.period == "1d":
                since = datetime.now() - timedelta(days=1)
                timeframe = '1h'
            elif chart_request.period == "1w":
                since = datetime.now() - timedelta(weeks=1)
                timeframe = '1d'
            elif chart_request.period == "1m":
                since = datetime.now() - timedelta(days=30)
                timeframe = '1d'

            ohlcv = await fetch_ohlcv(chart_request.exchange, chart_request.crypto, since, timeframe)
            img_data = generate_candlestick_chart(ohlcv)
            return ChartResponse(image_base64=img_data, crypto=chart_request.crypto, exchange=chart_request.exchange, period=chart_request.period)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/chart", response_class=HTMLResponse, include_in_schema=False)
    async def get_chart_form(self, request: Request):
        """Displays the chart generation form."""
        return templates.TemplateResponse("chart_form.html", {"request": request, "cryptos": SUPPORTED_CRYPTOS, "exchanges": SUPPORTED_EXCHANGES})

    @router.post("/chart", response_class=HTMLResponse, include_in_schema=False)
    async def generate_chart_form_post(self, request: Request, crypto: str = Form(...), exchange: str = Form(...), period: str = Form(...)):
        """Handles form submission for chart generation, redirects to the API endpoint."""
        try:
            chart_request = ChartRequest(crypto=crypto, exchange=exchange, period=period)
            api_response = await self.get_chart_api(chart_request, API_KEY)

            return templates.TemplateResponse("chart.html", {"request": request, "img_data": api_response.image_base64, "crypto": api_response.crypto, "exchange":api_response.exchange, "period": api_response.period})
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/ohlcv/{exchange}/{crypto}/{period}", response_model=OHLCVResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
    async def get_ohlcv_api(self, exchange: str, crypto: str, period: str, api_key: str = Depends(get_api_key)):
        """Retrieves OHLCV data for a cryptocurrency."""
        try:
            if crypto not in SUPPORTED_CRYPTOS:
                raise HTTPException(status_code=400, detail=f"Unsupported cryptocurrency: {crypto}")
            if exchange not in SUPPORTED_EXCHANGES:
                raise HTTPException(status_code=400, detail=f"Unsupported exchange: {exchange}")
            if period not in ["1d", "1w", "1m"]:
                raise HTTPException(status_code=400, detail="Period must be one of: 1d, 1w, 1m")

            if period == "1d":
                since = datetime.now() - timedelta(days=1)
                timeframe = '1h'
            elif period == "1w":
                since = datetime.now() - timedelta(weeks=1)
                timeframe = '1d'
            elif period == "1m":
                since = datetime.now() - timedelta(days=30)
                timeframe = '1d'

            ohlcv_raw = await fetch_ohlcv(exchange, crypto, since, timeframe)

            ohlcv_data = [
                OHLCVData(timestamp=item[0], open=item[1], high=item[2], low=item[3], close=item[4], volume=item[5])
                for item in ohlcv_raw
            ]
            return OHLCVResponse(data=ohlcv_data)

        except HTTPException as e:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)