# Schwab Streamer API

The Streamer API enables clients to connect into different services to stream market data and account activity with JSON-formatting via WebSockets. Authentication and entitlements are provided via the Access token generated from the POST Token endpoint. Streamer information to establish the connection can be found on the GET User Preference endpoint. "Client" as referenced throughout this document refers to the application.

---

## Contents

1. [API Contract](#1-api-contract)
2. [Admin Services](#2-admin-services)
3. [LEVELONE Services](#3-levelone-services)
4. [BOOK Services](#4-book-services)
5. [CHART Services](#5-chart-services)
6. [SCREENER Services](#6-screener-services)
7. [ACCOUNT Services](#7-account-services)

---

## 1. API Contract

### 1.1 Services Available

| Service Name | Description | Delivery Type |
|---|---|---|
| LEVELONE_EQUITIES | Level 1 Equities | Change |
| LEVELONE_OPTIONS | Level 1 Options | Change |
| LEVELONE_FUTURES | Level 1 Futures | Change |
| LEVELONE_FUTURES_OPTIONS | Level 1 Futures Options | Change |
| LEVELONE_FOREX | Level 1 Forex | Change |
| NYSE_BOOK | Level Two book for Equities | Whole |
| NASDAQ_BOOK | Level Two book for Equities | Whole |
| OPTIONS_BOOK | Level Two book for Options | Whole |
| CHART_EQUITY | Chart candle for Equities | All Sequence |
| CHART_FUTURES | Chart candle for Futures | All Sequence |
| SCREENER_EQUITY | Advances and Decliners for Equities | Whole |
| SCREENER_OPTION | Advances and Decliners for Options | Whole |
| ACCT_ACTIVITY | Get account activity information such as order fills, etc | All Sequence |

### 1.2 Request Format

A client request will consist of an array of one or more commands. Each command will include:

| Request | Name | Parameter |
|---|---|---|
| service | Service Name (required) | ADMIN, LEVELONE_EQUITY, etc. See Service Names table above. |
| command | Command (required) | LOGIN, SUBS, ADD, UNSUBS, VIEW, LOGOUT |
| requestid | Request ID (required) | Unique number that will identify this request. |
| SchwabClientCustomerId | Client's customer ID | `schwabClientCustomerId` as found in GET User Preference endpoint |
| SchwabClientCorrelId | Client's session ID | `schwabClientCorrelId` as found in GET User Preference endpoint. Unique identifier value attached to requests and messages that allow reference to a particular transaction or event chain. |
| parameters | Any parameter (optional) | fields, version, credential, symbol, frequency, period, etc. |

#### Command Descriptions

| Command | Description |
|---|---|
| LOGIN | Initial request when opening a new connection. Must be successful before sending other commands. |
| SUBS | Subscribes to a set of symbols or keys for a particular service. Overwrites all previously subscribed symbols for that service. Use ADD instead if you only want to add symbols to an existing subscription. |
| ADD | Adds a new symbol for a particular service without wiping out previous subscriptions. OK to use ADD for the first subscription instead of SUBS. |
| UNSUBS | Unsubscribes a symbol from the list of subscribed symbols for a particular service. |
| VIEW | Changes the field subscription for a particular service. Applies to all symbols for that service. |
| LOGOUT | Logs out of the streamer connection. Streamer will close the connection. |

**SUBS example:**
1. `SUBS A,B,C` — fresh sub for LEVELONE_EQUITIES
2. `SUBS A` — previous SUBS of B, C are unsubbed; only A is subbed

**ADD example:**
1. `ADD A,B` — fresh sub for LEVELONE_EQUITIES
2. `ADD C` — C added to A, B; all 3 stream

#### Request Examples

**Single Request:**
```json
{
  "requestid": "0",
  "service": "LEVELONE_EQUITIES",
  "command": "SUBS",
  "SchwabClientCustomerId": "Someone",
  "SchwabClientCorrelId": "3be0b7e7-5b8b-4fd3-9bed-7f49106cfe1",
  "parameters": {
    "keys": "AAPL",
    "fields": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51"
  }
}
```

**Multiple Requests:**
```json
{
  "requests": [
    {
      "requestid": "1",
      "service": "ADMIN",
      "command": "LOGIN",
      "SchwabClientCustomerId": "Someone",
      "SchwabClientCorrelId": "2be0b7e7-5b8b-4fd3-9bed-7f49106cfe1",
      "parameters": {
        "Authorization": "PN",
        "SchwabClientChannel": "IO",
        "SchwabClientFunctionId": "Tradeticket"
      }
    },
    {
      "requestid": "3",
      "service": "LEVELONE_EQUITIES",
      "command": "SUBS",
      "SchwabClientCustomerId": "Someone",
      "SchwabClientCorrelId": "2be0b7e7-5b8b-4fd3-9bed-7f49106cfe1",
      "parameters": {
        "keys": "AAPL",
        "fields": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19"
      }
    }
  ]
}
```

### 1.3 Response Format

Three types of responses:

- **Response** — Response to a request
- **Notify** — Notification of heartbeats
- **Data** — Streaming market data

Each response includes:

| Response Type | Request Name | Parameter |
|---|---|---|
| response / notify / data | service | ADMIN, LEVELONE_EQUITY, etc. |
| | requestid | Unique number identifying the original request |
| | command | LOGIN, SUBS, ADD, UNSUBS, VIEW, LOGOUT |
| | content | Data content |

**Examples:**

Heartbeat:
```json
{"notify":[{"heartbeat":"1668715930582"}]}
```

Response:
```json
{
  "response": [
    {
      "service": "LEVELONE_EQUITIES",
      "command": "SUBS",
      "requestid": "0",
      "SchwabClientCorrelId": "3be0b7e7-5b8b-4fd3-9bed-7f49106cfe1",
      "timestamp": 1668715930582,
      "content": {
        "code": 0,
        "msg": "SUBS command succeeded"
      }
    }
  ]
}
```

Data:
```json
{
  "data": [
    {
      "service": "LEVELONE_EQUITIES",
      "timestamp": 1668715930585,
      "command": "SUBS",
      "content": [
        {
          "1": 149.81,
          "2": 149.82,
          "3": 149.811,
          "4": 4,
          "5": 2,
          "6": "Q",
          "7": "P",
          "8": 56049058,
          "9": 300,
          "10": 151.48,
          "11": 146.15,
          "12": " ",
          "13": 142.41,
          "14": "Q",
          "15": false,
          "16": "APPLE INC",
          "17": "D",
          "18": 146.43,
          "19": 7.401,
          "20": 182.94,
          "21": 129.04,
          "22": 0.04062,
          "23": 0,
          "24": 0,
          "25": 0,
          "26": "NASDAQ",
          "27": "",
          "28": true,
          "29": true,
          "30": 149.811,
          "31": 300,
          "32": 7.401,
          "33": "Normal",
          "34": 149.811,
          "35": 1668715930570,
          "36": 1668715930345,
          "37": 1668715930345,
          "38": 1668715930570,
          "39": 1668715930522,
          "40": "XNAS",
          "41": "ARCX",
          "42": "XADF",
          "43": 5.19696651,
          "44": 5.19696651,
          "45": 7.401,
          "46": 5.19696651,
          "key": "AAPL",
          "delayed": false
        }
      ]
    }
  ]
}
```

### 1.4 Response Codes

| Code | Name | Description | Connection Severed | Notes |
|---|---|---|---|---|
| 0 | SUCCESS | Request was successful | No | n/a |
| 3 | LOGIN_DENIED | User login has been denied | Yes | Client should reconnect and re-login with new token. |
| 9 | UNKNOWN_FAILURE | Error of last-resort when no specific error was caught | TBD | Contact TraderAPI@Schwab.com with `schwabClientCorrelId`. |
| 11 | SERVICE_NOT_AVAILABLE | The service is not available | No | Contact TraderAPI@Schwab.com. Either an unsupported service or the service is not running. |
| 12 | CLOSE_CONNECTION | Reached maximum number of connections allowed | Yes | Limit of 1 Streamer connection at a time per user. |
| 19 | REACHED_SYMBOL_LIMIT | Subscribe or Add command reached total subscription symbol limit | No | Client to determine if symbol limit is expected. |
| 20 | STREAM_CONN_NOT_FOUND | No connection found for user or new session but no login request | TBD | Common causes: race condition where SUB is processed before LOGIN; modified SchwabClientCustomerId or SchwabClientCorrelId after login; streamer disconnected while processing command. |
| 21 | BAD_COMMAND_FORMAT | Command fails to match specification | No | Client should investigate why command is not formatted properly. |
| 22 | FAILED_COMMAND_SUBS | Subscribe command could not be completed | No | Contact TraderAPI@Schwab.com. Common cause: two or more commands processed in parallel. |
| 23 | FAILED_COMMAND_UNSUBS | Unsubscribe command could not be completed | No | |
| 24 | FAILED_COMMAND_ADD | Add command could not be completed | No | |
| 25 | FAILED_COMMAND_VIEW | View command could not be completed | No | |
| 26 | SUCCEEDED_COMMAND_SUBS | Subscribe command completed successfully | No | n/a |
| 27 | SUCCEEDED_COMMAND_UNSUBS | Unsubscribe command completed successfully | No | |
| 28 | SUCCEEDED_COMMAND_ADD | Add command completed successfully | No | |
| 29 | SUCCEEDED_COMMAND_VIEW | View command completed successfully | No | |
| 30 | STOP_STREAMING | Streaming terminated due to administrator action, inactivity, or slowness | Yes | Typically due to no subscriptions. See message for details. |

### 1.5 Delivery Types

| Delivery Type | Description |
|---|---|
| All Sequence | All data is streamed to the client and includes a sequence number. Data is not conflated by the streamer, though the underlying source may conflate. |
| Change | Only fields that clients are subscribed to and have changed are streamed. Data is conflated by the streamer. |
| Whole | Data is streamed as a whole unit to the client, in throttled mode. |

---

## 2. Admin Services

### 2.1 Login Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | ADMIN |
| command | String | Variable | LOGIN |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.Authorization | String | Variable | Access token from POST Token endpoint. |
| parameters.SchwabClientChannel | String | 2 | Channel identifier from GET User Preferences endpoint. |
| parameters.SchwabClientFunctionId | String | 5 | Page or source identifier (5 alphanumeric) from GET User Preferences endpoint. |

**Login Request Example:**
```json
{
  "requests": [
    {
      "requestid": "1",
      "service": "ADMIN",
      "command": "LOGIN",
      "SchwabClientCustomerId": "Someone",
      "SchwabClientCorrelId": "5be0b7e7-5b8b-4fd3-9bed-7f49106cfe96",
      "parameters": {
        "Authorization": "Access Token",
        "SchwabClientChannel": "N9",
        "SchwabClientFunctionId": "APIAPP"
      }
    }
  ]
}
```

### 2.2 Login Response

| Type | Request Name | Type | Description |
|---|---|---|---|
| response | service | | ADMIN |
| | requestid | | Unique request ID number |
| | command | | LOGIN |
| | SchwabClientCorrelId | | Correlation ID string passed by client |
| | timestamp | | Milliseconds since epoch |
| | content.code | Integer | 0 = Success, 3 = Login denied |
| | content.msg | String | `server=hostname-instance`; `status=PN` (Non-Paying Pro), `NP` (Non-Pro), `PP` (Paying-Pro). If no entitlements, client will get NFL/delayed quotes. |

**Login Successful:**
```json
{
  "response": [
    {
      "service": "ADMIN",
      "command": "LOGIN",
      "requestid": "1",
      "SchwabClientCorrelId": "5be0b7e7-5b8b-4fd3-9bed-7f49106cfe96",
      "timestamp": 1669828276886,
      "content": {
        "code": 0,
        "msg": "server=s0166bdv-1;status=PN"
      }
    }
  ]
}
```

**Login Denied:**
```json
{
  "response": [
    {
      "service": "ADMIN",
      "command": "LOGIN",
      "requestid": "1",
      "SchwabClientCorrelId": "5be0b7e7-5b8b-4fd3-9bed-7f49106cfe96",
      "timestamp": 1669828982588,
      "content": {
        "code": 3,
        "msg": "Login Denied.: token is invalid or has expired."
      }
    }
  ]
}
```

### 2.3 Logout Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | ADMIN |
| command | String | Variable | LOGOUT |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | From GET User Preferences endpoint (5 alphanumeric). |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters | String | Variable | Can leave empty. |

### 2.4 Logout Response

```json
{
  "response": [
    {
      "service": "ADMIN",
      "command": "LOGOUT",
      "requestid": "0",
      "SchwabClientCorrelId": "5be0b7e7-5b8b-4fd3-9bed-7f49106cfe95",
      "timestamp": 1669830137089,
      "content": {
        "code": 0,
        "msg": "SUCCESS"
      }
    }
  ]
}
```

---

## 3. LEVELONE Services

### 3.1 LEVELONE_EQUITIES

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | LEVELONE_EQUITIES |
| command | String | Variable | SUBS, UNSUBS, ADD, VIEW |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | Schwab-standard symbols in uppercase, comma-separated. e.g. `AAPL,TSLA,IBM` |
| parameters.fields | String | Variable | See LEVELONE_EQUITIES Field Definition table below. |

**Request Example:**
```json
{
  "requests": [
    {
      "service": "LEVELONE_EQUITIES",
      "requestid": 1,
      "command": "SUBS",
      "SchwabClientCustomerId": "Someone",
      "SchwabClientCorrelId": "29bdf6d-b9d0-46dd-8786-424e1577bd",
      "parameters": {
        "keys": "SCHW,AAPL,SPY",
        "fields": "0,1,2,3,4,5,8,10"
      }
    }
  ]
}
```

#### Response Field Definitions (Non-Numeric)

| Field Name | Type | Description | Notes |
|---|---|---|---|
| key | String | Usually the symbol | e.g. AAPL |
| delayed | boolean | Whether data is from SIP or NFL | `false` = SIP (real-time); `true` = NFL (delayed or subset of exchanges) |
| assetMainType | String | Asset Type | BOND, EQUITY, ETF, EXTENDED, FOREX, FUTURE, FUTURE_OPTION, FUNDAMENTAL, INDEX, INDICATOR, MUTUAL_FUND, OPTION, UNKNOWN |
| assetSubType | String | Asset sub type | ADR, CEF, COE, ETF, ETN, GDR, OEF, PRF, RGT, UIT, WAR |
| cusip | String | 9-digit CUSIP | e.g. 594918104 |

#### Response Field Definitions (Numeric)

| Field | Field Name | Type | Description | Notes |
|---|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case | |
| 1 | Bid Price | double | Current Bid Price | |
| 2 | Ask Price | double | Current Ask Price | |
| 3 | Last Price | double | Price at which the last trade was matched | |
| 4 | Bid Size | int | Number of shares for bid | Units are "lots" (typically 100 shares). NFL data may return 0 with a non-zero bid price if bid size < 100 shares. |
| 5 | Ask Size | int | Number of shares for ask | See bid size notes. |
| 6 | Ask ID | char | Exchange with the ask | |
| 7 | Bid ID | char | Exchange with the bid | |
| 8 | Total Volume | long | Aggregated shares traded throughout the day, including pre/post market | Volume reset to zero at 7:28am ET. |
| 9 | Last Size | long | Number of shares traded with last trade | Units are shares. |
| 10 | High Price | double | Day's high trade price | Only regular session trades set High. Resets to ZERO at 3:30am ET. |
| 11 | Low Price | double | Day's low trade price | See High Price notes. |
| 12 | Close Price | double | Previous day's closing price | Updated from DB at 3:30 AM ET. |
| 13 | Exchange ID | char | Primary "listing" Exchange | Exchange codes: A=AMEX, Q=NASDAQ, N=NYSE, P=Pacific, 9=Pinks, U=OTCBB, 0=Indices, 3=Mutual Fund |
| 14 | Marginable | boolean | Stock eligible for margin debt collateral | |
| 15 | Description | String | Company, index, or fund name | Loaded from DB once per day at 7:29:50 AM ET. |
| 16 | Last ID | char | Exchange where last trade was executed | |
| 17 | Open Price | double | Day's Open Price | Regular session trades only. Open is ZERO at 3:30am ET. Blank during pre-market. |
| 18 | Net Change | double | Last Price - Close Price | Zero if close is zero. |
| 19 | 52 Week High | double | Highest price in past 52 weeks | Merged from intraday high and 52-week high from DB. |
| 20 | 52 Week Low | double | Lowest price in past 52 weeks | Merged from intraday low and 52-week low from DB. |
| 21 | PE Ratio | double | Price-to-earnings ratio | Uses closing price; does not stream intraday. |
| 22 | Annual Dividend Amount | double | Annual Dividend Amount | |
| 23 | Dividend Yield | double | Dividend Yield | |
| 24 | NAV | double | Mutual Fund Net Asset Value | Loaded after market close. |
| 25 | Exchange Name | String | Display name of exchange | |
| 26 | Dividend Date | String | | |
| 27 | Regular Market Quote | boolean | Is last quote a regular quote | |
| 28 | Regular Market Trade | boolean | Is last trade a regular trade | |
| 29 | Regular Market Last Price | double | Only records regular trade | |
| 30 | Regular Market Last Size | integer | Currently realize/100, only records regular trade | |
| 31 | Regular Market Net Change | double | RegularMarketLastPrice - ClosePrice | |
| 32 | Security Status | String | Current trading status | Normal, Halted, Closed |
| 33 | Mark Price | double | Mark Price | |
| 34 | Quote Time in Long | Long | Last time a bid or ask updated (ms since Epoch) | |
| 35 | Trade Time in Long | Long | Last trade time (ms since Epoch) | |
| 36 | Regular Market Trade Time in Long | Long | Regular market trade time (ms since Epoch) | |
| 37 | Bid Time | long | Last bid time (ms since Epoch) | |
| 38 | Ask Time | long | Last ask time (ms since Epoch) | |
| 39 | Ask MIC ID | String | 4-char Market Identifier Code | |
| 40 | Bid MIC ID | String | 4-char Market Identifier Code | |
| 41 | Last MIC ID | String | 4-char Market Identifier Code | |
| 42 | Net Percent Change | double | Net Percentage Change | NetChange / ClosePrice * 100 |
| 43 | Regular Market Percent Change | double | Regular market hours percentage change | RegularMarketNetChange / ClosePrice * 100 |
| 44 | Mark Price Net Change | double | Mark price net change | e.g. 7.97 |
| 45 | Mark Price Percent Change | double | Mark price percentage change | e.g. 4.2358 |
| 46 | Hard to Borrow Quantity | integer | | -1 = NULL; >= 0 is valid quantity |
| 47 | Hard To Borrow Rate | double | | null = NULL; range = -99,999.999 to +99,999.999 |
| 48 | Hard to Borrow | integer | | -1 = NULL, 1 = true, 0 = false |
| 49 | Shortable | integer | | -1 = NULL, 1 = true, 0 = false |
| 50 | Post-Market Net Change | double | Change in price since end of regular session (typically 4:00pm) | PostMarketLastPrice - RegularMarketLastPrice |
| 51 | Post-Market Percent Change | double | Percent change since end of regular session | PostMarketNetChange / RegularMarketLastPrice * 100 |

**Response Example:**
```json
{
  "data": [
    {
      "service": "LEVELONE_EQUITIES",
      "timestamp": 1714949592301,
      "command": "SUBS",
      "content": [
        {
          "key": "SCHW",
          "delayed": false,
          "assetMainType": "EQUITY",
          "assetSubType": "COE",
          "cusip": "808513105",
          "1": 76.08,
          "2": 76.49,
          "3": 76.44,
          "4": 3,
          "5": 1,
          "8": 5414735,
          "10": 76.47
        },
        {
          "key": "AAPL",
          "delayed": false,
          "assetMainType": "EQUITY",
          "assetSubType": "COE",
          "cusip": "037833100",
          "1": 183.75,
          "2": 183.8,
          "3": 183.8,
          "4": 1,
          "5": 2,
          "8": 163224109,
          "10": 187
        },
        {
          "key": "SPY",
          "delayed": false,
          "assetMainType": "EQUITY",
          "assetSubType": "ETF",
          "cusip": "78462F103",
          "1": 512.3,
          "2": 512.32,
          "3": 511.29,
          "4": 8,
          "5": 1,
          "8": 72756709,
          "10": 512.55
        }
      ]
    }
  ]
}
```

---

### 3.2 LEVELONE_OPTIONS

Refer to LEVELONE_EQUITIES for request and response format. Replace `LEVELONE_EQUITIES` with `LEVELONE_OPTIONS`.

#### Symbol Format

```
RRRRRRYYMMDDsWWWWWddd
```

Where:
- `R` = space-filled root symbol
- `YY` = expiration year
- `MM` = expiration month
- `DD` = expiration day
- `s` = side: C/P (call/put)
- `WWWWW` = whole portion of strike price
- `nnn` = decimal portion of strike price

Example: `AAPL  251219C00200000`

#### Response Field Definitions

| Field | Field Name | Type | Description | Notes |
|---|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case | |
| 1 | Description | String | Company, index, or fund name | Loaded from DB at 3:30am ET daily. |
| 2 | Bid Price | double | Current Bid Price | |
| 3 | Ask Price | double | Current Ask Price | |
| 4 | Last Price | double | Price at which last trade was matched | |
| 5 | High Price | double | Day's high trade price | Regular session only. Resets to zero at 3:30am ET. |
| 6 | Low Price | double | Day's low trade price | See High Price notes. |
| 7 | Close Price | double | Previous day's closing price | Updated from DB at 7:29AM ET. |
| 8 | Total Volume | long | Aggregated contracts traded throughout the day | Volume reset to zero at 3:30am ET. |
| 9 | Open Interest | int | | |
| 10 | Volatility | double | Option Risk/Volatility (Implied) | Reset to 0 at 3:30am ET. |
| 11 | Money Intrinsic Value | double | Value if option were exercised today | In-the-money = positive; out-of-the-money = negative. |
| 12 | Expiration Year | int | | |
| 13 | Multiplier | double | | |
| 14 | Digits | int | Number of decimal places | |
| 15 | Open Price | double | Day's Open Price | Regular session only. Blank during pre-market. Reset to ZERO at 7:28 ET. |
| 16 | Bid Size | int | Number of contracts for bid | |
| 17 | Ask Size | int | Number of contracts for ask | |
| 18 | Last Size | int | Number of contracts traded with last trade | Size in 100's. |
| 19 | Net Change | double | Current Last - Prev Close | If close > 0: change = last - close; else 0. |
| 20 | Strike Price | double | Contract strike price | |
| 21 | Contract Type | char | | |
| 22 | Underlying | String | | |
| 23 | Expiration Month | int | | |
| 24 | Deliverables | String | | |
| 25 | Time Value | double | | |
| 26 | Expiration Day | int | | |
| 27 | Days to Expiration | int | | |
| 28 | Delta | double | | |
| 29 | Gamma | double | | |
| 30 | Theta | double | | |
| 31 | Vega | double | | |
| 32 | Rho | double | | |
| 33 | Security Status | String | Current trading status | Normal, Halted, Closed |
| 34 | Theoretical Option Value | double | | |
| 35 | Underlying Price | double | | |
| 36 | UV Expiration Type | char | | |
| 37 | Mark Price | double | Mark Price | |
| 38 | Quote Time in Long | long | Last quote time (ms since Epoch) | |
| 39 | Trade Time in Long | long | Last trade time (ms since Epoch) | |
| 40 | Exchange | char | Exchange character | e.g. `o` |
| 41 | Exchange Name | String | Display name of exchange | |
| 42 | Last Trading Day | long | Last Trading Day | |
| 43 | Settlement Type | char | | |
| 44 | Net Percent Change | double | Net Percentage Change | e.g. 4.2358 |
| 45 | Mark Price Net Change | double | Mark price net change | e.g. 7.97 |
| 46 | Mark Price Percent Change | double | Mark price percentage change | e.g. 4.2358 |
| 47 | Implied Yield | double | | |
| 48 | isPennyPilot | boolean | | |
| 49 | Option Root | String | | |
| 50 | 52 Week High | double | | |
| 51 | 52 Week Low | double | | |
| 52 | Indicative Ask Price | double | | Only valid for index options (0 for all others). |
| 53 | Indicative Bid Price | double | | Only valid for index options (0 for all others). |
| 54 | Indicative Quote Time | long | Latest time indicative bid/ask updated (ms since Epoch) | Only valid for index options (0 for all others). |
| 55 | Exercise Type | char | | |

---

### 3.3 LEVELONE_FUTURES

Refer to LEVELONE_EQUITIES for request and response format. Replace `LEVELONE_EQUITIES` with `LEVELONE_FUTURES`.

#### Symbol Format

```
'/' + 'root symbol' + 'month code' + 'year code'
```

Month codes:
| Code | Month | Code | Month |
|---|---|---|---|
| F | January | N | July |
| G | February | Q | August |
| H | March | U | September |
| J | April | V | October |
| K | May | X | November |
| M | June | Z | December |

Year code = last two digits of the year.

Common roots: `ES` (E-Mini S&P 500), `NQ` (E-Mini Nasdaq 100), `CL` (Light Sweet Crude Oil), `GC` (Gold), `HO` (Heating Oil), `BZ` (Brent Crude Oil), `YM` (Mini Dow Jones)

#### Response Field Definitions

| Field | Field Name | Type | Description | Notes |
|---|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case | |
| 1 | Bid Price | double | Current Best Bid Price | |
| 2 | Ask Price | double | Current Best Ask Price | |
| 3 | Last Price | double | Price at which last trade was matched | |
| 4 | Bid Size | long | Number of contracts for bid | |
| 5 | Ask Size | long | Number of contracts for ask | |
| 6 | Bid ID | char | Exchange with the best bid | Currently "?" (all quotes are CME) |
| 7 | Ask ID | char | Exchange with the best ask | Currently "?" (all quotes are CME) |
| 8 | Total Volume | long | Aggregated contracts traded throughout the day | |
| 9 | Last Size | long | Number of contracts traded with last trade | |
| 10 | Quote Time | long | Time of last quote (ms since epoch) | |
| 11 | Trade Time | long | Time of last trade (ms since epoch) | |
| 12 | High Price | double | Day's high trade price | |
| 13 | Low Price | double | Day's low trade price | |
| 14 | Close Price | double | Previous day's closing price | |
| 15 | Exchange ID | char | Primary "listing" Exchange | Currently "?" (all quotes are CME) |
| 16 | Description | String | Description of the product | |
| 17 | Last ID | char | Exchange where last trade was executed | |
| 18 | Open Price | double | Day's Open Price | |
| 19 | Net Change | double | Current Last - Prev Close | If close > 0: change = last - close; else 0. |
| 20 | Future Percent Change | double | Current percent change | If close > 0: pctChange = (last - close)/close; else 0. |
| 21 | Exchange Name | String | Name of exchange | |
| 22 | Security Status | String | Trading status of the symbol | Normal, Halted, Closed |
| 23 | Open Interest | int | Total futures contracts not closed or delivered on particular day | |
| 24 | Mark | double | Mark-to-Market value | If lastprice within spread: value = lastprice; else value = (bid+ask)/2 |
| 25 | Tick | double | Minimum price movement | |
| 26 | Tick Amount | double | Minimum amount price of the market can change | Tick * multiplier |
| 27 | Product | String | Futures product | |
| 28 | Future Price Format | String | Display in fraction or decimal format | Format: `<numerator decimals>, <implied denominator>`. Equity futures = "D,D" (pure decimal). Fixed income futures are fractional, e.g. "3,32". See CME docs for examples. |
| 29 | Future Trading Hours | String | Trading hours | Days: 0 = Mon-Fri, 1 = Sunday, 7 = Saturday |
| 30 | Future Is Tradable | boolean | Flag to indicate if this contract is tradable | |
| 31 | Future Multiplier | double | Point value | |
| 32 | Future Is Active | boolean | Indicates if this contract is active | |
| 33 | Future Settlement Price | double | Closing price | |
| 34 | Future Active Symbol | String | Symbol of the active contract | |
| 35 | Future Expiration Date | long | Expiration date of this contract (ms since epoch) | |
| 36 | Expiration Style | String | | |
| 37 | Ask Time | long | Time of last ask-side quote (ms since epoch) | |
| 38 | Bid Time | long | Time of last bid-side quote (ms since epoch) | |
| 39 | Quoted In Session | boolean | Indicates if this contract has quoted during the active session | |
| 40 | Settlement Date | long | Expiration date of this contract (ms since epoch) | |

For fractional pricing display examples: https://www.cmegroup.com/confluence/display/EPICSANDBOX/Fractional+Pricing+-+Display+Examples

---

### 3.4 LEVELONE_FUTURES_OPTIONS

Refer to LEVELONE_EQUITIES for request and response format. Replace `LEVELONE_EQUITIES` with `LEVELONE_FUTURES_OPTIONS`.

#### Symbol Format

```
'.' + '/' + 'root symbol' + 'month code' + 'year code' + 'Call/Put code' + 'Strike Price'
```

Month codes are the same as LEVELONE_FUTURES (F-Z).

Example: `./OZCZ23C565`

#### Response Field Definitions

| Field | Field Name | Type | Description | Notes |
|---|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case | |
| 1 | Bid Price | double | Current Bid Price | |
| 2 | Ask Price | double | Current Ask Price | |
| 3 | Last Price | double | Price at which last trade was matched | |
| 4 | Bid Size | long | Number of contracts for bid | |
| 5 | Ask Size | long | Number of contracts for ask | |
| 6 | Bid ID | char | Exchange with the bid | Currently "?" (all quotes are CME) |
| 7 | Ask ID | char | Exchange with the ask | Currently "?" (all quotes are CME) |
| 8 | Total Volume | long | Aggregated contracts traded throughout the day | |
| 9 | Last Size | long | Number of contracts traded with last trade | |
| 10 | Quote Time | long | Trade time of last quote (ms since epoch) | |
| 11 | Trade Time | long | Trade time of last trade (ms since epoch) | |
| 12 | High Price | double | Day's high trade price | |
| 13 | Low Price | double | Day's low trade price | |
| 14 | Close Price | double | Previous day's closing price | |
| 15 | Last ID | char | Exchange where last trade was executed | Currently "?" (all quotes are CME) |
| 16 | Description | String | Description of the product | |
| 17 | Open Price | double | Day's Open Price | |
| 18 | Open Interest | double | | |
| 19 | Mark | double | Mark-to-Market value | If lastprice within spread: value = lastprice; else value = (bid+ask)/2 |
| 20 | Tick | double | Minimum price movement | |
| 21 | Tick Amount | double | Minimum amount price of the market can change | Tick * multiplier |
| 22 | Future Multiplier | double | Point value | |
| 23 | Future Settlement Price | double | Closing price | |
| 24 | Underlying Symbol | String | Underlying symbol | |
| 25 | Strike Price | double | Strike Price | |
| 26 | Future Expiration Date | long | Expiration date (ms since epoch) | |
| 27 | Expiration Style | String | | |
| 28 | Contract Type | Char | | |
| 29 | Security Status | String | Current trading status | Normal, Halted, Closed |
| 30 | Exchange | char | Exchange character | |
| 31 | Exchange Name | String | Display name of exchange | |

---

### 3.5 LEVELONE_FOREX

Refer to LEVELONE_EQUITIES for request and response format. Replace `LEVELONE_EQUITIES` with `LEVELONE_FOREX`.

#### Symbol Format

Symbols in uppercase, comma-separated. Example: `EUR/USD,USD/JPY,AUD/CAD`

#### Response Field Definitions

| Field | Field Name | Type | Description | Notes |
|---|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case | |
| 1 | Bid Price | double | Current Bid Price | |
| 2 | Ask Price | double | Current Ask Price | |
| 3 | Last Price | double | Price at which last trade was matched | |
| 4 | Bid Size | long | Number of currency pairs for bid | |
| 5 | Ask Size | long | Number of currency pairs for ask | |
| 6 | Total Volume | long | Aggregated currency pairs traded throughout the day | |
| 7 | Last Size | long | Number of currency pairs traded with last trade | |
| 8 | Quote Time | long | Trade time of last quote (ms since epoch) | |
| 9 | Trade Time | long | Trade time of last trade (ms since epoch) | |
| 10 | High Price | double | Day's high trade price | |
| 11 | Low Price | double | Day's low trade price | |
| 12 | Close Price | double | Previous day's closing price | |
| 13 | Exchange | char | | |
| 14 | Description | String | Description of the product | |
| 15 | Open Price | double | Day's Open Price | |
| 16 | Net Change | double | Current Last - Prev Close | If close > 0: change = last - close; else 0. |
| 17 | Percent Change | double | Current percent change | If close > 0: pctChange = (last - close)/close; else 0. |
| 18 | Exchange Name | String | Name of exchange | |
| 19 | Digits | Int | Valid decimal points | |
| 20 | Security Status | String | Trading status of the symbol | Normal, Halted, Closed |
| 21 | Tick | double | Minimum price movement | |
| 22 | Tick Amount | double | Minimum amount price of the market can change | Tick * multiplier from database |
| 23 | Product | String | Product name | |
| 24 | Trading Hours | String | Trading hours | |
| 25 | Is Tradable | boolean | Flag to indicate if this forex is tradable | |
| 26 | Market Maker | String | | |
| 27 | 52 Week High | double | Highest price in past 52 weeks | |
| 28 | 52 Week Low | double | Lowest price in past 52 weeks | |
| 29 | Mark | double | Mark-to-Market value | |

---

## 4. BOOK Services

### 4.1 Book Common

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | NYSE_BOOK, NASDAQ_BOOK, OPTIONS_BOOK |
| command | String | Variable | SUBS, UNSUBS, ADD, VIEW |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | Symbols in uppercase, comma-separated. e.g. `AAPL,TSLA,IBM` |
| parameters.fields | String | Variable | See BOOK Field Definition table below. |

#### Response Field Definitions

**Book Fields:**

| Field | Field Name | Value Type | Description |
|---|---|---|---|
| 0 | Symbol | String | Ticker symbol in upper case |
| 1 | Market Snapshot Time | long | Milliseconds since Epoch — timestamp for the data |
| 2 | Bid Side Levels | Price Levels Array | Bid side price levels |
| 3 | Ask Side Levels | Price Levels Array | Ask side price levels |

**Book Price Levels Sub-Field:**

| Field # | Field Name | Type | Description |
|---|---|---|---|
| 0 | Price | double | Price for this level |
| 1 | Aggregate Size | int | Aggregate size for this price level |
| 2 | Market Maker Count | int | Number of Market Makers at this price level |
| 3 | Array of Market Makers | Array | Market maker sizes for this price level |

**Book Market Makers Sub-Field:**

| Field # | Field Name | Type | Description |
|---|---|---|---|
| 0 | Market Maker ID | String | Market Maker ID |
| 1 | Size | long | Size of the Market Maker for this price level |
| 2 | Quote Time | long | Quote time in milliseconds for this Market Maker's quote |

---

## 5. CHART Services

### 5.1 CHART_EQUITY

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | CHART_EQUITY |
| command | String | Variable | SUBS, UNSUBS, ADD, VIEW |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | Equity symbols in uppercase, comma-separated. e.g. `AAPL,TSLA,IBM` |
| parameters.fields | String | Variable | See CHART_EQUITY Field Definition table below. |

#### Response Field Definitions

| Field | Field Name | Type | Description |
|---|---|---|---|
| 0 | key | String | Ticker symbol in upper case |
| 1 | Open Price | double | Opening price for the minute |
| 2 | High Price | double | Highest price for the minute |
| 3 | Low Price | double | Chart's lowest price for the minute |
| 4 | Close Price | double | Closing price for the minute |
| 5 | Volume | double | Total volume for the minute |
| 6 | Sequence | long | Identifies the candle minute |
| 7 | Chart Time | long | Milliseconds since Epoch |
| 8 | Chart Day | int | |

---

### 5.2 CHART_FUTURES

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | CHART_FUTURES |
| command | String | Variable | SUBS, UNSUBS, ADD, VIEW |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | Futures symbols in uppercase, comma-separated. Same format as LEVELONE_FUTURES. |
| parameters.fields | String | Variable | See CHART_FUTURES Field Definition table below. |

#### Response Field Definitions

| Field | Field Name | Type | Description |
|---|---|---|---|
| 0 | key | String | Ticker symbol in upper case |
| 1 | Chart Time | long | Milliseconds since Epoch |
| 2 | Open Price | double | Opening price for the minute |
| 3 | High Price | double | Highest price for the minute |
| 4 | Low Price | double | Chart's lowest price for the minute |
| 5 | Close Price | double | Closing price for the minute |
| 6 | Volume | double | Total volume for the minute |

---

## 6. SCREENER Services

### 6.1 Screener Common

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | SCREENER_EQUITY, SCREENER_OPTION |
| command | String | Variable | SUBS, UNSUBS, ADD, VIEW |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | `(PREFIX)_(SORTFIELD)_(FREQUENCY)` |
| parameters.fields | String | Variable | See SCREENER Field Definition table below. |

**Key Format:** `(PREFIX)_(SORTFIELD)_(FREQUENCY)`

Prefixes:
- Indices: `$COMPX`, `$DJI`, `$SPX`, `INDEX_ALL`
- Exchanges: `NYSE`, `NASDAQ`, `OTCBB`, `EQUITY_ALL`
- Options: `OPTION_PUT`, `OPTION_CALL`, `OPTION_ALL`

Sort fields: `VOLUME`, `TRADES`, `PERCENT_CHANGE_UP`, `PERCENT_CHANGE_DOWN`, `AVERAGE_PERCENT_VOLUME`

Frequency: `0, 1, 5, 10, 30, 60` minutes (0 = all day)

#### Response Field Definitions

| Index | Field | Type | Description | Values |
|---|---|---|---|---|
| 0 | symbol | String | Symbol used to look up actives, gainers, or losers | Subscribed or requested symbol |
| 1 | timestamp | long | Market snapshot timestamp (ms since Epoch) | |
| 2 | sortField | String | Field to sort on | VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME |
| 3 | frequency | Integer | Frequency of data | 0, 1, 5, 10, 30, 60 minutes |
| 4 | Items | Array | See Items sub-fields below | |

**Items Sub-Fields:**

| Field | Type | Description |
|---|---|---|
| description | String | Description of instrument |
| lastPrice | double | Last trade price (up to 2 decimal places) |
| marketShare | double | Market share percentage (up to 2 decimal places) |
| netChange | double | Net change value (up to 2 decimal places) |
| netPercentChange | double | Net percent change value (up to 4 decimal places) |
| symbol | String | Stock or Option symbol |
| totalVolume | long | Total volume for the day |
| trades | long | Number of trades for the frequency requested |
| volume | long | Volume for the frequency requested |

---

## 7. ACCOUNT Services

### 7.1 ACCT_ACTIVITY

#### Request

| Name | Type | Length | Description |
|---|---|---|---|
| service | String | Variable | ACCOUNT_ACTIVITY |
| command | String | Variable | SUBS, UNSUBS |
| requestid | Integer | Variable | Unique number to identify this request. |
| SchwabClientCustomerId | String | Variable | `schwabClientCustomerId` from GET User Preference endpoint |
| SchwabClientCorrelId | String | Variable | Unique identifier for the transaction or event chain. |
| parameters.keys | String | Variable | Client-provided string that streamer will populate updates with. Only the first key is used if multiple are provided. |
| parameters.fields | String | Variable | `"0"` expected |

**Request Example:**
```json
{
  "requests": [
    {
      "service": "ACCT_ACTIVITY",
      "requestid": "2",
      "command": "SUBS",
      "SchwabClientCustomerId": "Someone",
      "SchwabClientCorrelId": "f308b89-19a7-2d18-4a0a-1c5e7120336",
      "parameters": {
        "keys": "Account Activity",
        "fields": "0,1,2,3"
      }
    }
  ]
}
```

#### Response Field Definitions

| Field | Field Name | Type | Description |
|---|---|---|---|
| seq | Sequence | Integer | Message number. If client reconnects and receives the same seq number, it can choose to ignore the duplicate. |
| key | Key | String | Passed back from the request to identify which subscription this response belongs to. |
| 1 | Account | String | Account number that the activity occurred on. |
| 2 | Message Type | String | Message type that dictates the format of the Message Data field. |
| 3 | Message Data | String | Core data for the message. Either JSON-formatted data describing the update, NULL in some cases, or plain text in case of ERROR. |

---

*© 2026 Charles Schwab & Co., Inc. All rights reserved. Member SIPC.*
