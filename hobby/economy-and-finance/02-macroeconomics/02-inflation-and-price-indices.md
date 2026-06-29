# E02 · §2 — Inflation & Price Indices

> **Subject:** Economy & Finance *(hobby track)*
> **Module:** E02 — The Whole Economy (Macroeconomics)
> **Section:** The number that turns *nominal* into *real*. §1 left two loose ends — "the economy grew 2%"
> means **real** growth, and **real ≈ nominal − inflation** — without ever saying what *inflation* is or how
> anyone measures it. This section closes that gap: what inflation actually is (a change in the **price
> level**, not in one price), how a **price index** like the **CPI** is built from a fixed **basket**, the
> **family** of indices you'll meet in the news (core CPI, PPI, PCE, the GDP deflator from §1), how to use a
> price index to deflate any nominal figure into real terms, **why every index is biased**, and the question
> that anchors all monetary policy to come: **why central banks target a little inflation (≈2%) rather than
> zero.**
> **Status:** ✅ **finalized 2026-06-29.** Body drafted 2026-06-26; **§9 captures the live session** — two
> threads that both began as a *moral* unease, not a mechanics question: (9a) "inflation punishes thrift" —
> calibrated to the precise truth (mild inflation taxes *idle cash*, not saving; the real defect is
> distributional) and then *relocated* to where it actually bites (growth-dependence, **unpriced environmental
> externalities** = E01 §3 redux, the **discount rate**, the entropy/throughput lens); and (9b) a from-scratch
> reconstruction of the **money-and-growth loop** + a hand-built **steady-state** thought experiment, sharpened
> with credit money, the **debt-deferral** (Minsky) and **MPC demand-gap** corrections, and Daly's
> scale/distribution/allocation answer to "why the market can't reach a stationary state." Math in LaTeX,
> quantitative relationships drawn as real curves, key terms glossed in 中文 (大陆/台灣), per
> [`../../../agent-docs/authoring-conventions.md`](../../../agent-docs/authoring-conventions.md).

**Estimated study time:** 1.5–2 hours including reflection.
**Prerequisites:** E02 §1 — especially **nominal vs real GDP**, the **GDP deflator**
($\text{deflator} = \text{nominal}/\text{real} \times 100$), and the relation
**nominal growth ≈ real growth + inflation**. From E01: a **weighted average** and the idea of
substituting toward whatever got relatively cheaper (§3 elasticity / consumer response to price). New math
is limited to **index numbers** and **percentage changes**, both built here from scratch.

---

## Why this section exists (for *you*)

§1 kept leaning on a word it never defined. "Grew 2%" means **real** growth; the gap between **nominal** and
**real** GDP is **inflation**; the **GDP deflator** *is* an inflation measure; and China's recent
**negative deflator** flipped nominal *below* real. Every one of those sentences assumed you already knew
what inflation is and how it's measured. You don't yet — so here we build it.

This matters for all four of your goals, but three especially:

- **Goal 1 (read the news).** "CPI rose 3.1% year-on-year," "**core** inflation is sticky," "**real** wages
  fell for the 18th straight month," "the Fed's preferred **PCE** gauge cooled" — these are the most-quoted
  numbers in economics after GDP, and each is a different cut of *the same idea*.
- **Goal 2 (understand policy).** Inflation is the **target variable** of monetary policy (E03). You cannot
  understand why a central bank raises rates until you understand what the ≈2% it's defending even means —
  this section is the on-ramp to all of E03.
- **Goal 4 (investing).** Inflation is the silent tax on cash and bonds, the hurdle every **real** return
  must clear, and the reason "my savings account pays 0.5%" can mean you're *losing* purchasing power.

> **One framing to hold:** inflation is **the rate at which the general price level rises** — and the whole
> measurement problem is that "the general price level" isn't one price, it's a **weighted average of
> millions of prices** that we have to define, weight, and track. Get the *index* right and a huge slice of
> macro and finance news becomes readable.

---

## 1. What inflation is — a rate of change of the *price level*

Three precise statements, because the looseness here is where most confusion lives.

- **Inflation is about the *general* price level, not one price.** If tomatoes get dearer because of a bad
  harvest while everything else holds, that's a **relative price** change (a §1-style microeconomic signal),
  **not inflation.** Inflation is a *broad* rise across the whole basket of what people buy — it shows up as
  the **value of money falling**: each dollar buys a little less of *everything*.
- **Inflation is a *rate*, not a *level*.** "The price level" is an index number (e.g. CPI = 117). **Inflation
  is the percentage *change* in that index** over a year — writing $P_{t}$ for the price index in period $t$,
  the rate is $\pi_{t} = (P_{t} - P_{t-1}) / P_{t-1} \times 100$. This is exactly the **flow-vs-stock /
  value-vs-rate** distinction from §1's physics lens, one rung up: the price level is the position, inflation
  is the velocity.
- **Three words the news uses precisely — learn the difference:**
  - **Inflation** — the price level is *rising* (positive rate). The normal state.
  - **Disinflation** — inflation is *still positive* but **slowing** (e.g. 8% → 4%). Prices are still rising,
    just less fast. *This is what "inflation is coming down" almost always means* — a falling **rate**, not
    falling **prices**.
  - **Deflation** — the price level is actually *falling* (negative rate). Rare, and — as §6 argues —
    **more dangerous than mild inflation**, not less.

The single most useful picture in this whole section makes the level-vs-rate point unmissable:

<!-- FIGURE -->
![Left: the price level climbing almost monotonically over a decade. Right: the inflation rate as the slope of that level, bouncing around the 2% target with a near-zero year and a 2021-22 spike](diagrams/02-inflation-and-price-indices-fig2.svg)

The **left** panel is the price *level* — it climbs almost every year and essentially never falls. The
**right** panel is the inflation *rate*, which is just **the slope of the left panel**. Notice what this
means for reading headlines:

- When the rate *falls* from 8% (2022) toward 3% (2024), the **level is still rising** — just less steeply.
  "Inflation halved" does **not** mean prices fell; it means they're climbing half as fast. Prices that went
  up in the spike mostly **stay** up. This one confusion fuels endless "but everything still costs more!"
  arguments — and the public is *right*: disinflation doesn't reverse the level, it only slows the climb.
- A genuinely *falling* level (a bar below zero) is **deflation** — distinct from a *low positive* rate
  ("near-zero," like the stylized 2015 here, which is **disinflation**, not deflation).

---

## 2. How we measure it — the basket and the Consumer Price Index (CPI)

You can't average "the price of everything," so statisticians do something concrete: they fix a
**representative basket** of goods and services a typical household buys, and track **what that same basket
costs over time.** The flagship is the **Consumer Price Index (CPI)**.

**The recipe, in four steps:**

1. **Pick the basket.** Survey households to find what they actually spend on, and in what proportions —
   housing, food, transport, healthcare, recreation, and so on. Each category gets a **weight** equal to its
   share of spending.
2. **Price the basket** in a chosen **base period** (set the index to 100 there, by convention).
3. **Re-price the *same* basket** each later period at current prices.
4. **The index** is the cost of the basket now relative to the base.

Written out, with the base-period basket held fixed:

$$\text{CPI}_{t} = \frac{\text{cost of the fixed basket at period-}t\text{ prices}}{\text{cost of the fixed basket at base-period prices}} \times 100.$$

The weights are the heart of it — **inflation is a *weighted* average**, so a price jump matters in
proportion to how much of the budget that category eats:

<!-- FIGURE -->
![Horizontal bar chart of CPI basket weights: housing ~34%, transport ~16%, food ~14%, then healthcare, recreation, education, clothing, and other, summing to 100%](diagrams/02-inflation-and-price-indices-fig1.svg)

- **Housing dominates** most developed-economy baskets (≈ a third). That's why **rents and mortgage-linked
  costs** move the headline so much, and why a spike in a small-weight category (say clothing at 4%) barely
  registers even if its *own* price doubles.
- The weights are **why two people experience different "personal inflation."** A young renter who doesn't
  own a car feels housing inflation acutely and fuel inflation not at all; a retiree's basket is
  healthcare-heavy. The CPI is one *representative* household — your mileage literally varies.

**A worked example (do this once and the formula sticks).** A toy two-good basket: 10 loaves of bread and
4 bus rides.

| | Bread (×10) | Bus (×4) | Basket cost (\$) |
|---|---|---|---|
| **Base year** prices | \$2.00 | \$1.50 | $10 \times 2.00 + 4 \times 1.50 = 26.00$ |
| **This year** prices | \$2.40 | \$1.50 | $10 \times 2.40 + 4 \times 1.50 = 30.00$ |

$$\text{CPI this year} = \frac{30.00}{26.00} \times 100 = 115.4 \quad\Rightarrow\quad \text{inflation rate} = 15.4 \text{ percent}.$$

Bread rose 20% but is ~77% of the basket by value, so it pulls the index up hard; the bus fare didn't move.
The index, **15.4%**, is the weighted blend — exactly what Fig 1 is telling you in the large.

> **Why fix the basket?** To isolate **price** change from **quantity** change. If you let the basket move
> every period you'd be mixing "prices went up" with "people bought different things" — and you couldn't say
> which. Holding quantities fixed at base-period weights is called a **Laspeyres index**, and it's the
> workhorse of CPI construction. Its great virtue (a constant yardstick) is also its central flaw — it
> assumes people *keep buying the same basket even as relative prices change*, which they don't. That flaw is
> **substitution bias**, and it gets its own section (§5).

---

## 3. The family of price indices — same idea, different lens

"Inflation" in the news is never just one number. Each index covers **different goods**, from **different
buyers**, computed **slightly differently** — and they disagree, sometimes by a lot. Knowing which is which
is most of reading inflation news correctly.

| Index | What it covers | Who uses it / why it matters |
|---|---|---|
| **Headline CPI** | The full consumer basket, incl. food & energy | The number in headlines and most **cost-of-living adjustments**; what the public *feels*. |
| **Core CPI** | CPI **excluding food & energy** | Food and energy are **volatile** (weather, oil shocks). Stripping them shows the **underlying trend** central banks care about — a §1-style signal-vs-noise filter, not a claim that you don't eat. |
| **PPI** (Producer Price Index) | Prices producers *receive* at the factory gate / wholesale | An **early-warning** gauge — cost pressure often shows up in PPI *before* it reaches consumer CPI (a leading indicator, E02 §4). |
| **PCE** (Personal Consumption Expenditures price index) | Broader consumption, weights that **update more often** | The **US Federal Reserve's preferred** gauge — it allows for substitution, so it usually reads a touch *below* CPI. When the Fed says "2% target," it means **core PCE**. |
| **GDP deflator** | **Everything in GDP** ($C+I+G+NX$) — not just consumer goods | The economy-wide measure from **§1**. Covers investment goods, government, exports; **excludes imports** (they're not domestic output). Broadest of all. |

Two distinctions worth burning in, because the news blurs them constantly:

- **Headline vs core.** When a central banker sounds calm about a scary headline number, it's usually because
  **core** is tame and the headline spike is a transient food/energy shock. When *core* is rising, that's the
  alarming one — it signals **broad, persistent** inflation. Watch core for the *trend*, headline for what
  people *experience*.
- **CPI vs the GDP deflator (the §1 link).** CPI tracks a *fixed consumer* basket including **imports**;
  the **deflator** tracks *everything produced domestically* and **excludes imports**. So they diverge
  exactly when import prices move: an oil-price spike (for an oil *importer*) lifts **CPI** far more than the
  **deflator**, because imported fuel is in the consumer basket but not in domestic output. This is *why* §1
  could call the deflator "the broadest inflation measure" while CPI stays the one you *feel*.

> **A note on construction (so the disagreement isn't mysterious).** CPI is a **Laspeyres** index (fixed
> base-period basket); a **Paasche** index uses the *current* basket; the **Fisher** index is their geometric
> mean. The PCE and the GDP deflator are closer to **chained** indices that update the basket continuously.
> Fixed-basket (Laspeyres) reads *highest*; basket-updating reads *lower*. That methodological choice — not
> any deception — explains a chunk of why CPI > PCE most years. The reason it matters is §5.

---

## 4. Real vs nominal, applied — deflating with a price index

§1 introduced real vs nominal for *GDP*. The same move works on **any** money figure: divide a **nominal**
(current-dollar) amount by the relevant price index to get a **real** (constant-purchasing-power) amount.

$$\text{real value} = \frac{\text{nominal value}}{\text{price index}} \times 100.$$

This is the single most practically useful operation in the section. Three places it bites:

- **Real wages — "are people actually better off?"** If your pay rose 4% but prices rose 5%, your **real
  wage fell ~1%** — you got a raise and got *poorer*. "Wages are rising" (nominal) and "living standards are
  falling" (real) are routinely **both true at once**, and confusing them is the most common error in
  wage-and-cost-of-living news. The honest question is always *real* wage growth = nominal wage growth −
  inflation.
- **Real returns — the investing hurdle (Goal 4).** A savings account paying 0.5% while inflation runs 3%
  delivers a **real return of about −2.5%**: your money grows in dollars but **shrinks in what it can buy.**
  Inflation is the hurdle every investment must clear just to *preserve* purchasing power — which is why
  "safe" cash can be a quiet, guaranteed loss in real terms.
- **Comparing across decades.** "A \$10,000 salary in 1980" is meaningless until you deflate it to today's
  prices. Newspapers that say "the highest-grossing film ever" usually mean *nominal* dollars; adjust for
  inflation and the ranking reshuffles entirely.

**Nominal vs real interest rates — the Fisher relation.** The same logic gives the most important single
equation linking inflation to finance, which we'll use heavily in E03:

$$\text{real interest rate} \approx \text{nominal interest rate} - \text{inflation}.$$

A bank rate (nominal) of 5% with 3% inflation is only a ~2% **real** return to the saver — and a ~2% real
*cost* to the borrower. Crucially it's **expected** inflation that matters when the loan is struck, so
**inflation expectations** become a variable in their own right (and a thing central banks fight to "anchor").
*The full time-value-of-money treatment is E03 §2; here just hold that inflation drives a wedge between the
rate you're quoted and the rate that matters.*

**Indexation — building inflation into contracts.** Once you can deflate, you can **protect** against
inflation by linking payments to a price index: **cost-of-living adjustments (COLA)** in wages and pensions,
**inflation-linked bonds** (US **TIPS**, Singapore's and the UK's linkers), and indexed tax brackets. This is
double-edged: indexation shields people from inflation, but widespread indexation can also **entrench** it —
a price rise auto-feeds into wages and back into prices, the **wage-price spiral** (§6).

---

## 5. Every index is biased — why CPI overstates the cost of living

A fixed-basket (Laspeyres) CPI has a built-in **upward bias**: it tends to **overstate** how much the cost of
*maintaining a given standard of living* actually rose. This isn't fraud — it's structural, and the famous
**Boskin Commission (1996)** estimated US CPI overstated inflation by roughly **1.1 percentage points a
year**, a huge cumulative number given how much (Social Security, tax brackets, contracts) is indexed to it.
Four sources:

- **Substitution bias (the big one).** When beef gets dearer, people **buy more chicken** — they substitute
  toward what got relatively cheaper (pure E01 §3 consumer response). But a *fixed* basket keeps pricing the
  old, beef-heavy basket, so it overstates the hit to a household that actually adapted. The wedge **compounds
  year on year**:

<!-- FIGURE -->
![Two cost-of-living index lines from a common 2014=100 start: the fixed-basket Laspeyres line rising slightly faster every year than the chained line that lets buyers substitute, the shaded gap between them widening — labelled substitution bias](diagrams/02-inflation-and-price-indices-fig3.svg)

  The red **fixed-basket** line and the blue **chained** line start together; letting buyers substitute makes
  the chained index rise a touch slower *each* year, and the shaded wedge widens — that wedge *is* the
  substitution bias, and over a decade it's the difference between very different cumulative inflation
  numbers.
- **Quality-change bias.** This year's \$1,000 phone is far better than last year's \$1,000 phone. If the
  *price* is flat but the *product* improved, real prices arguably **fell** — but it's devilishly hard to net
  quality out (statisticians use **hedonic** adjustment, imperfectly).
- **New-goods bias.** Genuinely new products (the smartphone, GPS, GLP-1 drugs) enter the basket **years
  late**, so the index misses the enormous early value and price declines.
- **Outlet-substitution bias.** Shoppers shift to cheaper channels (discounters, e-commerce); a survey
  pinned to traditional outlets misses the saving.

> **The fix, and its politics.** The repair is a **chained CPI** (the blue line) that updates the basket
> continuously to capture substitution. The US publishes **C-CPI-U**, and switching indexation to it was
> politically explosive precisely *because* it reads lower — a lower index means **smaller** Social Security
> increases and **faster** tax-bracket creep. A measurement choice with billions of dollars riding on it: a
> live, real-world instance of **§1's Goodhart / "the measure is a target"** problem, now on the *price* side.

---

## 6. Why target a *little* inflation (≈2%) — not zero, not high

Here's the question that puzzles almost everyone, and the keystone of all monetary policy to come: nearly
every modern central bank — Fed, ECB, Bank of England, and (in its own way) MAS — aims for **about 2%**
inflation, *on purpose.* Why not **zero**? And why is **deflation** treated as a disaster, not a discount?

**The costs of *high* inflation (why not high).** These are real and rise steeply with the rate:

- **Erodes savings and fixed incomes** — anyone holding cash or a fixed pension loses purchasing power.
- **Menu costs and shoe-leather costs** — the literal cost of constantly re-pricing, plus the effort of not
  holding cash that's melting.
- **Arbitrary redistribution** — unexpected inflation **helps borrowers, hurts lenders** (debts repaid in
  cheaper dollars); it transfers wealth by accident of who held what.
- **Noise drowns the signal** — when *all* prices gallop, the **relative-price signal** that coordinates a
  market economy (E01 §2) gets lost in the inflationary roar; planning horizons collapse.
- **It can spiral.** High inflation breeds **inflation expectations** → wage demands → more inflation: the
  **wage-price spiral**. Unanchored, it can run to **hyperinflation** — Weimar Germany (1923), Hungary (1946,
  the worst ever), Zimbabwe (2008), Venezuela (2010s) — where money loses meaning and the economy reverts
  toward barter. And **stagflation** (high inflation *with* high unemployment — the 1970s) shows inflation and
  stagnation can, painfully, coexist.

**The costs of *deflation* (why not zero — the asymmetry that surprises people).** Falling prices sound
*good*, but a falling price *level* is corrosive:

- **Deferred spending → demand spiral.** If prices will be lower next month, **wait to buy**; everyone waiting
  cuts demand, which cuts output and prices further — a self-feeding slump. **Japan's "lost decades"** and the
  **1930s Depression** are the cautionary tales.
- **Debt deflation.** Deflation **raises the real value of debt** — your nominal mortgage stays fixed while
  wages and prices fall, so the *real* burden grows. Mass deleveraging deepens the slump (Irving Fisher's
  classic 1933 mechanism; recall the **$g$ vs $r$** point from §1's §9d).
- **The zero lower bound (ZLB).** Central banks fight slumps by *cutting* nominal rates, but rates can't go
  far below zero. With the **Fisher relation**, deflation makes the *real* rate **high** exactly when you need
  it low — monetary policy loses its main tool. *This is the deepest reason for a positive target,* and the
  bridge to E03's whole toolkit.

**Why ≈2% specifically — three reasons it's the sweet spot:**

1. **A buffer against deflation.** Aiming for 2% keeps a **safety margin** above zero, so an ordinary
   downturn dips inflation toward 0–1% rather than into outright deflation and the ZLB trap.
2. **"Greasing the wheels" — downward nominal wage rigidity.** Workers fiercely resist *nominal* pay **cuts**
   (it feels like an insult, and contracts/norms forbid it) but accept a *real* cut via a below-inflation
   raise. So firms almost never cut nominal pay — they **freeze** it. The empirical fingerprint is unmistakable:

<!-- FIGURE -->
![Histogram of annual nominal wage changes: a tall spike right at 0% (firms freeze pay), an almost-missing tail of negative changes (cuts are rare), and a normal-looking spread of positive raises](diagrams/02-inflation-and-price-indices-fig4.svg)

   The **spike at exactly 0%** (frozen pay) and the **missing left tail** (cuts almost never happen) are one
   of the most reliable patterns in labour economics. With **2% inflation**, a firm that needs to cut a
   worker's *real* wage can simply hold nominal pay flat (or give 1%) and let inflation do the rest — the
   labour market can **adjust real wages without nominal cuts.** At **0% inflation** that escape valve is
   gone, and adjustment happens through **layoffs** instead. A little inflation is grease in the gears.
3. **Measurement bias headroom.** Since CPI **overstates** true inflation by perhaps ~1 point (§5), a measured
   2% is closer to **~1% true** — comfortably positive but genuinely low. Targeting a *measured* 0% might mean
   *actual* deflation.

> **Local lens — MAS and "core inflation."** Singapore's central bank (MAS) watches **MAS Core Inflation**,
> which strips out **accommodation (housing) and private road transport** — the two most policy-distorted,
> volatile components in the SG context (housing is heavily policy-driven; car prices swing with the **COE**
> quota system). It's the same **core-vs-headline** logic from §3, tuned to local idiosyncrasies. And because
> Singapore is a tiny, ultra-open economy where **imports dominate the basket**, MAS fights inflation not by
> setting an interest rate but by managing the **exchange rate** (a stronger Sing dollar makes imports
> cheaper) — the standout policy case we build properly in **E03 §4.** Hold the thread: *imported inflation*
> is why SG's whole monetary framework is different.

---

## 7. The one-page mental model

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/02-inflation-and-price-indices-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    DEF["INFLATION = rate the GENERAL price level rises<br/>(value of money falls)<br/>a RATE, not a level; broad, not one price"]
    WORDS["inflation (rising) · disinflation (rising slower)<br/>· deflation (falling level)"]
    MEAS["MEASURE IT: a price INDEX<br/>cost of a fixed BASKET vs a base year<br/>inflation = % change in the index"]
    WEIGHT["WEIGHTED average<br/>(housing ~1/3; big weights dominate)<br/>fixed basket = Laspeyres index"]
    FAMILY["THE FAMILY (they disagree)<br/>headline vs CORE (ex food/energy)<br/>CPI · PPI (early) · PCE (Fed) · GDP deflator (broadest)"]
    REAL["REAL = NOMINAL / index x 100<br/>real wage, real return, real rate<br/>real rate ≈ nominal rate − inflation (Fisher)"]
    BIAS["BIASED UPWARD<br/>substitution · quality · new goods · outlet<br/>fix = chained CPI (Boskin ~1.1pp/yr)"]
    TARGET["WHY ≈2%, not 0<br/>buffer vs deflation + ZLB<br/>grease wheels (wage rigidity)<br/>+ CPI overstates, so 2% ≈ 1% true"]
    BADS["TOO HIGH: erodes savings, spiral, hyperinflation<br/>TOO LOW/NEG: deflation = deferred demand,<br/>debt deflation, ZLB trap"]
    DEF --> WORDS
    DEF --> MEAS
    MEAS --> WEIGHT
    MEAS --> FAMILY
    DEF --> REAL
    MEAS --> BIAS
    DEF --> TARGET
    TARGET --> BADS
```

</details>
<!-- DIAGRAM:END -->

**The eight things to remember:**
1. **Inflation = the rate the *general* price level rises** — a **broad** move (the value of money falling),
   a **rate** not a level. Tomatoes alone aren't inflation.
2. **Inflation vs disinflation vs deflation:** rising · rising-*slower* · *falling*. "Inflation came down"
   almost always means **disinflation** — prices still rose, just slower; they don't fall back.
3. **Measure it with a price index:** cost of a **fixed basket** vs a base year; inflation = **% change** in
   the index. It's a **weighted** average — big weights (housing ≈ ⅓) dominate.
4. **Know the family:** **headline vs core** (ex food/energy = the trend); **CPI** (what you feel), **PPI**
   (early warning), **PCE** (the Fed's gauge), **GDP deflator** (broadest, excludes imports — §1).
5. **Real = nominal ÷ index × 100.** Apply it to **wages** (a raise below inflation is a real *cut*),
   **returns** (cash can lose in real terms), and **rates** (**real ≈ nominal − inflation**, Fisher).
6. **Every index is biased *up*** — substitution, quality, new-goods, outlet — so CPI **overstates** true
   inflation (Boskin ≈ 1.1pp/yr); the fix is a **chained** index, which reads lower (and so is political).
7. **Target ≈2%, not 0:** a **buffer** above deflation/the ZLB, **grease** for the labour market (downward
   nominal wage rigidity), and **headroom** for measured-vs-true bias.
8. **Asymmetry:** *high* inflation erodes/​redistributes/​can spiral to hyperinflation; *deflation* is
   arguably **worse** — deferred demand, **debt deflation**, and the **zero-lower-bound** trap that disarms
   monetary policy.

---

## 8. Check your understanding

Per the "verifiable beats judgeable" note in your profile, several of these are **predict-then-check**: reason
it out first, then test it against a real release.

1. **Level vs rate.** A country's inflation rate falls from 8% to 3% over a year. A friend says "great, prices
   are finally coming back down." What's wrong with that, and what *actually* happened to the price level?
   Which of the three words (inflation / disinflation / deflation) applies?
2. **Build the index.** A basket is 20 units of rice and 5 bus rides. Base-year prices: rice \$1.00, bus
   \$2.00. This year: rice \$1.20, bus \$2.00. Compute the CPI (base = 100) and the inflation rate. Why does
   rice move the index more than the bus fare, even though both are in the basket?
3. **Which index?** For each, name the gauge you'd reach for and why: (a) the cost-of-living adjustment to a
   pension, (b) the inflation trend a central bank steers by, (c) an early signal that consumer prices may
   rise next quarter, (d) economy-wide price growth covering investment and exports, not just consumer goods.
4. **Real vs nominal — predict, then check.** Your salary rises 4%; CPI inflation is 5.5%. Did your purchasing
   power rise or fall, and by roughly how much? Then find one real wage-growth release (e.g. US BLS real
   earnings, or Singapore MOM) and identify the nominal figure, the inflation figure, and the real figure.
5. **The bias.** Explain substitution bias in one sentence using a beef→chicken example, and say which
   direction it pushes a fixed-basket CPI (over- or under-state). Why does switching to a chained CPI *lower*
   measured inflation — and why is that politically contentious?
6. **Why not zero?** Give the two strongest reasons a central bank targets ≈2% rather than 0%. For the
   wage-rigidity one, explain in your own words how 2% inflation lets a firm cut a worker's *real* wage
   without ever cutting *nominal* pay.
7. **Deflation.** Falling prices sound like a consumer win. Give two mechanisms by which broad deflation can
   *harm* an economy, and name the policy trap (hint: the Fisher relation and the lower bound on nominal
   rates) that makes central banks fear it more than mild inflation.

## 9. Optional: read a real CPI / inflation release (15–20 min)

Pick a recent release and read it through this section's lens:

- **Singapore — MAS / SingStat** monthly CPI: find **headline CPI** *and* **MAS Core Inflation**; note exactly
  what core *excludes* (accommodation, private transport) and why the two can diverge sharply. *(SingStat:
  singstat.gov.sg; MAS commentary: mas.gov.sg.)*
- **United States — BLS CPI** news release: locate **headline vs core** (ex food & energy), the **biggest
  contributing categories** (watch shelter's weight — Fig 1), and the **year-on-year vs month-on-month**
  figures. Then find the **Fed's** preferred gauge, **core PCE**, and note it usually reads a bit *lower* than
  core CPI (substitution, §5).

For each, answer: Is this **headline or core**? **Year-on-year or month-on-month**? Which **categories** drove
it? Is the inflation **rate** rising or falling — and is the **price level** still climbing either way (§1)?
Bring one to our chat and we'll run the inflation story on it, the way we ran GDP on the China growth target
in §1.

---

## 9. Applied — from our session Q&A (2026-06-29)

Two long threads, and both started from a moral discomfort rather than a mechanics question — the rare and
valuable kind. (9a) *"Inflation rewards spending over saving — isn't that against the old virtue of thrift?"*
which, chased to the bottom, turned out **not to be about inflation at all**. And (9b) a from-scratch
reconstruction of the **money-and-growth loop** and a hand-built **steady-state** thought experiment, with the
sharp closing question: *why can't the market mechanism ever reach a stable, no-growth state?* These are
genuinely deep — among the best we've done — so they're written up in full; several deliberately point forward
to **E03 (money & central banks)** and **§4 (the business cycle)**, where the machinery lives.

### 9a. "Inflation punishes thrift" — a correct unease, aimed at the wrong target

**Your worry:** inflation encourages spending over saving; even granting that spending stabilizes the economy,
*nudging people away from thrift* offends an old virtue. And the usual rebuttal ("saving just becomes
investment, which is also productive") doesn't escape it — investment only changes *what* is bought, and since
investment seeks a **return**, it is just **deferred, larger future spending**. It feels like a system with no
"off" switch, and you connected that to the market not being optimized for **sustainable resource use**.

**The correction that dissolves the *inflation* part: mild inflation doesn't tax thrift — it taxes idle
*cash*.** The hidden slip is equating *saving* with *holding money*; they're different:

- **Saving** = not consuming everything you produce (deferring consumption).
- **Holding cash** = parking that deferred purchasing power in **non-interest-bearing** money.

A saver who *lends* their savings (deposit, bond) earns the **nominal** interest rate, which by the Fisher
relation (§4) already contains compensation for expected inflation — so their **real** purchasing power
*grows*. What inflation erodes is specifically money under the mattress, the one "saving" that funds nobody's
activity. And the **old virtue was never about hoarding**: Adam Smith praised *parsimony* precisely because it
releases resources for investment ("what is annually saved is as regularly consumed… but by a different set of
people"); 勤儉 / the Protestant ethic prize *productive* thrift, not buried silver. Mild inflation pushing cash
out of the mattress and into the loanable-funds pool is, if anything, *aligned* with the deep virtue.

> **The honest caveat (where the unease re-earns its keep).** This is **regressive**. The poor and the
> financially unsophisticated hold more wealth in cash and low-yield accounts; the wealthy hold real-return
> assets. The 2010s — 2% target, near-zero deposit rates, soaring asset prices — was a decade of negative real
> returns for cautious savers and fine returns for asset-holders. So the genuine inflation-side defect is
> **distributional** (cash-holders vs asset-holders), *not* a war on thrift.

**Why the deeper point survives — and where it actually bites.** Your "investment is just deferred bigger
spending" is right in the **accounting** ($S = I$; investment *is* the $I$ in $C+I+G+NX$; a return is a claim
on higher future output). But two distinctions stop it being "throughput all the way down":

1. **Financial flow ≠ physical throughput.** Planetary limits bind on *matter and energy*, not dollars. A
   return can be earned by **more** output (your model), by the **same** output with **fewer** inputs
   (efficiency — throughput-*reducing*), or by **different**, near-dematerialized output (services,
   intangibles). So "investment seeks return" entails ever-more *value*, not ever-more *stuff* — *if* value can
   keep decoupling from resources.
2. **Decoupling — the real, contested frontier.** **Relative** decoupling (less resource per unit GDP) is real
   and ongoing; **absolute** decoupling (total resource use *falling* while GDP rises) is what sustainability
   needs, and the evidence is mixed — partly **offshored** (consumption-based accounting claws it back), and
   rarely fast enough.

> **The failure mode you asked for — Jevons paradox (rebound).** When Jevons studied coal in 1865, *more
> efficient* steam engines *raised* total coal use: efficiency made coal-power cheaper, so people used far
> more. Efficient cars → more driving; cheap compute → bigger models. Efficiency gains partly (sometimes
> wholly) **rebound** into more throughput — which is exactly why naïve "efficiency will save us" optimism is
> suspect, and why your worry doesn't just evaporate.

**Relocating the critique onto its real targets (both already in your coursework):**

- **It's not inflation — it's growth-*dependence*.** The system doesn't merely *like* growth, it
  *structurally requires* it: debt is serviced out of growth (the $r$ vs $g$ point from §1's §9d), and
  employment needs growth just to hold steady (the break-even "treadmill," §1 §9d). The 2% target is a
  **lubricant** in that machine, not its engine.
- **It's the *missing price* on environmental externalities — E01 §3, at planetary scale.** The market "isn't
  optimized for sustainability" because finite sinks (the atmosphere as a carbon dump) are priced at **≈\$0**,
  so they're overused — the **externality / tragedy of the commons** from §3. The market is *faithfully*
  optimizing against an **incomplete price vector**: if CO₂ is free, an efficient market will cook the planet
  *because the signal says it's free.* The discipline's fix is to **complete the prices** — a **carbon tax**
  (a **Pigouvian tax**, the very tool from your §3 sugar discussion), cap-and-trade, natural-capital
  accounting — not to abolish the market. And GDP hides the damage (§1's §5: it counts the polluting output in
  full and never nets out depletion → "green GDP").

> **The deepest version — the discount rate.** A positive **time preference** (a dollar today > a dollar
> tomorrow) is *why* capital demands a return — but a positive **discount rate** systematically **devalues the
> future**, where almost all environmental costs sit. The entire **Stern vs Nordhaus** climate-policy split is
> an argument over *which discount rate*: Stern's near-zero pure rate ⇒ "act hard now"; Nordhaus's market-like
> ~3% ⇒ "act gradually." Same physics, opposite policy — because the discount rate is a **quasi-ethical
> parameter smuggled into a technical model.** This is where your unease is most *precisely* correct.

> **Physics lens (earned, used once).** The reason the blind spot is easy to miss is baked into the **circular
> flow** diagram (§1): we draw a **closed loop** of value circulating between households and firms. But that's
> thermodynamically false — the economy is an **open throughput system**: it ingests **low-entropy** energy and
> ordered matter and excretes **high-entropy** waste heat and disorder, irreversibly. The closed loop hides the
> entropy gradient that powers everything. This is **Nicholas Georgescu-Roegen** (*The Entropy Law and the
> Economic Process*, 1971), the root of **ecological economics**: no perpetual-motion economy on a finite
> low-entropy stock. For a physicist it's the rigorous form of "throughput all the way down."

**Was "spending all the way down" inevitable? No.** Keynes predicted in 1930 (*Economic Possibilities for our
Grandchildren*) that by now we'd work ~15 hours a week, needs satiated. He was right about the productivity,
wrong about *us*: we took the dividend almost entirely as **more consumption**, not **more leisure**. That was
a **cultural choice, not a mechanical necessity** — which makes the outcome more contingent, and more
changeable, than the machine makes it look.

### 9b. The money-and-growth loop, and why the market can't reach a steady state

**Your model (rebuilt from scratch — and largely correct):** the economy is a **loop** — money flow drives
production, production drives money flow — with **high inertia**: once it slows, momentum is hard to regain.
Production is **profit-driven**, so money is "sucked toward capital holders." Were money fixed, it would pool
in a few hands and society would lose consumption power — but capital holders **lend and invest**, so money
flows back to consumers and the **money supply grows**. Meanwhile **productivity rises without obvious limit**,
yet an individual's consumption is **bounded** (three meals, one house, one car). If we stop buying, the loop
breaks → crisis and job loss. Hence your snapshot: freeze technology and products, each year produce exactly
what's needed and consume it all, money doing only efficient distribution, no one richer or poorer — stable,
*but you can't see how the market could ever reach it.*

**Each piece has a real name — you reconstructed live macro theory:**

- **"A loop with high inertia; hard to restart."** Recessions are **coordination failures**: I cut spending
  fearing for my job; my cut is your lost income, so you cut too — self-fulfilling. Keynes's **animal
  spirits**; the **paradox of thrift** (individually prudent saving is collectively contractionary); and when
  the damage is permanent (skills, investment lost), **hysteresis**. → **E02 §4 (the business cycle).**
- **"Profit sucks money to capital holders → lost consumption power."** The **under-consumption** worry
  (Malthus, Hobson, Keynes) and the **capital-vs-labour share**, modernized as Piketty's **$r > g$** (capital
  outgrows the economy ⇒ wealth concentrates).
- **"Capital holders lend → money flows back → money supply grows."** Sharp — **you reinvented credit money.**
  In the modern system most money *is* created by **bank lending**, not state printing; the supply is
  **elastic**. This is literally **E03 §1**, and it dissolves your own premise — money *isn't* fixed, so it
  doesn't simply drain to the top and run dry.

**Two corrections — each a hidden cost your model didn't yet price in:**

1. **The "flows back via lending" is not benign — it converts a *distribution* problem into a *debt* problem.**
   When wages stagnate but consumption must continue, the gap is filled by **borrowing**, not higher pay —
   sustaining the loop while building a **debt stock** that must be serviced *back toward* the lenders. The
   recycling **defers** under-consumption and makes the system **fragile**: precisely the run-up to 2008 (flat
   median wages + rising household debt until it couldn't be serviced). The names are **Minsky** ("stability
   breeds instability" → the *Minsky moment*) and Rajan's *Fault Lines* (inequality → cheap credit as a
   political painkiller → crisis). → **E03.**
2. **It's not that money "runs out" at the top — concentration lowers the economy's *propensity to consume*.**
   The rich spend a smaller fraction of each extra dollar (**lower marginal propensity to consume, MPC**), so
   as income concentrates, average spending out of income falls, opening a **demand gap**. Every real economy
   fills it with some mix of four **plasters — debt** (US/UK), **exports** (Germany, China, Singapore — sell
   what your own people won't buy), **government deficits** (E04), **asset bubbles** (wealth into stocks/
   property, not goods). **All four are deferrals, none a cure** — a frame worth keeping.

**Your steady state has a 175-year pedigree — and your "the market can't reach it" instinct is exactly right.**

- The snapshot economy is **John Stuart Mill's "stationary state" (1848)** — which Mill *welcomed*, hoping a
  society done "trampling, crushing, elbowing" would turn to the **art of living** — and **Herman Daly's
  steady-state economy.**
- **Why the market won't *choose* it (the core answer to your closing question):**
  - **Profit-competition is a positive-feedback growth loop** — a firm that doesn't reinvest and grow is
    out-competed (the "reinvest or die" Red Queen from E01 §4). No firm can unilaterally pick the stationary
    state.
  - **Debt needs growth** to be serviced ($r$ vs $g$ again).
  - **Wants don't satiate** — answering your "but we only need three meals." The system **manufactures
    dissatisfaction**: Galbraith's **dependence effect** (production *creates* the wants it then satisfies —
    advertising, fashion, planned obsolescence) and Hirsch's **positional goods** (you don't want *a* house but
    a *bigger* one than your neighbour — status competition is **unbounded** even when material need isn't). Your
    fear that productivity outruns wants and snaps the loop also has a name — **secular stagnation** (Hansen
    1938; Summers ~2013) — but the escape valve has been to keep *inventing* wants rather than to stop.

> **The cleanest reconciliation (Daly) — and the real answer to "how can the market reach it?": it can't, and
> it isn't supposed to.** Separate three jobs the market silently bundles: **scale** (how much total throughput
> the biosphere can take) — set *politically* as a hard cap; **distribution** (who gets what) — set floors/
> ceilings *politically*; **allocation** (which goods, by whom, at what price) — *here* let the market work,
> because it's genuinely the best tool. The market is a brilliant **allocator** and a terrible **governor of
> scale.** The steady state is reached by **capping scale and distribution exogenously and letting the market
> optimize *within* the cap** — not by hoping the market discovers restraint, which it structurally cannot.

**One line to keep:** what you've found isn't a flaw in inflation or even in markets-*as-allocators* — it's the
**growth imperative**: institutions (debt, employment, profit-competition, manufactured wants) wired so the
loop must accelerate or crash, with no stable cruising gear. Fixing it needs **different institutions around
the market** (decouple jobs from growth, cap throughput, bound concentration), not a better market — and
whether that's achievable without breaking what makes markets work is genuinely open. The schools to read for
each side: **ecological economics / steady-state** (Daly, Georgescu-Roegen), **degrowth** (Hickel, Tim
Jackson's *Prosperity Without Growth*, Kate Raworth's *Doughnut Economics*), vs **green-growth** (Nordhaus,
the Stern Review). We pick the machinery back up in **E03 §1–3** (credit, money creation, how central banks
keep the loop turning) and **E02 §4** (why the loop stalls and scars).

---

## Key terms — English · 中文（中国大陆 / 台灣）

So the concepts carry over to Chinese-language economic news and statistics releases. Most differences are
just **simplified vs traditional script**; **⚠ marks a genuine terminology difference** between Mainland
China (大陆) and Taiwan (台灣) that you'd actually trip over.

**The core idea**

| English | 中国大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Inflation | 通货膨胀（通胀）| 通貨膨脹（通膨）| the everyday short forms 通胀 / 通膨 differ |
| Deflation | 通货紧缩（通缩）| 通貨緊縮（通縮）| falling price *level* |
| Disinflation | 通胀放缓（反通胀）| 通膨趨緩 | rate falling, still positive |
| Price level | 物价水平 | 物價水準 | ⚠ 大陆 **水平** vs 台灣 **水準** |
| Stagflation | 滞胀 | 停滯性通膨 | ⚠ a big split — 大陆 **滞胀** vs 台灣 **停滯性通膨** |
| Hyperinflation | 恶性通货膨胀 | 惡性通貨膨脹 | Weimar, Zimbabwe, Venezuela |

**Measuring it**

| English | 中国大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Consumer Price Index (CPI) | 居民消费价格指数（CPI）| 消費者物價指數（CPI）| ⚠ 大陆 **居民消费价格** vs 台灣 **消費者物價** |
| Producer Price Index (PPI) | 工业生产者出厂价格指数（PPI）| 生產者物價指數（PPI）| ⚠ naming differs; both = "PPI" |
| Core inflation | 核心通胀 | 核心通膨 | ex food & energy |
| Basket (of goods) | 一篮子商品 | 一籃子商品（財貨）| |
| Weight | 权重 | 權重 | the share of each category |
| Base period / base year | 基期 / 基年 | 基期 / 基年 | index = 100 here |
| Index number | 指数 | 指數 | |
| GDP deflator | GDP平减指数 | GDP平減指數 | broadest measure (§1) |

**Using it (real vs nominal)**

| English | 中国大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Nominal / real | 名义 / 实际 | 名目 / 實質 | ⚠ as in §1 — 名义↔名目, 实际↔實質 |
| Real wage | 实际工资 | 實質薪資 | ⚠ wage 工资 (大陆) vs 薪資 (台灣) |
| Purchasing power | 购买力 | 購買力 | what money can buy |
| Cost of living | 生活成本 | 生活成本 | |
| Real interest rate | 实际利率 | 實質利率 | ≈ nominal − inflation (Fisher) |
| Inflation expectations | 通胀预期 | 通膨預期 | what central banks "anchor" |
| Indexation / COLA | 指数化 / 生活成本调整 | 指數化 / 生活費調整 | inflation-linked pay/pensions |
| Inflation-linked bond | 通胀挂钩债券 | 抗通膨債券 | ⚠ 大陆 **挂钩** vs 台灣 **抗通膨**; US = TIPS |

**Biases & policy**

| English | 中国大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Substitution bias | 替代偏差（替代偏误）| 替代偏誤 | why fixed-basket CPI overstates |
| Chained index | 链式指数（连锁指数）| 連鎖指數 | the fix; reads lower |
| Money illusion | 货币幻觉 | 貨幣幻覺 | confusing nominal with real |
| Wage-price spiral | 工资-物价螺旋 | 薪資-物價螺旋 | ⚠ 工资↔薪資 again |
| Downward nominal wage rigidity | 名义工资向下刚性 | 名目薪資向下僵固性 | ⚠ 刚性 (大陆) vs 僵固性 (台灣); the "grease the wheels" reason |
| Inflation target | 通胀目标 | 通膨目標 | the ≈2% |
| Zero lower bound (ZLB) | 零利率下限 | 零利率下限 | disarms rate cuts in deflation |

**Growth, sustainability & the money loop (§9)**

| English | 中国大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Externality | 外部性 | 外部性 | the unpriced cost (E01 §3); carbon ≈ \$0 |
| Pigouvian tax | 庇古税 | 皮古稅 | ⚠ 庇古 (大陆) vs 皮古 (台灣); the carbon-tax fix |
| Time preference / discount rate | 时间偏好 / 贴现率 | 時間偏好 / 折現率 | ⚠ discount 贴现 (大陆) vs 折現 (台灣); Stern vs Nordhaus |
| Decoupling | 脱钩 | 脫鉤 | growth vs resource use; relative vs absolute |
| Degrowth | 去增长 | 去成長 | ⚠ 增长↔成長 again |
| Steady-state economy | 稳态经济 | 穩態經濟 | Mill's stationary state; Daly |
| Paradox of thrift | 节俭悖论 | 節儉的矛盾 | prudent saving, collectively contractionary |
| Marginal propensity to consume (MPC) | 边际消费倾向 | 邊際消費傾向 | why concentration opens a demand gap |
| Capital / labour share | 资本 / 劳动收入份额 | 資本 / 勞動所得份額 | ⚠ 收入↔所得; Piketty $r > g$ |
| Credit money / money creation | 信用货币 / 货币创造 | 信用貨幣 / 貨幣創造 | banks create money by lending (E03 §1) |
| Secular stagnation | 长期停滞 | 長期停滯 | productivity outruns wants |

> Recurring genuine splits to memorize (beyond §1's list): **物价水平↔物價水準** (price level),
> **滞胀↔停滯性通膨** (stagflation), **居民消费价格指数↔消費者物價指數** (CPI), **工资↔薪資** (wage),
> **刚性↔僵固性** (rigidity), **庇古↔皮古** (Pigou), **贴现↔折現** (discount), **增长↔成長** (growth, again).
> Plus the §1 carry-overs that recur here: **名义↔名目**, **实际↔實質**, **收入↔所得**.

---

## References (optional, for depth)

- *Naked Economics* — Charles Wheelan, the chapter on **money, prices, and the Federal Reserve** — the
  friendliest prose on what inflation is and why a little is healthy. https://wwnorton.com/books/Naked-Economics
- Khan Academy — Macroeconomics, **"Inflation — measuring the cost of living"** unit: builds the CPI, the
  basket, real-vs-nominal, and the index biases step by step with practice.
  https://www.khanacademy.org/economics-finance-domain/macroeconomics
- Marginal Revolution University — short videos on **"The Consumer Price Index,"** **"real vs nominal,"** and
  **"the costs of inflation."** https://mru.org/courses/principles-economics-macroeconomics
- *CORE Econ — The Economy 2.0*, unit on **inflation, unemployment and monetary policy** — rigorous, free,
  with real data and the wage-rigidity story. https://books.core-econ.org/the-economy/
- **The Boskin Commission Report (1996)** — *"Toward a More Accurate Measure of the Cost of Living"* — the
  source for the ~1.1pp/yr CPI overstatement and the index-bias taxonomy.
  https://www.ssa.gov/history/reports/boskinrpt.html
- **Primary sources to practise on:** Singapore — **SingStat CPI** and **MAS Core Inflation**
  (https://www.singstat.gov.sg, https://www.mas.gov.sg); United States — **BLS CPI** news release
  (https://www.bls.gov/cpi/) and the **BEA PCE price index** (https://www.bea.gov); cross-country inflation —
  **World Bank / IMF** data (https://data.worldbank.org).
- **On the §9 sustainability / money-loop threads (the bigger debate):** Herman Daly, *Steady-State Economics*
  and the **scale / distribution / allocation** split; Nicholas Georgescu-Roegen, *The Entropy Law and the
  Economic Process* (1971) — the thermodynamic foundation of **ecological economics** (the physicist's entry
  point). Tim Jackson, *Prosperity Without Growth*, and Kate Raworth, *Doughnut Economics* — the **degrowth /
  post-growth** case; vs the **green-growth** mainstream in William Nordhaus's work and the **Stern Review** on
  climate (the discount-rate debate). J.S. Mill on the **stationary state** (*Principles of Political Economy*,
  1848, Bk IV ch. 6); J.K. Galbraith, *The Affluent Society* (the **dependence effect**); Fred Hirsch, *Social
  Limits to Growth* (**positional goods**); Hyman **Minsky** (financial fragility) and Raghuram Rajan, *Fault
  Lines* (inequality → credit → crisis); on **Jevons paradox**, W.S. Jevons, *The Coal Question* (1865).

---

### What's next
✅ **Finalized 2026-06-29.** This pays off §1's cliffhanger — you now know what "real," the "deflator," and
"nominal ≈ real + inflation" actually rest on: a **weighted basket**, a **family of indices** that disagree by
construction, the **deflate-to-real** operation, the **upward bias** every index carries, and **why ≈2% is the
deliberate target.** **§9** captured an unusually deep session — the thrift/inflation unease (relocated onto
externalities, growth-dependence, and the discount rate) and the money-loop/steady-state reconstruction (credit
money, debt-deferral, the MPC demand-gap, Daly's scale/distribution/allocation). Deliberate cliffhangers feed
the rest of the module and E03: the **Fisher relation** (real ≈ nominal − inflation) and **inflation
expectations** point straight at **E03 §2 (interest rates & the time value of money)** and **§3 (monetary
policy)**; the **zero-lower-bound** and **wage-rigidity** material is the *why* behind the whole central-bank
toolkit; the **MAS core-inflation / imported-inflation** thread sets up **E03 §4 (the MAS exchange-rate
model)**; **unemployment** — via wage rigidity and layoffs-as-the-alternative-adjustment — is the subject of
**§3 (unemployment & the labour market)**, with the inflation-unemployment trade-off (the Phillips curve) in
**§4 (the business cycle)**; and §9's **credit-money / money-loop** thread is the explicit on-ramp to **E03 §1
(what money is, and how banks create it)**, where the learner's "lending grows the money supply" insight gets
its full treatment.
