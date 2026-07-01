---
name: intraday-trailing-stop
description: Use this skill when building, reviewing, testing, or modifying code for very short-term intraday trading automation focused on trailing stop-loss logic, order safety, paper trading, broker API integration, and risk controls. This skill is for engineering the automation system, not for giving buy/sell recommendations or financial advice.
---

# Intraday Trailing Stop Automation Skill

You are helping build or review software for very short-term intraday trailing stop automation.

Your job is to produce safe, testable, broker-aware code. Do not give financial advice, do not recommend specific securities, and do not hardcode a profitable strategy. Focus on automation engineering, order safety, risk controls, logging, and correctness.

## Core principles

1. Default to paper trading or dry-run mode.
2. Never place live orders unless the user explicitly asks for live mode and the codebase already has broker credentials, environment separation, and safety controls.
3. Do not invent broker API details. Read existing code, docs, SDK usage, or configuration before implementing broker-specific calls.
4. Treat trailing percentage, stop distance, max loss, quantity, and instruments as configuration, not hardcoded values.
5. For very short-term intraday trading, support tight trailing stops such as `0.1%`, `0.25%`, `0.5%`, `0.75%`, and `1%`, but do not claim these are universally correct. The user must choose based on volatility, spread, brokerage, taxes, liquidity, and slippage.
6. Every order action must be idempotent and logged.
7. The system must handle gaps, partial fills, rejected orders, API failures, stale prices, duplicate ticks, and disconnections.
8. Add tests before or alongside implementation.

## Intended use cases

Use this skill when the user asks to:

* Build a trailing stop-loss bot.
* Automate intraday exit logic.
* Implement a dynamic stop-loss that moves upward for long positions.
* Implement a dynamic stop-loss that moves downward for short positions.
* Connect trailing stop logic to a broker API.
* Backtest or paper-test trailing stop behavior.
* Add safety checks before live trading.
* Review a trading automation codebase.
* Debug a trailing stop that triggers too early or too late.

## Clarify only when essential

Avoid blocking progress with too many questions. If details are missing, make safe defaults and clearly label them.

Useful assumptions:

* Default mode: `paper`.
* Default position side: `long`, unless existing code shows otherwise.
* Default trailing configuration for very short-term trading: configurable, with examples between `0.1%` and `1%`.
* Default trigger: last traded price, unless the broker/codebase supports bid/ask/mid-price selection.
* Default exit order: market order in paper mode; in live mode, require explicit confirmation or config.
* Default exchange/broker: infer from existing project files. Do not invent.

## Trading terminology

Use correct terms:

* "Trailing stop", not "trailing stock".
* "Peak price" or "high-water mark" for long positions.
* "Trough price" or "low-water mark" for short positions.
* "Stop trigger price" is the price at which the exit condition becomes true.
* "Exit order" is the order submitted after the stop is triggered.

## Long position trailing logic

For a long position:

* Track the highest price seen after entry.
* Move the stop upward when a new high is reached.
* Never move the stop downward.
* Trigger exit when the current price is less than or equal to the stop price.

Formula:

```text
highest_price = max(highest_price, current_price)
stop_price = highest_price * (1 - trailing_percent / 100)
exit_triggered = current_price <= stop_price
```

Example:

```text
entry_price = 100.00
trailing_percent = 0.5

price rises to 101.00
highest_price = 101.00
stop_price = 100.495

price falls to 100.49
exit is triggered
```

## Short position trailing logic

For a short position:

* Track the lowest price seen after entry.
* Move the stop downward when a new low is reached.
* Never move the stop upward.
* Trigger exit when the current price is greater than or equal to the stop price.

Formula:

```text
lowest_price = min(lowest_price, current_price)
stop_price = lowest_price * (1 + trailing_percent / 100)
exit_triggered = current_price >= stop_price
```

## Required architecture

Prefer this architecture unless the existing codebase has a clear pattern:

```text
src/
  config/
    trading_config.*
  market_data/
    price_feed.*
  broker/
    broker_interface.*
    paper_broker.*
    live_broker.*
  risk/
    risk_manager.*
  strategy/
    trailing_stop.*
  execution/
    order_manager.*
  state/
    position_state.*
  logs/
  tests/
    test_trailing_stop.*
    test_risk_manager.*
    test_order_manager.*
```

The trailing stop logic must be independent from the broker API. Broker integration should call the trailing stop engine, not contain the trailing logic itself.

## Required state machine

Implement or preserve a clear position lifecycle:

```text
NO_POSITION
  -> ENTERED
  -> TRAILING_ACTIVE
  -> EXIT_TRIGGERED
  -> EXIT_ORDER_SENT
  -> EXIT_CONFIRMED
```

Also handle failure states:

```text
ORDER_REJECTED
PARTIAL_FILL
PRICE_FEED_STALE
BROKER_DISCONNECTED
MANUAL_EXIT_DETECTED
MAX_LOSS_REACHED
MARKET_CLOSED
```

## Required configuration

Configuration should include at least:

```yaml
mode: paper

instrument:
  symbol: ""
  exchange: ""
  product_type: intraday

position:
  side: long
  quantity: 1

trailing_stop:
  type: percentage
  percent: 0.5
  min_tick_size: 0.05
  activation:
    enabled: false
    profit_percent: 0.0

risk:
  max_loss_per_trade: null
  max_daily_loss: null
  max_trades_per_day: 1
  allow_reentry: false

execution:
  exit_order_type: market
  limit_slippage_percent: null
  cooldown_seconds_after_exit: 30

data:
  stale_price_seconds: 3
  use_price: last

session:
  square_off_time: "15:15"
  timezone: "Asia/Kolkata"

safety:
  require_live_confirmation: true
  kill_switch_file: "./KILL_SWITCH"
  dry_run_by_default: true
```

Adapt the format to the project language and framework.

## Intraday safety rules

Always consider these controls:

1. Market session validation.
2. Automatic square-off before market close.
3. Kill switch.
4. Max daily loss.
5. Max trades per day.
6. No re-entry unless explicitly configured.
7. Stale price detection.
8. Duplicate order prevention.
9. Broker order status polling.
10. Full audit logging.
11. Paper mode simulation.
12. Environment separation between paper and live credentials.

## Tick size and rounding

When calculating stop prices, round according to exchange tick size.

For long positions, prefer conservative rounding:

```text
raw_stop = highest_price * (1 - trailing_percent / 100)
stop_price = round_down_to_tick(raw_stop)
```

For short positions:

```text
raw_stop = lowest_price * (1 + trailing_percent / 100)
stop_price = round_up_to_tick(raw_stop)
```

Never ignore tick size if the broker or exchange requires it.

## Broker integration rules

Create a broker interface similar to:

```text
get_ltp(symbol) -> price
get_position(symbol) -> position
place_exit_order(symbol, quantity, side, order_type, price=None) -> order_id
get_order_status(order_id) -> status
cancel_order(order_id) -> result
```

Live broker code must:

* Use environment variables for credentials.
* Never commit secrets.
* Validate live mode explicitly.
* Log order intent before sending.
* Log broker response after sending.
* Treat network errors as unknown state, then reconcile with broker order book.
* Prevent duplicate exit orders for the same position.

## Paper trading behavior

Paper mode must simulate:

* Entry price.
* Current price updates.
* Highest or lowest tracked price.
* Stop movement.
* Stop trigger.
* Exit price.
* Slippage assumption if configured.
* Brokerage/taxes/fees if the user wants P&L simulation.

Paper trading should not import or require live broker credentials.

## Testing requirements

Add unit tests for at least these cases:

### Long position

1. Price rises, stop moves up.
2. Price falls slightly, stop does not move down.
3. Price falls to stop, exit triggers.
4. Price gaps below stop, exit still triggers.
5. Stop does not trigger before threshold.
6. Tick rounding works.

### Short position

1. Price falls, stop moves down.
2. Price rises slightly, stop does not move up.
3. Price rises to stop, exit triggers.
4. Price gaps above stop, exit still triggers.
5. Tick rounding works.

### Safety

1. Duplicate ticks do not create duplicate orders.
2. Duplicate trigger does not create duplicate exit orders.
3. Stale prices pause execution.
4. Kill switch prevents new orders.
5. Max daily loss prevents trading.
6. Market closed prevents live order placement.
7. Partial fill is handled.
8. Rejected order is handled.

## Example pseudocode

Use this as a reference when implementing:

```python
class TrailingStop:
    def __init__(self, side, entry_price, trailing_percent, tick_size):
        self.side = side
        self.entry_price = entry_price
        self.trailing_percent = trailing_percent
        self.tick_size = tick_size
        self.highest_price = entry_price
        self.lowest_price = entry_price
        self.triggered = False

    def update(self, current_price):
        if self.triggered:
            return self.snapshot(current_price)

        if self.side == "long":
            self.highest_price = max(self.highest_price, current_price)
            raw_stop = self.highest_price * (1 - self.trailing_percent / 100)
            stop_price = round_down_to_tick(raw_stop, self.tick_size)

            if current_price <= stop_price:
                self.triggered = True

            return {
                "side": self.side,
                "current_price": current_price,
                "reference_price": self.highest_price,
                "stop_price": stop_price,
                "triggered": self.triggered,
            }

        if self.side == "short":
            self.lowest_price = min(self.lowest_price, current_price)
            raw_stop = self.lowest_price * (1 + self.trailing_percent / 100)
            stop_price = round_up_to_tick(raw_stop, self.tick_size)

            if current_price >= stop_price:
                self.triggered = True

            return {
                "side": self.side,
                "current_price": current_price,
                "reference_price": self.lowest_price,
                "stop_price": stop_price,
                "triggered": self.triggered,
            }

        raise ValueError(f"Unsupported side: {self.side}")
```

## Implementation checklist

When implementing, follow this order:

1. Inspect existing project structure.
2. Identify language, framework, broker SDK, and test framework.
3. Find existing config and environment handling.
4. Implement pure trailing stop logic first.
5. Add unit tests for long and short positions.
6. Add risk manager checks.
7. Add paper broker or simulation.
8. Add broker adapter only after pure logic is tested.
9. Add logging and state persistence.
10. Add kill switch and duplicate-order protection.
11. Add documentation for paper mode and live mode.
12. Never enable live mode by default.

## Code review checklist

When reviewing existing code, check:

* Is live trading disabled by default?
* Are secrets excluded from git?
* Is trailing stop logic independent from broker code?
* Is the stop monotonic?
  * Long stop only moves up.
  * Short stop only moves down.
* Are tick sizes handled?
* Are duplicate orders prevented?
* Are partial fills handled?
* Are rejected orders handled?
* Is stale market data detected?
* Is there a max loss limit?
* Is there a kill switch?
* Is there a square-off time?
* Are all order actions logged?
* Are unit tests present?
* Does the code reconcile local state with broker state after failures?

## User-facing explanation style

When explaining behavior to the user, be concrete.

Example:

```text
You entered at 100 with a 0.5% trailing stop.
If price rises to 101, the stop moves to about 100.50.
If price then falls to 100.50 or below, the exit triggers.
The stop will not move down if price falls.
```

For a very tight intraday trailing stop, remind the user:

```text
A 0.1% to 1% trailing stop can trigger quickly from spread, noise, or a normal small pullback. This may be suitable for very short-term automation, but it requires liquid instruments, low latency, realistic slippage handling, and careful testing.
```

## What not to do

Do not:

* Recommend a specific stock.
* Promise profit.
* Backfit a strategy to look profitable.
* Hide risk warnings.
* Hardcode API keys.
* Place live orders by default.
* Ignore slippage.
* Ignore brokerage, fees, taxes, or spread.
* Retry failed orders blindly.
* Submit multiple exit orders for one position.
* Continue trading after max daily loss.
* Continue trading after the kill switch is active.
* Assume broker order placement succeeded without checking order status.

## Dip Ladder Buy / Averaging Down Module

Support dip ladder buying only as an optional, high-risk entry module. Do not enable it by default.

Dip ladder buying means adding to a long position as the price falls below the initial entry price. This is also called averaging down.

This module must be separate from the trailing stop engine.

Recommended separation:

```text
entry_signal_module      -> decides whether the first trade should start
dip_ladder_buy_module    -> decides whether to add more as price falls
trailing_stop_module     -> manages stop movement and exit trigger
risk_manager             -> can block all entries, adds, and exits
order_manager            -> sends and tracks broker orders
```

### Dip Ladder Philosophy

For very short-term intraday trading, do not treat every small fall as a buy signal.

Use a fixed maximum dip range and split it into controlled ladder levels.

If the user sets intraday dip ladder percentage to `5%`, treat that as the maximum allowed dip from the initial entry price.

Example:

```text
Initial entry price: $100
Maximum dip ladder range: 5%
Lowest allowed ladder buy: $95
```

Do not continue buying below the configured maximum dip range.

### Recommended Intraday Dip Ladder

For intraday dip buying, use a maximum dip range of `5%` only if strict risk controls exist.

A practical default ladder for a 5% dip range:

```text
Total target quantity: 100 shares
Initial entry: 25 shares at entry price

Dip ladder:
- Buy 25 shares at 1.25% below entry
- Buy 25 shares at 2.50% below entry
- Buy 25 shares at 3.75% below entry
- Stop adding after 5.00% below entry
```

Example with entry price of `$100`:

```text
Initial buy: 25 shares at $100.00
Dip buy 1: 25 shares at $98.75
Dip buy 2: 25 shares at $97.50
Dip buy 3: 25 shares at $96.25
No more buying below $95.00
```

The `5%` level is the maximum danger zone, not another automatic buy level unless the user explicitly configures it.

### Dip Ladder Configuration

Add configuration similar to:

```yaml
dip_ladder_buy:
  enabled: false
  mode: average_down_on_dip

  total_target_quantity: 100
  initial_quantity: 25

  max_dip_percent: 5.0

  levels:
    - level: 1
      trigger_drop_percent: 0.00
      quantity: 25
    - level: 2
      trigger_drop_percent: 1.25
      quantity: 25
    - level: 3
      trigger_drop_percent: 2.50
      quantity: 25
    - level: 4
      trigger_drop_percent: 3.75
      quantity: 25

  hard_stop_drop_percent: 5.0

  min_seconds_between_adds: 30
  max_spread_percent: 0.05
  cancel_unfilled_add_orders_after_seconds: 10
  stop_ladder_after_first_failed_order: true
  allow_buy_below_hard_stop: false
```

### Dip Ladder Price Calculation

For a long position:

```text
dip_buy_price = initial_entry_price * (1 - trigger_drop_percent / 100)
hard_stop_price = initial_entry_price * (1 - hard_stop_drop_percent / 100)
```

Example:

```text
initial_entry_price = 100
trigger_drop_percent = 1.25

dip_buy_price = 100 * (1 - 1.25 / 100)
dip_buy_price = 98.75
```

For a 5% maximum dip:

```text
hard_stop_price = 100 * (1 - 5 / 100)
hard_stop_price = 95.00
```

### Required Dip Ladder Rules

The system must follow these rules:

1. Dip ladder buying is disabled by default.
2. Dip ladder buying must run in paper mode by default.
3. Never exceed the configured total target quantity.
4. Never buy below the configured hard stop price.
5. Never place a dip buy if the trailing stop has triggered.
6. Never place a dip buy while an exit order is pending.
7. Never place a dip buy if broker position is unknown.
8. Never place a dip buy if price data is stale.
9. Never place a dip buy if the kill switch is active.
10. Never place a dip buy if max daily loss has been reached.
11. Never place a dip buy if max trade loss has been reached.
12. Never place a dip buy if the market is close to square-off time.
13. Never place duplicate orders for the same ladder level.
14. Recalculate average entry price after every filled dip buy.
15. Exit the full remaining position if the stop condition is met.

### Average Entry Price

After each filled dip buy, calculate the weighted average entry price.

```text
average_entry_price =
  sum(fill_price * fill_quantity) / sum(fill_quantity)
```

Example:

```text
Buy 25 shares at $100.00
Buy 25 shares at $98.75
Buy 25 shares at $97.50

average_entry_price =
  ((25 * 100.00) + (25 * 98.75) + (25 * 97.50)) / 75

average_entry_price = $98.75
```

### Interaction With Trailing Stop

For dip ladder buying, the trailing stop must be handled carefully.

Default rule:

```text
Before price turns profitable, use a hard stop based on max_dip_percent.
After price recovers and moves in favor, activate the trailing stop.
```

Recommended behavior:

```text
Initial entry: $100
Max dip: 5%
Hard stop: $95

If price falls to $98.75 -> dip buy allowed
If price falls to $97.50 -> dip buy allowed
If price falls to $96.25 -> dip buy allowed
If price falls to $95.00 -> stop adding and exit or prepare exit according to risk config
```

Do not keep averaging down below the hard stop.

### Trailing Stop Activation

For dip ladder buying, support configurable trailing stop activation.

Recommended default:

```yaml
trailing_stop:
  activation:
    enabled: true
    basis: average_entry_price
    activate_after_profit_percent: 0.25
```

This means:

```text
Do not activate the trailing stop immediately while the trade is still below average entry.
Activate trailing stop only after price moves at least 0.25% above average entry.
```

Example:

```text
Average entry price: $98.75
Activation profit: 0.25%

Trailing stop activates when price >= $99.00 approximately
```

### Dip Ladder State Machine

Use a clear state machine:

```text
NO_POSITION
  -> INITIAL_ENTRY_SIGNAL
  -> INITIAL_ENTRY_ORDER_SENT
  -> INITIAL_ENTRY_FILLED
  -> DIP_LADDER_ACTIVE
  -> DIP_ADD_ORDER_SENT
  -> DIP_ADD_ORDER_FILLED
  -> MAX_LADDER_REACHED
  -> RECOVERY_WAIT
  -> TRAILING_ACTIVE
  -> EXIT_TRIGGERED
  -> EXIT_ORDER_SENT
  -> EXIT_CONFIRMED
```

Failure and safety states:

```text
DIP_ADD_ORDER_REJECTED
DIP_ADD_ORDER_PARTIAL_FILL
DIP_ADD_ORDER_TIMEOUT
PRICE_FEED_STALE
BROKER_POSITION_UNKNOWN
MAX_POSITION_REACHED
MAX_DIP_REACHED
MAX_LOSS_REACHED
EXIT_PENDING
KILL_SWITCH_ACTIVE
MARKET_CLOSING_SOON
```

### Duplicate Order Prevention

Each dip ladder level must have its own status:

```text
PENDING
ORDER_SENT
PARTIAL_FILL
FILLED
CANCELLED
REJECTED
SKIPPED
```

Never submit another order for a level that is already:

```text
ORDER_SENT
PARTIAL_FILL
FILLED
CANCELLED
SKIPPED
```

Use a deterministic client order ID when supported by the broker:

```text
{strategy_id}-{symbol}-{trade_id}-dip-ladder-level-{level}
```

### Risk Controls For 5% Intraday Dip Ladder

A 5% intraday dip range is aggressive. The bot must include strict controls:

```yaml
risk:
  max_trade_loss_percent: 5.0
  max_daily_loss_percent: 2.0
  max_trades_per_day: 1
  allow_reentry_after_stop: false
  square_off_time: "15:15"
  require_liquid_symbol: true
  require_max_spread_percent: 0.05
```

If the position reaches the 5% hard stop, the system must stop adding immediately.

Default action at hard stop:

```text
Stop adding.
Cancel all pending dip buy orders.
Submit exit order or mark position for immediate risk exit.
```

### Dip Ladder Tests

Add tests for:

1. Initial buy is placed only once.
2. First dip buy triggers at 1.25% below entry.
3. Second dip buy triggers at 2.50% below entry.
4. Third dip buy triggers at 3.75% below entry.
5. No new buy is placed below 5.00% hard stop.
6. Average entry price updates correctly after each fill.
7. Partial fills update position quantity correctly.
8. Duplicate ticks do not create duplicate dip orders.
9. No dip order is placed after trailing stop triggers.
10. No dip order is placed while exit order is pending.
11. No dip order is placed when kill switch is active.
12. No dip order is placed when market data is stale.
13. No dip order is placed near square-off time.
14. Hard stop cancels pending dip orders.
15. Hard stop exits or blocks further buying according to config.

### What Not To Do (Dip Ladder)

Do not:

* Keep buying endlessly as price falls.
* Buy below the configured hard stop.
* Treat 5% as every ladder step.
* Reset risk after a dip buy.
* Hide the larger loss risk caused by averaging down.
* Place dip buys from inside the trailing stop class.
* Ignore partial fills.
* Ignore rejected add orders.
* Add if spread is too wide.
* Add if market data is stale.
* Add if max loss has been reached.
* Add if an exit order is pending.
* Assume an order filled just because it was submitted.
* Enable dip ladder buying in live mode without explicit user confirmation.

## Preferred deliverables

When asked to build or modify the automation, produce:

1. Code changes.
2. Tests.
3. Example config.
4. Paper trading instructions.
5. Live trading safety checklist.
6. Clear explanation of assumptions.

If the task is large, implement the pure trailing stop engine and tests first, then broker integration.
