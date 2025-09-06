# Polygon MCP Demo

A Streamlit demo application that replicates the functionality from the Polygon.io blog post: **"Creating stock market reports using OpenAI's GPT-5 and Agent SDK with the Polygon.io MCP server in under 200 lines of code"**.

## Features

- **Real-time Stock Data**: Integration with Polygon.io API for live market data
- **Chat Interface**: Interactive Streamlit chat interface for stock queries
- **Financial Analysis**: AI-powered analysis using OpenAI models
- **Report Generation**: Save analysis reports in markdown format
- **Query Validation**: Finance-related query validation
- **Command Line Tests**: Comprehensive test suite with sample data

## Files Structure

```
polygon-mcp/
├── Home.py                 # Main Streamlit app (full OpenAI integration)
├── simple_demo.py          # Simplified demo (Polygon.io only)
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (API keys)
├── tests/                 # Test scripts
│   ├── test_polygon_api.py    # Main API tests
│   └── test_simple_queries.py # Simple query tests
├── test-data/             # Generated test data (JSON files)
│   ├── aapl_*.json           # Apple stock data
│   ├── msft_*.json           # Microsoft stock data
│   ├── meta_*.json           # Meta stock data
│   ├── tsla_nvda_comparison.json # Tesla vs Nvidia comparison
│   └── simple_queries_results.json # Simple query test results
└── reports/               # Generated analysis reports
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   # Copy and edit .env file
   OPENAI_API_KEY=your_openai_api_key
   POLYGON_API_KEY=your_polygon_api_key
   ```

3. **Run the Application**:
   ```bash
   # Full demo (requires working OpenAI API)
   streamlit run Home.py
   
   # Simplified demo (Polygon.io only)
   streamlit run simple_demo.py
   ```

## Testing

Run the command line tests to verify functionality:

```bash
# Test Polygon.io API with blog post queries
python3 tests/test_polygon_api.py

# Test simple query processing
python3 tests/test_simple_queries.py
```

## Example Queries

Based on the blog post examples:

1. **Simple Price Query**: "Get the latest price of Microsoft"
2. **Deep Analysis**: "Do a deep dive on AAPL over the last year"
3. **Comparison**: "Compare TSLA and NVDA performance"
4. **News Query**: "What's the latest news on META?"

## Test Data

The `test-data/` directory contains JSON files with real API responses for:

- **Company Details**: Ticker information, market cap, descriptions
- **Stock Quotes**: Latest trading prices and volumes
- **Historical Data**: Daily aggregates for trend analysis
- **News Articles**: Recent financial news for each ticker
- **Comparisons**: Side-by-side analysis data

## Architecture

### Core Components

1. **PolygonAPI Class**: Wrapper for Polygon.io REST API
2. **FinancialAnalysisAgent**: OpenAI-powered analysis engine
3. **Query Processing**: Ticker extraction and validation
4. **Report Generation**: Markdown report creation
5. **Streamlit Interface**: Interactive chat UI

### Data Flow

1. User enters query in chat interface
2. System extracts ticker symbols from query
3. Polygon.io API fetches relevant market data
4. OpenAI processes data and generates analysis
5. Results displayed in chat with option to save report

## API Integration

### Polygon.io Endpoints Used

- `/v3/reference/tickers/{ticker}` - Company details
- `/v2/last/trade/{ticker}` - Latest quotes
- `/v2/aggs/ticker/{ticker}/range/` - Historical aggregates
- `/v2/reference/news` - Financial news

### OpenAI Integration

- **Model**: GPT-4.1-mini (configurable)
- **Guardrails**: Finance query validation
- **Analysis**: Comprehensive market analysis
- **Report Generation**: Structured markdown output

## Limitations

- OpenAI API key must support required models
- Polygon.io API has rate limits
- Some endpoints require premium Polygon.io subscription
- Real-time data may have delays

## Blog Post Reference

This demo implements the concepts from:
**"Creating stock market reports using OpenAI's GPT-5 and Agent SDK with the Polygon.io MCP server in under 200 lines of code"**

Published: August 19, 2025
URL: https://polygon.io/blog/creating-stock-market-reports-using-open-ais-gpt-5-and-agent-sdk-with-the-polygon-io-mcp-server-in-under-200-lines-of-code

## Disclaimer

*Not financial advice. For informational purposes only.*

