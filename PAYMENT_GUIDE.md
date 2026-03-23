# Payment Guide — Connect YOUR Payment Provider

**BeehiveOfAI works out of the box in free test mode. When you're ready for real money, this guide tells you exactly what to use and how to connect it.**

---

## How Payments Work in BeehiveOfAI

There are only two money flows to connect:

1. **Money In** — A Beekeeper buys Nectar credits (Honey Drop / Jar / Pot packages)
2. **Money Out** — A Queen or Worker requests a Honey Harvest (payout of accumulated earnings)

The platform handles everything in between — credits, balances, revenue splits, transaction history. Your payment provider just plugs into those two points.

---

## Which Provider Should You Use?

### Quick Answer by Country

| Your Country | Use This | Why |
|-------------|----------|-----|
| **USA** | Stripe Connect | Best APIs, best marketplace features, easiest setup |
| **Canada** | Stripe Connect | Full support, same as US |
| **UK** | Stripe Connect | Full support |
| **Germany, France, Netherlands** | Stripe Connect | Full EU support |
| **Rest of Western Europe** | Stripe Connect | Supported in 30+ EU countries |
| **Eastern Europe (EU members)** | Stripe Connect | Most EU countries covered |
| **Australia / New Zealand** | Stripe Connect | Full support |
| **Japan** | Stripe Connect | Full support |
| **Singapore** | Stripe Connect | Full support |
| **India** | Razorpay Route | Dominant choice for India, supports UPI |
| **Brazil** | Stripe Connect or Mercado Pago | Mercado Pago better for local payment methods |
| **Mexico** | Stripe Connect or Mercado Pago | Both work, Mercado Pago has cash payments (OXXO) |
| **Rest of Latin America** | Mercado Pago | Covers Argentina, Chile, Colombia, Peru, Uruguay |
| **Nigeria** | Paystack or Flutterwave | Both have split payments, Paystack has better DX |
| **Kenya, Uganda, Tanzania** | Flutterwave | M-PESA support is critical |
| **South Africa** | Paystack | Full support |
| **Rest of Africa** | Flutterwave | Broadest African coverage (34+ countries) |
| **Southeast Asia** | Xendit | Covers Indonesia, Philippines, Malaysia, Thailand, Vietnam, Singapore |
| **UAE** | Stripe Connect | Available in UAE |
| **Other Middle East** | PayPal or Stripe Atlas | Options are limited — see note below |
| **Anywhere else** | See "Not in the list?" below | |

### Not in the List?

If your country isn't listed above, you have two options:

1. **PayPal** — Available in 200+ countries for receiving payments. Payouts are more limited but work in 95+ countries. The BeehiveOfAI code already includes a working PayPal integration you can use directly.

2. **Stripe Atlas** — For $500, Stripe will create a US company (LLC) on your behalf, giving you access to Stripe Connect from anywhere. This works from 140+ countries. Be aware: you'll have US tax filing obligations.

---

## Provider Details

### Stripe Connect (Recommended for most countries)

**What it is:** Stripe's marketplace product. Handles collecting payments, splitting funds, and paying out sellers.

**Fees:**
- US: 2.9% + $0.30 per transaction
- EU/UK: 1.5% + €0.25 per transaction
- Plus: 0.25% + $0.25 per payout to connected accounts
- Plus: $2/month per active connected account

**Setup:**
1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Enable Connect in your Stripe Dashboard
3. Get your API keys (publishable key + secret key)

**Marketplace features:** Split payments, seller onboarding with identity verification, automated payouts, tax reporting (US 1099s), chargeback protection.

---

### PayPal (Included — Working Code)

**What it is:** BeehiveOfAI already includes a complete, tested PayPal integration. If you're in a PayPal-supported country, you can use it directly.

**Fees:**
- US: 2.99% + $0.49 per transaction
- International: ~4.4% + fixed fee
- Payouts (Standard Payouts): 2% per payout (capped)

**Setup:**
1. Create a PayPal Business account at [paypal.com](https://www.paypal.com)
2. Create an app at [developer.paypal.com](https://developer.paypal.com)
3. Request Payouts API access (for the money-out side)
4. Set environment variables:
   ```bash
   # Windows:
   set PAYPAL_CLIENT_ID=your_client_id
   set PAYPAL_CLIENT_SECRET=your_secret
   set PAYPAL_MODE=sandbox     # change to "live" for real money

   # Linux/Mac:
   export PAYPAL_CLIENT_ID=your_client_id
   export PAYPAL_CLIENT_SECRET=your_secret
   export PAYPAL_MODE=sandbox
   ```

That's it — the code handles the rest. No AI assistant needed for PayPal.

---

### Razorpay Route (India)

**What it is:** India's leading payment processor, with marketplace split payment features.

**Fees:**
- Domestic cards/UPI: ~2% + GST
- International: ~3% + GST

**Supports:** Credit/debit cards, UPI, net banking, wallets (Paytm, PhonePe), EMI.

---

### Mercado Pago (Latin America)

**What it is:** The payment arm of MercadoLibre. Dominant in Latin America.

**Fees:** ~3-5% per transaction (varies by country and method).

**Countries:** Argentina, Brazil, Chile, Colombia, Mexico, Peru, Uruguay.

**Supports:** Credit/debit cards, bank transfers, and cash payments (OXXO in Mexico, boleto in Brazil) — essential for Latin American customers who may not have credit cards.

---

### Flutterwave (Africa — 34+ Countries)

**What it is:** Pan-African payment platform with marketplace split features.

**Fees:** 1.4% - 3.8% depending on transaction type and country.

**Supports:** Cards, bank transfers, mobile money (M-PESA, MTN), USSD.

---

### Paystack (Nigeria, Ghana, South Africa, Kenya)

**What it is:** Stripe-backed African payment processor. Known for developer-friendly APIs.

**Fees:** ~1.5% + fixed fee (local), ~3.9% + fixed fee (international). Capped in Nigeria.

**Supports:** Cards, bank transfers, mobile money, USSD.

---

### Xendit (Southeast Asia)

**What it is:** Southeast Asian payment platform.

**Fees:** ~2-3% + fixed fee depending on country and method.

**Countries:** Indonesia, Philippines, Malaysia, Thailand, Vietnam, Singapore.

**Supports:** Cards, e-wallets (GCash, DANA, OVO, GrabPay), direct debit.

---

## How to Connect Any Provider (The Vibe Coding Way)

BeehiveOfAI is designed so that connecting a new payment provider is straightforward. The existing PayPal code (`paypal_service.py`) serves as a clear reference pattern.

**Here's what you do:**

1. **Look at `paypal_service.py`** — It has these key functions:
   - `is_configured()` — checks if API credentials are set
   - `create_order()` — creates a checkout session (money in)
   - `capture_order()` — confirms the payment after the buyer approves
   - `send_payout()` — sends money to a worker/queen (money out)

2. **Open your AI coding assistant** (Claude Code, Cursor, GitHub Copilot, etc.)

3. **Give it this prompt** (customize for your provider):

   > I have a BeehiveOfAI instance and I want to connect [Stripe/Razorpay/etc.] for payments.
   >
   > Look at `paypal_service.py` — it has 4 key functions: `is_configured()`, `create_order()`, `capture_order()`, and `send_payout()`. Create a similar file called `[provider]_service.py` that implements the same interface using [Stripe/Razorpay/etc.] APIs.
   >
   > Then update `app.py` to import and use the new service instead of `paypal_service`.
   >
   > My API keys are: [your keys here]
   >
   > The platform sells Nectar credit packages ($18, $40, $75) and pays out workers when their Honeycomb Balance reaches the threshold.

4. **The AI assistant will:**
   - Read the existing PayPal code to understand the pattern
   - Create a new service file for your provider
   - Update `app.py` to use it
   - This typically takes 10-15 minutes

5. **Test in sandbox/test mode first** — Every major provider has a sandbox. Test the full flow before going live.

---

## The Two-Mode Architecture

BeehiveOfAI is designed with a graceful fallback:

- **If payment credentials are set** → Real payments (your provider handles money)
- **If payment credentials are NOT set** → Free test mode (purchases are free, no real money moves)

This means you can always run the platform without a payment provider. Test mode is fully functional — users can register, buy credits (free), submit jobs, and process results. Only the actual money flow is simulated.

This is useful for:
- Development and testing
- Internal company deployments (where the "payment" is just internal credits)
- Demos and presentations

---

## Fee Comparison Summary

| Provider | Receiving | Payouts | Currency Conversion | Best For |
|----------|----------|---------|-------------------|----------|
| Stripe Connect | 2.9% + $0.30 | 0.25% + $0.25 | ~1% | US, EU, UK, AU, JP |
| PayPal | 2.99% + $0.49 | 2% (capped) | 2.5% | Widest global reach |
| Razorpay | ~2% + GST | Varies | N/A (INR) | India |
| Mercado Pago | 3-5% | Varies | Built-in | Latin America |
| Flutterwave | 1.4-3.8% | Varies | Varies | Africa |
| Paystack | 1.5% + fixed | Via transfer | Varies | Nigeria, Ghana, SA, Kenya |
| Xendit | 2-3% + fixed | Varies | Varies | Southeast Asia |

---

## Questions?

If you're not sure which provider to use, check:
1. Does the provider operate in YOUR country? (Check their website's country list)
2. Can the provider pay out to OTHER people? (Not all can — some only receive)
3. Does the provider have a sandbox/test mode? (Essential for development)

For the full story behind why we built the payment system this way — including the micro-transaction problem, the bundling solution, and the lessons learned from trying every provider on Earth — read Chapter 8 of [The Distributed AI Revolution](https://github.com/strulovitz/TheDistributedAIRevolution).
