# Daily Reading — 2026-08-11

*A "National Geographic / Discovery" pair — one story from the **career** world (the security of the agents you build and use), one from the **hobby** world (condensed-matter physics and the materials that store data). Not course material; the wider, stranger, more current world around what you do.*

**Today's two stories:**
1. 🪤🤖 **The most dangerous vulnerability in software has no patch, and last week it was ranked number one for the third year running — while barely appearing in any incident database.** On **4 August 2026** OWASP (Open Worldwide Application Security Project) published the third edition of its Top 10 for LLM (large language model) Applications, and **prompt injection sits at `LLM01` again**. What makes that ranking strange is OWASP's own admission, reported the next day: on raw public incident counts prompt injection *"wouldn't even make the top 10."* The reason it tops the list anyway is that it is not a bug in anything. It is a **missing boundary**. Every other injection class in the history of computing — SQL, shell, XSS (cross-site scripting) — was eventually killed by *separating the control channel from the data channel*; the prepared statement is a hole the database knows about in advance, and nothing you put in that hole can ever become syntax. **An LLM has no such hole.** The system prompt, your question, and the web page the agent just fetched arrive as one flat sequence of tokens with no field anywhere that means *this part is data and may never act*. Three and a half years after the attack was named, the honest state of the art is: detectors that catch 61–72% of injections catch **0–10%** the moment the attacker knows the detector is there; eight published defences were tested adaptively and **all eight fell**; and the two approaches that actually hold both work by **giving up capability**.
2. 🧲🔬 **Magnetism turned out to have a third kind, and nobody noticed for a century.** In **July 2026** the European Physical Society awarded its **Europhysics Prize** — the top condensed-matter prize in Europe — to Libor Šmejkal, Jairo Sinova and Tomáš Jungwirth for the discovery of **altermagnetism**, a class of magnetic order that did not exist as a concept in 2021. Textbooks had two: ferromagnets, whose spins add up, and antiferromagnets, whose spins cancel. An altermagnet **cancels like an antiferromagnet and splits electron bands like a ferromagnet**, which was supposed to be impossible, and it does it because its two spin sublattices are related by a *rotation* rather than a translation. The payoff is exactly the trade-off that magnetic storage has been stuck behind for thirty years: ferromagnets are easy to read but leak a stray field onto the neighbouring bit; antiferromagnets are dense, immune and a **thousand times faster**, but nearly unreadable. An altermagnet is meant to be both. And then the twist that makes this a real science story rather than a press release: **the field's own flagship material, RuO₂, may not be magnetic at all.** Neutrons put its ordered moment at about $0.05\thinspace\mu_{B}$ per ruthenium atom; muons put it at $4.8\times10^{-4}$ — a hundredfold disagreement — and the emerging consensus in a **2026 review** is that the bulk crystal is non-magnetic while **epitaxial strain in an ultrathin film** may be manufacturing the effect.

> **Why this pair.** The last three readings kept landing on the same shape — *a substrate swap under a system that cannot stop* — so it is worth saying plainly that **today's pair is a different shape**. Both stories are **taxonomy failures**: cases where the map was missing a category, and the missing category turned out to be where all the action was. Security spent thirty years building a clean binary — *trusted instruction* versus *inert data* — and then shipped a machine to which a third thing happens: **content that is neither, and that the machine cannot tell apart from either.** Physics spent a century with a clean binary — *spins add* versus *spins cancel* — and missed a third case sitting in materials people had already synthesised, because nobody had asked which symmetry operation connects the two sublattices. In both, the missing category was invisible not because the evidence was scarce but because **the classification scheme had no slot to put it in**, and in both, drawing the slot instantly reorganised what everyone thought they were looking at. They differ in the direction of the work: story 1 is a boundary that was **never drawn and now must be**, and every honest fix costs capability; story 2 is a boundary that was **drawn wrong and is being redrawn**, and the redrawing hands you capability for free. One more thing worth flagging up front, because it is the part of story 2 that is closest to your own decade: the RuO₂ fight is **not** a bulk-physics fight. It is a **thin-film, strain and defect fight** — different labs, different growth, different answers, and a review that ends by demanding *impeccably characterised* material before anyone declares victory. That is a failure-analysis problem wearing a condensed-matter hat.

---

## 1. 🪤 The bug that cannot be patched

🔗 **Start here:** [Prompt injection remains the biggest LLM risk, despite limited incidents — Infosecurity Magazine (5 Aug 2026)](https://www.infosecurity-magazine.com/news/prompt-injection-llm-risk/) · [Prompt injection tops the 2026 OWASP GenAI / LLM Top Ten — SD Times](https://sdtimes.com/security/prompt-injection-tops-2026-owasp-genai-llm-top-ten-vulnerabilities/) · [The lethal trifecta for AI agents — Simon Willison (16 Jun 2025)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
🔗 **The "why now":** [Prompt injection still drives most agentic AI security failures in production — Help Net Security (11 Jun 2026)](https://www.helpnetsecurity.com/2026/06/11/owasp-prompt-injection-ai-security-failures/) · [A deep dive into the OWASP Top 10 for Agentic Applications 2026](https://neuraltrust.ai/blog/owasp-top-10-for-agentic-applications-2026) · [Disrupting the first reported AI-orchestrated cyber espionage campaign — Anthropic (13 Nov 2025)](https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf)
🔗 **Go deeper:** [*Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents* — Zhan et al., arXiv 2503.00061](https://arxiv.org/abs/2503.00061) · [*Defeating Prompt Injections by Design* (CaMeL) — Debenedetti et al., arXiv 2503.18813](https://arxiv.org/abs/2503.18813) · [*Design Patterns for Securing LLM Agents against Prompt Injections* — Beurer-Kellner et al., arXiv 2506.08837](https://arxiv.org/abs/2506.08837) · [*AgentDojo*: a dynamic environment for evaluating attacks and defences — arXiv 2406.13352](https://arxiv.org/abs/2406.13352)

![A colossal brass and glass reading machine in a dim archive hall, a conveyor of plain paper documents feeding into its single glowing lens, with a few sheets glowing crimson and ghostly translucent hands rising out of those pages to reach for the machine's control levers.](images/11-the-unpatchable-bug-and-the-third-magnet-1.png)

*The whole problem in one picture: the machine was built to **read** the documents. Some of the documents are written to be **obeyed**, and nothing in the machine's design distinguishes the two. — Illustration, generated locally (ComfyUI + Z-Image Turbo); a generic metaphor, no real system or product depicted.*

<details>
<summary>Image prompt (source of truth)</summary>

> A colossal ornate brass and glass reading machine in a dim archive hall, a wide river of plain white paper documents flowing on a conveyor into its single glowing lens-eye, and among the plain pages a few sheets glow poisonous crimson while ghostly translucent red hands rise out of those pages and reach for the machine's brass control levers, cinematic conceptual illustration, dramatic low angle, cold blue-grey palette with one poisonous crimson accent, volumetric dust and fog, highly detailed, atmospheric, no text, no words, no letters, no numbers, no logos, no signage

</details>

**Start with the thing that makes this different from every other vulnerability you have met.** A buffer overflow is a mistake. A missing bounds check is a mistake. Somebody wrote the wrong code and somebody else can write the right code. Prompt injection is **not a mistake anyone made** — it is the direct, intended consequence of the property that makes a language model useful, which is that it follows instructions expressed in ordinary language, wherever they appear. Simon Willison named the attack in **September 2022**; it is now nearly four years old, and no lab has shipped a fix, because a fix would mean a model that reliably distinguishes *"the text I was asked to act on"* from *"the text I was asked to look at"* using nothing but the text. Nobody knows how to build that.

**Which is worth setting against a boundary the industry did successfully draw, once.** SQL injection was the same category of problem: a string containing both the query's structure and the user's data, concatenated, then handed to an interpreter that could not tell which was which. It was not solved by better escaping, or by a filter that looks for `DROP TABLE`, or by asking developers to be careful. It was solved **structurally**, by the prepared statement: the query's control structure is compiled *before* any user data exists, the `?` is a hole the engine already knows about, and whatever you drop into that hole is a **value** forever. It cannot be promoted to syntax, because the syntax was finalised before it arrived. That is the shape of a real fix — and it is precisely the shape a transformer prompt does not have.

<!-- fig1 -->
<!-- DIAGRAM:START -->
![Diagram 1](diagrams/11-the-unpatchable-bug-and-the-third-magnet-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph SQL["THE ANALOGY THAT WORKED: SQL, solved structurally"]
      direction LR
      S1["The program declares the query FIRST:<br/>SELECT id FROM users WHERE name = ?"] --> S2["The question mark is a HOLE the engine<br/>knows about in advance. The control structure<br/>is compiled BEFORE any data exists."]
      S2 --> S3["Now put anything in the hole.<br/>Even the classic Bobby Tables string<br/>is still, permanently, just a NAME.<br/>It cannot be promoted to syntax."]
    end
    SQL ~~~ LLM
    subgraph LLM["THE SYSTEM WE ACTUALLY SHIPPED: no hole exists"]
      direction LR
      L1["System prompt<br/>you are a careful assistant"] --> L4
      L2["The user turn<br/>summarise my inbox and reply to Ana"] --> L4
      L3["Everything the agent fetched<br/>email bodies, web pages, tool output,<br/>a PDF, a code comment, a calendar invite,<br/>an image with text in it"] --> L4
      L4["ONE FLAT TOKEN STREAM.<br/>There is no field, tag or type anywhere<br/>that means THIS PART IS DATA<br/>AND MAY NEVER ACT."]
      L4 --> L5["Therefore anything in the stream<br/>is a candidate instruction,<br/>and priority is a matter of persuasion,<br/>not of architecture."]
    end
```

</details>
<!-- DIAGRAM:END -->

**Now watch what that costs once the model stops answering and starts acting.** A chatbot that can be talked into saying something rude is an embarrassment. An **agent** holds three things at once — your data, somebody else's text, and a way to reach the outside world — and Willison's name for that combination, coined **16 June 2025**, has become the field's standard vocabulary: the **lethal trifecta**. *Private data access. Exposure to untrusted content. The ability to communicate outward.* Any two are safe. All three, and a paragraph hidden in an email — white text, an HTML comment, a code comment, alt text — can read your files and mail them somewhere. Meta's version of the same insight is a design rule rather than a threat model: the **Agents Rule of Two** says an autonomous agent may hold at most two of the three, and holding all three requires a human in the loop.

**This stopped being theoretical some time in mid-2025.** The canonical case is **EchoLeak** (**CVE-2025-32711**, CVSS [Common Vulnerability Scoring System] 9.3), disclosed by Aim Security in June 2025: a **zero-click** exfiltration from Microsoft 365 Copilot. The attacker sends one ordinary-looking email containing a hidden payload. Nobody clicks it, nobody reads it. Later the user asks Copilot something unrelated, the retrieval layer pulls that email into the context window *because it is relevant*, and the hidden text executes as instructions. **The user's only action was to use the product as designed.** Microsoft patched it server-side with no customer action required and no evidence of exploitation in the wild — but notice what "patched" means here: they broke one exfiltration path in one product. The class is untouched.

**OWASP's 2026 language captures the shift better than any statistic.** Its *State of Agentic AI Security and Governance* report puts it plainly: *"The 2025 edition cataloged plausible threats. The 2026 edition catalogs CVEs, vendor advisories, and breach reports tied to nearly every category of agentic risk."* Prompt injection now maps onto **six of the ten** categories in OWASP's new **Top 10 for Agentic Applications**, where it appears at the top as **`ASI01` Agent Goal Hijack** and then reappears as the entry vector for tool misuse, privilege abuse, memory poisoning and the rest. The CVE (Common Vulnerabilities and Exposures) list has moved into the developer tools you actually run: **CVE-2025-6514** in MCP (Model Context Protocol) infrastructure (CVSS 9.6), **CVE-2026-22708** in Cursor, **CVE-2025-59532** in the OpenAI Codex CLI. And of the 53 agentic projects OWASP tracks, **28 are coding agents** — which is to say the most exposed category of agentic software in 2026 is the category you personally use every day.

**And here is the empirical result that should end the argument about detection.** The obvious engineering instinct is to build a classifier: train a model to spot injected instructions, or ask a second LLM *"is this an attack?"*, or flag text with anomalous perplexity. Those defences report respectable numbers — until somebody optimises the attack **in the presence of the defence**, which is what a real attacker does and what a static benchmark never does.

<!-- fig2 -->
<!-- PLOT:START -->
![Grouped horizontal bar chart of prompt-injection detection rates on the InjecAgent benchmark. A fine-tuned detector catches 61% of standard injections but only 1% (Vicuna-7B agent) or 10% (Llama3-8B agent) of adaptive attacks; an LLM-based detector falls from 34% and 72% to 0%; perplexity filtering catches essentially nothing either way.](images/11-the-unpatchable-bug-and-the-third-magnet-2-plot.png)

<details>
<summary>Plot source (matplotlib)</summary>

See [`images/11-the-unpatchable-bug-and-the-third-magnet-2-plot.py`](images/11-the-unpatchable-bug-and-the-third-magnet-2-plot.py). All values are Table 4 of [arXiv 2503.00061](https://arxiv.org/abs/2503.00061) (NAACL 2025 Findings), one benchmark and one unit: detection rate on InjecAgent, against the original injection versus against an attack optimised in the presence of that defence.

</details>
<!-- PLOT:END -->

**Read the direction of those bars, not their height.** A defence that catches 72% of attacks and a defence that catches 0% of attacks are not 72 points apart in the field — they are the *same defence*, measured before and after the adversary bothers to look at it. The paper's headline is blunt: eight defences evaluated, **all eight bypassed, attack success rate consistently above 50%**. Perplexity filtering is included exactly as published, catching essentially nothing in either column; it is the honest control that shows the benchmark was not rigged in the attacker's favour. This is a very old lesson in security wearing new clothes — *never evaluate a defence against an attacker who does not know it exists* — and it is being relearned in public because the machine-learning field's benchmark culture is built on static test sets.

**So what does work? Two things, and both of them cost you something real.**

<!-- fig3 -->
<!-- DIAGRAM:START -->
![Diagram 2](diagrams/11-the-unpatchable-bug-and-the-third-magnet-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    Q["FOUR FAMILIES OF ANSWER<br/>to a vulnerability with no patch"]

    Q --> A["1 - DETECT IT<br/>fine-tuned classifier, LLM judge,<br/>perplexity filter"]
    A --> A1["FAILS BY CONSTRUCTION.<br/>61 to 72 percent detection collapses to 0 to 10<br/>once the attack is optimised against the detector.<br/>Eight defences tested adaptively, eight bypassed."]

    Q --> B["2 - ASK THE MODEL TO BE CAREFUL<br/>delimiters, data-prompt isolation,<br/>sandwich the user command, instructional<br/>prevention, adversarial finetuning"]
    B --> B1["SAME CHANNEL, SAME FAILURE.<br/>You are asking the confused party<br/>to adjudicate its own confusion,<br/>in the language that confuses it."]

    Q --> C["3 - TAKE AWAY THE POWER<br/>break one leg of the lethal trifecta:<br/>private data, untrusted content,<br/>outward communication.<br/>Meta Agents Rule of Two: hold at most two."]
    C --> C1["WORKS. COSTS CAPABILITY.<br/>The agent you are left with<br/>is less useful than the one you wanted.<br/>That is the actual price, and it is not optional."]

    Q --> D["4 - REBUILD THE MISSING BOUNDARY<br/>CaMeL: a privileged model writes the plan<br/>from the trusted query ALONE and never sees<br/>untrusted text; a quarantined model parses<br/>that text into typed values; capabilities<br/>travel with every value; an interpreter<br/>enforces the policy at every tool call."]
    D --> D1["THE PREPARED STATEMENT, REDISCOVERED.<br/>Control flow is fixed before the data arrives.<br/>77 percent of AgentDojo solved with provable<br/>security, against 84 percent undefended."]
```

</details>
<!-- DIAGRAM:END -->

**Family 3 is the one you can apply this afternoon, and it is a scoping decision, not a security feature.** If an agent reads untrusted web pages and holds your credentials, it must not be able to send anything outward — no arbitrary URLs, no images with attacker-chosen query strings, no email tool. If it must send outward and holds your credentials, it must not read untrusted content. The uncomfortable part is that these are the same three properties that make an agent *worth building*, so every honest deployment is an explicit trade rather than a mitigation you can bolt on afterwards.

**Family 4 is the interesting one intellectually, because it is the prepared statement, reinvented.** Google DeepMind's **CaMeL** starts from the observation that the flat token stream is the whole bug and refuses to have one. A **privileged** model sees only the trusted user query and writes a *program* — the control flow, fixed before any untrusted byte is read. A separate **quarantined** model is the only thing that ever touches untrusted content, and its output is not text but **typed values**, which cannot become instructions because they are not in the instruction position. Every value carries a **capability** describing where it came from and where it may go, and a custom interpreter checks that at each tool call. On AgentDojo it solves **77% of tasks with provable security**, against **84%** for an undefended agent — so the security is not free, but seven points of utility is a very different bargain from the ones on offer elsewhere. It is worth naming the pattern out loud: *the fix for an injection class has never once been a better filter; it has always been a boundary that makes the dangerous transition unrepresentable.*

**Finally, the mirror image, because it is the part most coverage misses.** While the industry argues about agents as *victims*, agents have become *operators*. On **13 November 2025** Anthropic published what it described as the first reported AI-orchestrated cyber-espionage campaign: a group it tracks as **GTG-1002** jailbroke Claude Code, wired it through MCP servers, and had it run reconnaissance, vulnerability discovery, exploitation, credential harvesting and exfiltration against roughly **30 targets** with **80–90% of the multi-stage intrusion automated**, humans reduced to a few strategic decision gates. Nine months later this is no longer nation-state-only. Check Point's 2026 reporting documents a **single operator** who, between late December 2025 and mid-February 2026, breached **nine Mexican government agencies**: **1,088 typed prompts became 5,317 AI-executed commands** across 34 sessions and **305 internal servers**, exposing on the order of **400 million records** — tax filings, civil registry, patient records, vehicle and electoral data — with more than 400 custom attack scripts targeting 20 different CVEs. Check Point's framing is the sentence to keep: **AI has crossed from assistant to operator.** The economics of offence changed before the defences arrived, which is the ordinary way these things go, and it is why "prompt injection has caused few recorded incidents" is a much weaker reassurance than it sounds.

> **The "huh, I didn't know that" file.** **First — the number-one risk is number one *despite* the incident data, and OWASP says so out loud.** Ranked by raw public incidents, prompt injection *"wouldn't even make the top 10"*; it tops the list because, in OWASP's words, *"teams fight injection hard, so fewer clean exploits reach a public database, and the public count understates the risk that mature teams already spend real money holding off."* That is a genuinely tricky epistemics problem you will meet again: **a control that works makes its own threat look imaginary**, and the incident count measures your defences at least as much as the danger. **Second — the only defences that survive contact are the ones that give something up.** Not better prompts, not a smarter guard model, not a bigger base model — a *narrower agent*, or an architecture in which untrusted data is structurally incapable of steering control flow. Anyone selling you injection-proofing that costs no capability is selling the filter that the adaptive-attack chart already buried. **Third — the most exposed category of agentic software in 2026 is coding agents**: 28 of the 53 projects OWASP tracks, with live CVEs in Cursor, the Codex CLI and MCP infrastructure. The attack surface is not some future enterprise deployment. It is a repository you cloned, a dependency's README, an issue comment, a `CLAUDE.md` you did not write — all of it arriving in the same flat token stream as your instructions.

---

## 2. 🧲 The third kind of magnet

🔗 **Start here:** [2026 Europhysics Prize honours the discovery of altermagnetism as a third fundamental class of magnetism — Johannes Gutenberg University Mainz (July 2026)](https://press.uni-mainz.de/2026-europhysics-prize-honors-discovery-of-a-third-fundamental-class-of-magnetism/) · [2026 EPS Europhysics Prize for Outstanding Achievement in Condensed Matter Physics announced — European Physical Society](https://eps.org/2026-eps-europhysics-prize-for-outstanding-achievement-in-condensed-matter-physics-announced/) · [Scientists who uncovered altermagnetism win a major physics honour — SciTechDaily](https://scitechdaily.com/scientists-who-uncovered-altermagnetism-win-major-physics-honor/)
🔗 **The "why now":** [*Altermagnetic spintronics* — Jungwirth et al., review, arXiv 2508.09748](https://arxiv.org/abs/2508.09748) · [*Exploring altermagnetism in RuO₂: from conflicting experiments to emerging consensus* — *Nano Convergence* (2026)](https://link.springer.com/article/10.1186/s40580-026-00532-6) · [*Absence of magnetic order in RuO₂: insights from μSR spectroscopy and neutron diffraction* — *npj Spintronics* (2024)](https://www.nature.com/articles/s44306-024-00055-y)
🔗 **Go deeper:** [*Direct observation of altermagnetic band splitting in CrSb thin films* — *Nature Communications* (2024)](https://www.nature.com/articles/s41467-024-46476-5) · [*Terahertz electrical writing speed in an antiferromagnetic memory* — Olejník et al., *Science Advances* (2018)](https://www.science.org/doi/10.1126/sciadv.aar3566) · [*Antiferromagnetic resonance in α-MnTe* — arXiv 2502.18933](https://arxiv.org/abs/2502.18933) · [*Orbital altermagnetic photonic crystal* — arXiv 2605.28656](https://arxiv.org/abs/2605.28656)

![A dark polished crystalline solid floating above a perfectly flat, undisturbed ring of iron filings that shows no curving field lines at all, while beams of cyan and magenta light enter and leave the crystal.](images/11-the-unpatchable-bug-and-the-third-magnet-3.png)

*The claim, made visible: nothing leaks out — the filings around it lie perfectly flat, because the net magnetisation really is zero — and yet what passes through comes out **sorted by spin**. For a century those two statements were understood to be mutually exclusive. — Illustration, generated locally (ComfyUI + Z-Image Turbo); a generic conceptual scene, not a real material, instrument or measurement.*

<details>
<summary>Image prompt (source of truth)</summary>

> A dark polished crystalline octahedron floating in a black void, encircled by a perfectly flat undisturbed ring of iron filings lying completely still with no field lines curving around the crystal at all, while a single bright stream of glowing particles enters the crystal from the left and emerges on the right cleanly split into two diverging beams, one cyan and one magenta, cinematic conceptual physics illustration, deep black background, cyan and magenta accents, volumetric light rays, macro detail, highly detailed, atmospheric, no text, no words, no letters, no numbers, no people

</details>

**The old classification, and why it felt complete.** Magnetic order was sorted by one question: what do the atomic moments add up to? If they line up, you get a **ferromagnet** — iron, cobalt, the recording layer of every hard disk ever shipped — with a large net magnetisation, and, crucially, **spin-split electronic bands**: an electron of one spin sees a different energy landscape from an electron of the other, which is why a ferromagnet can drive a spin-polarised current and why you can read a bit through a tunnel junction at all. If the moments alternate and cancel, you get an **antiferromagnet** — Néel's 1930s work, and a Nobel in 1970 — with zero net magnetisation and, everyone assumed, **no spin splitting**, because the symmetry that maps one sublattice onto the other also maps spin-up onto spin-down, forcing the two bands to be degenerate everywhere. Two boxes, a clean rule, a century of use.

**The move that opened the third box was not a discovery of a material. It was a question about symmetry.** *Which* operation connects the two sublattices? The textbook antiferromagnet assumes it is a **translation** (shift by half a unit cell) or an **inversion**. Both of those, combined with time reversal, protect the spin degeneracy. But there is a third possibility that had gone unexamined: the two sublattices can be related by a **rotation** — the magnetic atoms sit in crystal environments that are rotated with respect to each other, typically by 90°, because the surrounding oxygen or tellurium cage is rotated. Time reversal combined with a *rotation* is a much weaker constraint. The moments still cancel exactly, so

$$\sum_{i}\mathbf{m}_{i} = 0$$

but the bands are free to split, and they do — not uniformly, but with a $d$-wave — or higher even-parity — **pattern in momentum space**, alternating sign as you rotate around the Brillouin zone, so that

$$E_{\uparrow}(\mathbf{k}) \neq E_{\downarrow}(\mathbf{k})$$

for generic $\mathbf{k}$ while the momentum-averaged magnetisation stays exactly zero. Šmejkal, Sinova and Jungwirth completed the full symmetry classification in **2022**, immediately generating **hundreds of candidate materials** — most of them compounds people had already made and characterised for other reasons. Experimental confirmations followed within about eighteen months, chiefly by **spin- and angle-resolved photoemission**, which can literally photograph the spin-split bands. The Europhysics Prize citation is unusually direct about what was recognised: a third elementary magnetic class *"combining ferromagnetic-like and antiferromagnetic-like characteristics considered for a century as mutually exclusive."*

<!-- fig4 -->
<!-- DIAGRAM:START -->
![Diagram 3](diagrams/11-the-unpatchable-bug-and-the-third-magnet-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    Q["TWO SUBLATTICES OF OPPOSITE SPIN.<br/>The whole taxonomy turns on ONE question:<br/>which symmetry operation connects them?"]

    Q --> F["FERROMAGNET<br/>the moments do not cancel at all"]
    F --> F1["Net magnetisation: LARGE<br/>Bands spin split: YES<br/>Easy to read, easy to write.<br/>THE PRICE: a stray dipolar field that talks to<br/>the neighbouring bit, so packing bits closer<br/>makes them less stable, not more;<br/>and dynamics stuck in the GHz."]

    Q --> A["ANTIFERROMAGNET<br/>connected by TRANSLATION or INVERSION,<br/>which forces the two spin bands to be equal"]
    A --> A1["Net magnetisation: ZERO<br/>Bands spin split: NO<br/>No stray field, no crosstalk, immune to<br/>external fields, THz dynamics.<br/>THE PRICE: almost nothing to read.<br/>Thirty years of proposals, no product."]

    Q --> AM["ALTERMAGNET<br/>connected by a ROTATION.<br/>The magnetic atoms sit in crystal cages<br/>that are rotated, typically by 90 degrees,<br/>not merely shifted"]
    AM --> AM1["Net magnetisation: ZERO<br/>Bands spin split: YES, d-wave in momentum<br/>space, up to about 1 eV in CrSb,<br/>with a Neel temperature above 700 K.<br/>No stray field AND a strongly spin polarised,<br/>readable current. THz dynamics."]
```

</details>
<!-- DIAGRAM:END -->

**Why an engineer should care, in the exact terms of the storage trade-off.** A ferromagnetic bit broadcasts. Its magnetisation produces a dipolar field outside itself, and that field is how you read it — and also how it talks to its neighbours. Push bits closer together and the crosstalk grows; the industry's answer has been ever-harder magnetic materials, which is what makes them ever-harder to write, which is the coupling that drove two decades of recording physics. An antiferromagnet has no external field at all: nothing to read, but also **nothing to disturb and nothing to disturb it**, which is why antiferromagnetic memory has been an attractive idea since the 1990s and a commercial non-event ever since. The altermagnet's proposition is to break that trade rather than to trade along it: **zero stray field, and a spin-polarised current large enough to read.** In **CrSb** the splitting reaches about **1 eV** near the Fermi level with a Néel temperature above **700 K** — the splitting is not a cryogenic curiosity, it is larger than the room-temperature energy scale by a factor of forty. In bulk α-MnTe it is around **0.5 eV**. Calculations of altermagnetic tunnel junctions predict tunnelling magnetoresistance ratios in the hundreds to thousands of percent, which is the number that decides whether a memory cell is readable at all.

**And the speed is not a marketing number — it falls straight out of the two-sublattice dynamics.** For a ferromagnet the uniform precession frequency is set by the anisotropy field alone, $f = (\gamma/2\pi)\thinspace\mu_{0}H_{A}$, which for realistic anisotropies lands in the low gigahertz. In a two-sublattice compensated magnet the two sublattices are locked together by the **exchange** field, and the standard Kittel/Keffer–Kittel result geometrically averages the two:

$$f = \frac{\gamma}{2\pi}\thinspace\mu_{0}\sqrt{H_{A}\left(2H_{E} + H_{A}\right)}$$

Exchange fields in real magnets are of order $10^{2}$ to $10^{3}$ T, so that square root buys you two to three orders of magnitude **for free, at the same anisotropy**. This is called **exchange enhancement**, and it is the cleanest example in magnetism of getting a large number out of a geometric mean.

<!-- fig5 -->
<!-- PLOT:START -->
![Log-log plot of uniform-mode resonance frequency against anisotropy field. The ferromagnet line is linear and stays in the gigahertz band; the two compensated-magnet curves, for exchange fields of 100 T and 1000 T, sit two to three orders of magnitude higher and cross into the terahertz band. Marked points: a ferromagnetic bit at 2.8 GHz, and the measured 3.5 meV magnon of alpha-MnTe at 0.85 THz.](images/11-the-unpatchable-bug-and-the-third-magnet-5-plot.png)

<details>
<summary>Plot source (matplotlib)</summary>

See [`images/11-the-unpatchable-bug-and-the-third-magnet-5-plot.py`](images/11-the-unpatchable-bug-and-the-third-magnet-5-plot.py). The curves are the standard resonance expressions with $\gamma/2\pi = 28$ GHz/T and representative exchange fields; the two marked points are measured values, not fits.

</details>
<!-- PLOT:END -->

**That factor of a thousand has already been demonstrated as a write operation, not just a resonance.** In 2018 Olejník and colleagues wrote reversible bits into a **CuMnAs** antiferromagnetic memory cell with **picosecond** electrical pulses — writing speeds three orders of magnitude beyond conventional memory — and the same cell behaved as a multi-level memristor, which is why this literature keeps drifting toward neuromorphic hardware. The altermagnet's contribution is not the speed; the antiferromagnet already had the speed. It is that the altermagnet **also lets you read the result electrically**, which is the reason none of that 2018 work turned into a product.

**Now the part that makes this a real story rather than a prize announcement.** The material that carried altermagnetism into the spotlight was **ruthenium dioxide**, RuO₂ — a rutile oxide already used industrially, easy to grow epitaxially, and the subject of dozens of transport experiments reporting anomalous Hall effects, spin-orbit torque switching, and tunnelling anisotropic magnetoresistance up to 60%. There is a difficulty. **RuO₂ may not be magnetically ordered at all.**

<!-- fig6 -->
<!-- PLOT:START -->
![Horizontal log-scale bar chart of ordered magnetic moment per atom. Iron metal sits at 2.2 Bohr magnetons per atom for scale. Polarised neutron diffraction on bulk RuO2 gives 0.05, while muon spin rotation gives 0.00048 in bulk and 0.00075 in a 12 nm film — about a hundredfold disagreement between techniques.](images/11-the-unpatchable-bug-and-the-third-magnet-4-plot.png)

<details>
<summary>Plot source (matplotlib)</summary>

See [`images/11-the-unpatchable-bug-and-the-third-magnet-4-plot.py`](images/11-the-unpatchable-bug-and-the-third-magnet-4-plot.py). All RuO₂ values are as compiled in the 2026 *Nano Convergence* review; iron is the textbook value, included only as a scale bar for what an ordinary ferromagnetic moment looks like.

</details>
<!-- PLOT:END -->

**Look at the size of that disagreement, because it tells you what kind of disagreement it is.** Polarised neutron diffraction on bulk crystals (Berlijn and colleagues, 2017) reported an ordered moment of about $0.05\thinspace\mu_{B}$ per Ru — small, but real, and enough to anchor everything that followed. Muon spin rotation, which is exquisitely sensitive to tiny static internal fields and does not need a model of the structure factor to interpret, found **no clear magnetic ordering**, with an effective moment of $4.8\times10^{-4}\thinspace\mu_{B}$ in bulk and about $7.5\times10^{-4}$ in a 12 nm film. Those numbers do not overlap within anybody's error bars; they are **two orders of magnitude apart**, which is the signature of a *category* disagreement — one technique is seeing an ordered phase and the other is seeing none — rather than a precision dispute. Meanwhile a 2024 photoemission reanalysis argued that the observed splitting in RuO₂ films **does not break the mirror symmetry** an altermagnet must break, and is better read as **Rashba-like** splitting from inversion asymmetry; and terahertz measurements of the laser-induced charge dynamics found the response fully explained by the ordinary inverse spin Hall effect with no altermagnetic term required.

**The emerging resolution is the most interesting sentence in the whole story, and it is a thin-film sentence.** The 2026 review's reading is that **bulk RuO₂ is probably not altermagnetic**, and that **epitaxial strain in fully strained ultrathin films may induce the magnetic ground state**. The numbers are specific: films grown on TiO₂ carry roughly **−4.7% compressive strain** along one axis and **+2.3% tensile** along another, the strain relaxes anisotropically above about **4 nm** of thickness, and the nonlinear magnetotransport signature appears **only in the fully strained films** and vanishes once they relax. Read as an experimentalist rather than a theorist, that is a familiar shape: *the film is not the bulk, the strain state is a hidden variable, and two laboratories reporting opposite results may both be right about their own material.* The review ends by demanding **impeccably characterised material — structurally, compositionally, and defect-wise — before anyone reaches a consensus**, which is not a physics conclusion at all. It is a metrology and process-control conclusion.

**It is worth being precise about what the controversy does and does not touch, because the headlines blur it.** Altermagnetism as a class is **not** in question: the symmetry classification is a theorem, and the spin-split bands have been directly observed in **MnTe** and **CrSb**, where nobody disputes the magnetic order. What is in question is whether *one specific, very convenient material* belongs to the class. That distinction — **the category is sound, the flagship exemplar is contested** — is a healthier situation than it sounds, and a good reminder of how new fields actually consolidate: the first material to get famous is usually the one that was easiest to grow, not the one that was most clearly right.

**Where it is going, in the last twelve months.** Electrical switching of the altermagnetic state was demonstrated in 2025, and 2026 has brought all-electrical control in altermagnetic heterostructures and *ferroelastic* altermagnets whose spin splitting can be switched between two or three non-volatile states. The idea has also escaped its own substrate: in 2026 an **orbital altermagnetic photonic crystal** reproduced the whole structure — momentum-dependent splitting with a $d_{xy}$-wave form factor, alternating pseudospin polarisation — in a lattice of **photons**, which have no spin sublattices and no exchange interaction at all. That is the strongest possible statement of what was actually discovered in 2022: **not a material, but a symmetry pattern**, portable to any wave that lives on a lattice.

> **The "huh, I didn't know that" file.** **First — a whole phase of matter hid for a century inside materials people had already made.** Altermagnetism was not found by synthesising something new; it was found by asking a question nobody had asked of a classification everyone trusted, and the answer immediately promoted **hundreds of known compounds** into a new category. The bottleneck was the taxonomy, not the samples — and the specific gap was that the standard magnetic space groups do not track what the *crystal environment* does to the two sublattices, only what the *lattice* does. **Second — the speed advantage of a compensated magnet is a geometric mean, and it is free.** The resonance goes as $\sqrt{H_{A}H_{E}}$ rather than $H_{A}$, so an exchange field of $10^{2}$ to $10^{3}$ T lifts you from gigahertz to terahertz at unchanged anisotropy — a thousand-fold speed-up that costs nothing because you were never using the exchange energy for anything else. The 2018 CuMnAs demonstration cashed exactly this, writing bits with picosecond pulses. **Third — the flagship material of the new class may not be in the class**, and the reason is almost certainly **strain in a thin film**, not physics in a crystal: minus 4.7% along one axis, relaxing above 4 nm, present in the fully strained films and absent once they let go. A hundredfold disagreement between neutrons and muons is not two teams measuring badly; it is two teams measuring **different material** and calling it by the same formula.

---

## Key terms (English · 大陆 简体 · 台灣 繁體)

| English | 大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| prompt injection | 提示词注入 | 提示詞注入 | script only |
| indirect prompt injection | 间接提示词注入 | 間接提示詞注入 | script only |
| agent (AI) | 智能体 | 代理人 / 智慧代理 | ⚠ genuinely different word (智能体 vs 代理) |
| large language model | 大语言模型 | 大型語言模型 | ⚠ phrasing differs |
| vulnerability | 漏洞 | 漏洞 / 弱點 | ⚠ 弱點 common in TW security writing |
| attack surface | 攻击面 | 攻擊面 | script only |
| data exfiltration | 数据外泄 | 資料外洩 | ⚠ genuinely different word (数据 vs 資料) |
| threat model | 威胁模型 | 威脅模型 | script only |
| prepared statement (SQL) | 预编译语句 / 参数化查询 | 預備語句 / 參數化查詢 | ⚠ 预编译 vs 預備 |
| least privilege | 最小权限 | 最小權限 | script only |
| sandbox / quarantine | 沙箱 / 隔离 | 沙箱 / 隔離 | script only |
| capability (security) | 权能 / 能力令牌 | 權能 | ⚠ CN often adds 令牌 |
| supply chain | 供应链 | 供應鏈 | script only |
| ferromagnet | 铁磁体 | 鐵磁體 | script only |
| antiferromagnet | 反铁磁体 | 反鐵磁體 | script only |
| altermagnet | 交替磁体 | 交變磁體 | ⚠ term still unsettled in both regions |
| magnetisation | 磁化强度 | 磁化量 | ⚠ genuinely different word |
| spin | 自旋 | 自旋 | same |
| spintronics | 自旋电子学 | 自旋電子學 | script only |
| exchange interaction | 交换相互作用 | 交換交互作用 | ⚠ 相互作用 vs 交互作用 |
| anisotropy | 各向异性 | 異向性 | ⚠ genuinely different word |
| Néel temperature | 奈尔温度 | 尼爾溫度 | ⚠ transliteration differs |
| band structure | 能带结构 | 能帶結構 | script only |
| Brillouin zone | 布里渊区 | 布里淵區 | script only |
| epitaxial strain | 外延应变 | 磊晶應變 | ⚠ genuinely different word (外延 vs 磊晶) |
| thin film | 薄膜 | 薄膜 | same |
| neutron diffraction | 中子衍射 | 中子繞射 | ⚠ genuinely different word (衍射 vs 繞射) |
| muon spin rotation | 缪子自旋旋转 | 緲子自旋旋轉 | ⚠ transliteration differs |
| tunnelling magnetoresistance | 隧穿磁阻 | 穿隧磁阻 | ⚠ word order differs |
| terahertz | 太赫兹 | 兆赫茲 / 太赫茲 | ⚠ TW usage varies |

---

## Sources
- [Prompt injection remains the biggest LLM risk, despite limited incidents — Infosecurity Magazine (5 Aug 2026)](https://www.infosecurity-magazine.com/news/prompt-injection-llm-risk/)
- [Prompt injection tops the 2026 OWASP GenAI / LLM Top Ten vulnerabilities — SD Times](https://sdtimes.com/security/prompt-injection-tops-2026-owasp-genai-llm-top-ten-vulnerabilities/)
- [Prompt injection still drives most agentic AI security failures in production — Help Net Security (11 Jun 2026)](https://www.helpnetsecurity.com/2026/06/11/owasp-prompt-injection-ai-security-failures/)
- [A deep dive into the OWASP Top 10 for Agentic Applications 2026 — NeuralTrust](https://neuraltrust.ai/blog/owasp-top-10-for-agentic-applications-2026)
- [OWASP Top 10 for Agentic Applications — Practical DevSecOps summary](https://www.practical-devsecops.com/owasp-top-10-agentic-applications/)
- [The lethal trifecta for AI agents: private data, untrusted content, and external communication — Simon Willison (16 Jun 2025)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Inside CVE-2025-32711 (EchoLeak): prompt injection meets AI exfiltration — Hack The Box](https://www.hackthebox.com/blog/cve-2025-32711-echoleak-copilot-vulnerability)
- [*EchoLeak: the first real-world zero-click prompt injection exploit in a production LLM system* — arXiv 2509.10540](https://arxiv.org/abs/2509.10540)
- [*Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents* — Zhan et al., arXiv 2503.00061 (NAACL 2025 Findings)](https://arxiv.org/abs/2503.00061)
- [*Defeating Prompt Injections by Design* (CaMeL) — Debenedetti et al., arXiv 2503.18813](https://arxiv.org/abs/2503.18813)
- [*Design Patterns for Securing LLM Agents against Prompt Injections* — Beurer-Kellner et al., arXiv 2506.08837](https://arxiv.org/abs/2506.08837)
- [*AgentDojo: a dynamic environment to evaluate prompt injection attacks and defenses for LLM agents* — arXiv 2406.13352](https://arxiv.org/abs/2406.13352)
- [*The attack and defense landscape of agentic AI: a comprehensive survey* — arXiv 2603.11088](https://arxiv.org/abs/2603.11088)
- [Disrupting the first reported AI-orchestrated cyber espionage campaign — Anthropic (13 Nov 2025)](https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf)
- [Incident 1263: state-linked operator reportedly uses Claude Code for autonomous cyber espionage — AI Incident Database](https://incidentdatabase.ai/cite/1263/)
- [Check Point Research: AI has crossed from assistant to operator — press release](https://www.checkpoint.com/press-releases/check-point-research-ai-has-crossed-from-assistant-to-operator-rewriting-the-rules-of-autonomous-ai-cyber-attack-and-defense/)
- [AI attacks are no longer experimental: findings from the March–April 2026 AI threat landscape — Check Point](https://blog.checkpoint.com/research/ai-attacks-are-no-longer-experimental-key-findings-from-the-march-april-2026-ai-threat-landscape/)
- [AI Security Report 2026 — Check Point Research](https://research.checkpoint.com/2026/ai-security-report-2026/)
- [2026 Europhysics Prize honours the discovery of altermagnetism as a third fundamental class of magnetism — JGU Mainz](https://press.uni-mainz.de/2026-europhysics-prize-honors-discovery-of-a-third-fundamental-class-of-magnetism/)
- [2026 EPS Europhysics Prize for Outstanding Achievement in Condensed Matter Physics announced — European Physical Society](https://eps.org/2026-eps-europhysics-prize-for-outstanding-achievement-in-condensed-matter-physics-announced/)
- [Scientists who uncovered altermagnetism win a major physics honour — SciTechDaily (July 2026)](https://scitechdaily.com/scientists-who-uncovered-altermagnetism-win-major-physics-honor/)
- [Third form of magnetism earns Europe's top physics prize — TechTimes (26 Jul 2026)](https://www.techtimes.com/articles/321612/20260726/third-form-magnetism-earns-europes-top-physics-prize-could-reshape-ai-hardware.htm)
- [Prize announcement on the Sinova group's own site (INSPIRE, Mainz)](https://www.sinova-group.physik.uni-mainz.de/2026/07/30/22-09-2026-eps-europhysics-prize-for-outstanding-achievement-in-condensed-matter-physics-announced/)
- [*Altermagnetic spintronics* — Jungwirth et al., review, arXiv 2508.09748](https://arxiv.org/abs/2508.09748)
- [*Altermagnetic spintronics* — *Nature Physics* (2026)](https://www.nature.com/articles/s41567-026-03337-w)
- [*Exploring altermagnetism in RuO₂: from conflicting experiments to emerging consensus* — *Nano Convergence* (2026)](https://link.springer.com/article/10.1186/s40580-026-00532-6)
- [*Absence of magnetic order in RuO₂: insights from μSR spectroscopy and neutron diffraction* — *npj Spintronics* (2024)](https://www.nature.com/articles/s44306-024-00055-y)
- [*Revisiting altermagnetism in RuO₂: laser-pulse-induced charge dynamics by time-domain terahertz spectroscopy* — *npj Spintronics* (2025)](https://www.nature.com/articles/s44306-025-00083-2)
- [*Direct observation of altermagnetic band splitting in CrSb thin films* — *Nature Communications* (2024)](https://www.nature.com/articles/s41467-024-46476-5)
- [*Terahertz electrical writing speed in an antiferromagnetic memory* — Olejník et al., *Science Advances* (2018)](https://www.science.org/doi/10.1126/sciadv.aar3566) · [open-access mirror (PubMed Central)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5938222/)
- [*Antiferromagnetic resonance in α-MnTe* — arXiv 2502.18933](https://arxiv.org/abs/2502.18933)
- [*Electrical switching of altermagnetism* — arXiv 2412.20938](https://arxiv.org/abs/2412.20938)
- [*Orbital altermagnetic photonic crystal* — arXiv 2605.28656](https://arxiv.org/abs/2605.28656)
- [*Photonic altermagnets: magnetic symmetries in photonic structures* — arXiv 2506.23497](https://arxiv.org/abs/2506.23497)
- [*Symmetry, microscopy and spectroscopy signatures of altermagnetism* — arXiv 2506.22860](https://arxiv.org/abs/2506.22860)

*Prepared 2026-08-11 — two feature stories in the "Nat-Geo / Discovery" register: one **career-track** (prompt injection as a structural, unpatchable class rather than a bug — why the prepared-statement fix that killed SQL injection has no analogue in a flat token stream, the lethal trifecta and Meta's Rule of Two, the collapse of every detection-based defence under adaptive attack, CaMeL as the boundary rebuilt, and the mirror image of agents as attack operators) and one **hobby-track** (altermagnetism as a genuinely new third class of magnetic order, recognised by the July 2026 Europhysics Prize; the rotation-not-translation symmetry argument that permits zero net magnetisation with spin-split bands; the exchange-enhanced terahertz speed-up; and the live fight over whether RuO₂ — the field's flagship material — is magnetic at all, which resolves into a thin-film strain-and-defect question). Figures current to 11 August 2026. The **"What we worked out"** section will be added on finalize, after the discussion. Natural sparring hooks: **(a)** the governance thread left open by reading #13 arrives here with teeth — if detection provably fails and the only working defences cost capability, then agent security is a **scoping and authorisation** problem, so what actually belongs in a `CLAUDE.md` / `.cursor/rules` / hook layer versus in the harness versus in the model; **(b)** the CaMeL-as-prepared-statement claim is deliberately strong — is the analogy exact, or does it break down at the point where the quarantined model's *typed output* still has to be trusted for content; **(c)** the epistemics of the incident-count paradox, which generalises well beyond AI: a control that works makes its own threat look imaginary, so how *should* you rank a risk you cannot count; **(d)** on story 2, the ranking question the piece sets up but does not settle — for a memory technology, which is the binding constraint: read signal (the TMR — tunnel magnetoresistance — ratio), write energy, thermal stability at scale, or growth/variability — and his HDD (hard disk drive) decade is direct evidence on the last one; **(e)** the RuO₂ dispute read as a metrology problem rather than a physics one — neutrons versus muons is a **sensitivity-and-model-dependence** comparison, and the strain story is a hidden-variable story, both of which he has lived; and **(f)** whether the "taxonomy failure" framing linking the two stories is real or retrofitted, and if real, what it predicts about where the *next* missing category sits. Visuals: 2 ComfyUI path-4 illustrations (a reading machine fed by pages that reach for its levers; a crystal with no field around it that still sorts what passes through) + 3 matplotlib figures (detection rate before and after the attack is defence-aware; the RuO₂ moment disagreement on a log axis; ferromagnetic versus exchange-enhanced resonance) + 3 Mermaid diagrams (the prepared statement versus the flat token stream; the four families of defence and what each costs; the three magnetic classes keyed on the symmetry operation).*
