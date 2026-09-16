# Daily Reading — 2026-06-12  ✅ finalized

**Today's two readings (the pair you queued yesterday, while it's fresh):**
1. **Python / data modeling** — `@dataclass`: the boilerplate-free data container, and what `frozen` / `slots` / `field()` / `replace()` actually do. *(plus the comparison you asked for: dataclass vs NamedTuple vs Pydantic vs attrs)*
2. **Python / interfaces** — `typing.Protocol`: **static duck typing**. The other half of yesterday's pipeline skeleton — your `Step` was a Protocol.

> **Why these, and why now.** In yesterday's M01 Ch2 §1 session you drove the whole thing into pipeline state-management and we landed on a best-practice skeleton (§10b): a **`frozen` dataclass `State`** flowed through explicit signatures, set-once **`Deps`** injected on `self`, and a **`Step` `Protocol`** as the uniform interface. You flagged that *both `dataclass` and `Protocol` were unfamiliar* — which is notable given your Python strength (you vibe-code and have never had to reach for them). So this reading closes that exact gap: it's not generic Python trivia, it's **the two tools that make the design we agreed on actually expressible.** They're also the concrete, hands-on layer under three things you already hold from this week: Ousterhout's *"define errors out of existence"* (06-11), the *explicit-immutable-dataflow* keeper (yesterday), and the bridge into M05 (types — *make illegal states unrepresentable*).

> **Diversification note:** this is a third computer-science / software-engineering-leaning reading day in a row (git+design → this). Deliberate — the value of consolidating the skeleton *while the session is one day old* beats strict topic-rotation. Next reading day I'll swing back to the AI thread (M12 Ch2 video, or something current). Say the word if you'd rather pivot today.

---

## 1. Data classes — stop hand-writing `__init__`, and get immutability for free

<details>
<summary><b>Vocabulary for this section</b> — every term and abbreviation used below (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **LLM** | large language model | the text model whose loosely-structured JSON output motivates validation at the boundary |
| **JSON** | JavaScript Object Notation | the text data format used for API payloads and model output |
| **API** | application programming interface | the calls a service or library exposes; here, a source of untrusted input |
| **`repr`** | representation | the developer-facing string form of an object, printed in the shell and in logs |
| **stdlib** | standard library | what ships with Python itself, needing no extra dependency |

**Terms**

| Term | Definition |
|---|---|
| **Dataclass** | a class decorated with `@dataclass`, whose boilerplate methods Python generates from its annotated fields |
| **Decorator** | a function applied with `@name` above a class or function to modify or extend it |
| **Type annotation** | the declared type of a field or argument (`prompt: str`), which the type checker reads |
| **Field** | one declared attribute of a dataclass |
| **Boilerplate** | repetitive mechanical code you would otherwise write by hand — here `__init__`, `__repr__`, `__eq__` |
| **`__init__`** | the constructor: what runs when you create an instance |
| **`__repr__`** | the method producing the object's printable representation |
| **`__eq__`** | the method defining `==`; dataclasses make it compare field values |
| **Value-based equality** | two objects are equal when their contents match, not only when they are the same object |
| **`frozen=True`** | makes instances read-only: assigning to a field afterwards raises `FrozenInstanceError` |
| **Immutability** | the property that an object cannot change after construction |
| **Shallow immutability** | freezing the reference but not what it points at — a frozen field holding a list can still be appended to |
| **Aliasing** | two names referring to the same object, so a mutation through one is visible through the other |
| **Temporal coupling** | code that only works if things happen in a particular order, e.g. mutate-then-read |
| **`slots=True`** | generates `__slots__`, giving instances a fixed layout instead of a per-instance attribute dictionary |
| **`__dict__`** | the per-instance dictionary that normally holds an object's attributes |
| **`AttributeError`** | the error raised when you touch an attribute that does not exist — what `slots` turns typos into |
| **`field(default_factory=...)`** | supplies a fresh default object per instance, instead of one object shared by all of them |
| **Mutable default** | the classic bug of using `[]` or `{}` as a default, so every instance shares the same object |
| **`replace(obj, **changes)`** | returns a new instance with some fields changed, leaving the original untouched |
| **Functional update** | producing a new value instead of mutating the old one — how you "change" frozen state |
| **Reducer** | a function that folds an update into existing state; LangGraph's generalisation of the same move |
| **LangGraph** | a library for building stateful multi-step LLM pipelines as a graph |
| **Hashable** | usable as a dictionary key or set member, which requires a stable hash and therefore immutability |
| **`NamedTuple`** | a tuple subclass with named fields — immutable and lightweight, but also iterable and indexable |
| **Tuple semantics** | being unpackable and indexable (`a, b = x`, `x[2]`) — convenient, and a place bugs hide |
| **Pydantic** | a validation library: it checks and coerces untrusted data into a declared model |
| **Coercion** | converting a value to the declared type, e.g. the string `"3"` into the integer `3` |
| **Validation** | checking that incoming data actually matches the shape you expect, and failing loudly if not |
| **Boundary** | the edge of your system where untrusted data arrives — the right place to validate |
| **`attrs`** | the third-party library dataclasses were modelled on; more powerful, with validators and converters |
| **Domain model / internal data** | your own already-trusted objects, as opposed to data crossing a boundary |
| **`Dict[str, Any]`** | an untyped dictionary used as an ad-hoc record — the habit dataclasses replace |
| **Type checker** | a tool (mypy, pyright) that verifies annotations without running the code |
| **`functools.cached_property`** | a decorator that computes a property once and stores it on the instance — which needs a `__dict__` |
| **C-struct layout** | a fixed block of memory with one slot per field, which is why `slots` is smaller and faster |

</details>

🔗 **Primary (tutorial, your level):** [Data Classes in Python — Real Python](https://realpython.com/python-data-classes/)
🔗 **Canonical reference (the one to bookmark):** [`dataclasses` — Python docs](https://docs.python.org/3/library/dataclasses.html)
🔗 **Comparative (the "which container?" question):** [Why not…? — attrs docs](https://www.attrs.org/en/stable/why.html) · [Battle of the Data Containers — Towards Data Science](https://towardsdatascience.com/battle-of-the-data-containers-which-python-typed-structure-is-the-best-6d28fde824e/)

**The one idea.** A `@dataclass` is a decorator that **writes the boring methods for you** from your type-annotated fields — `__init__`, `__repr__`, `__eq__` (and more on request). You declare the *shape*; Python generates the plumbing. That's it. Everything else is options on that.

```python
from dataclasses import dataclass, field, replace

@dataclass(frozen=True, slots=True)
class PipeState:
    prompt: str
    candidates: list[str] = field(default_factory=list)   # NOT  = []  — see below
    score: float = 0.0
```

This one line gives you: a real constructor, a readable `repr` (`PipeState(prompt='...', score=0.0)`), value-based equality (two states with the same fields are `==`), immutability, and a compact memory layout. By hand that's ~30 lines of error-prone boilerplate.

**The four knobs that matter for you (this is the keeper):**

| Knob | What it does | Why it matters to *your* design |
|---|---|---|
| `frozen=True` | Assigning to a field after construction **raises** `FrozenInstanceError`. The object is read-only. | This is the mechanism behind yesterday's keeper. A frozen `State` **cannot be mutated in place** — the aliasing/temporal-coupling bugs you were trying to avoid become *structurally impossible*, not just discouraged. "Define errors out of existence." |
| `slots=True` (3.10+) | Generates `__slots__`: instances use a fixed C-struct layout instead of a per-instance `__dict__`. | Lower memory + faster attribute access when you make many instances. Also a **bonus safety net**: typos like `state.scoer = 1` raise `AttributeError` instead of silently creating a junk attribute. |
| `field(default_factory=list)` | Per-instance default for **mutable** defaults. | **The classic trap:** `candidates: list = []` would share *one* list across *all* instances (the same mutable-default bug that bites function args). `field(default_factory=...)` is the fix — `dataclass` actually *forbids* a bare mutable default and makes you use it. |
| `replace(obj, score=0.9)` | Returns a **new** instance with some fields changed; original untouched. | This is how you "update" frozen state. It *is* the explicit-immutable-dataflow pattern in one function: `new = replace(old, **delta)` — the functional-update move that LangGraph's reducers generalize. |

> **The `frozen` is shallow gotcha (we flagged this yesterday — here's the mechanism).** `frozen=True` stops you rebinding the *field*, but if the field holds a mutable object (a `list`, a `dict`), you can still mutate *that*: `state.candidates.append(x)` succeeds on a frozen dataclass. Immutability stops at the first reference. The disciplined fix: store immutable collections (`tuple` instead of `list`) when you want it to actually hold. This is the same "names are pointers; frozen freezes the pointer, not the pointee" idea straight out of yesterday's Ch2 §1.

**The comparison you asked for — dataclass vs NamedTuple vs Pydantic vs attrs.** They look interchangeable; they are not. The axis that sorts them: **how much do you pay, and what do you get?**

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/12-dataclasses-and-protocols-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    Q["I need a typed data container.<br/>What do I actually need from it?"] --> V{"Do I need to VALIDATE / coerce<br/>untrusted external data<br/>(JSON, API input, LLM output)?"}
    V -- "yes" --> P["<b>Pydantic</b><br/>runtime validation + coercion + JSON<br/>(the cost: it's heavier, and it re-validates)"]
    V -- "no — data is already trusted" --> I{"Do I want tuple-like behavior<br/>(iterable, indexable, unpackable)?"}
    I -- "yes, genuinely" --> N["<b>NamedTuple</b><br/>immutable, lightweight<br/>⚠ but iterable = typo/unpack bugs hide"]
    I -- "no, I want a real object" --> D["<b>@dataclass</b><br/>stdlib, zero deps, frozen+slots<br/>the default for internal/domain data"]
    D -. "need validators / converters /<br/>more power, still no JSON layer" .-> A["<b>attrs</b><br/>dataclass's more powerful ancestor"]
```

</details>
<!-- DIAGRAM:END -->

The sharp distinctions (from the attrs docs and the comparison piece, both linked):
- **Pydantic is a *validation* library, not a container.** Its job is sanitizing untrusted input (it coerces `"3"` → `3`). Reach for it at your **boundaries** — exactly your **LLM (large language model)-JSON-reliability gap**: a Pydantic model is how you make malformed model output a caught validation error instead of a downstream crash. But the attrs authors warn: don't use it for your *internal domain* objects — *"Is it really necessary to re-validate all your objects while reading them from a trusted database?"* Validation is a boundary tax you shouldn't pay everywhere.
- **NamedTuple has a hidden cost:** because it *is* a tuple, it's iterable, indexable, and unpackable. That sounds convenient and is actually a **bug surface** — `a, b = my_point` silently "works" and a typo'd index `point[2]` reads neighbor data. Use it only when you genuinely want tuple semantics (e.g. a return value you'll unpack).
- **dataclass is the right default for trusted, internal data** — your pipeline `State`, config objects, domain models. Zero dependencies, and `frozen`+`slots` covers most of what you'd want.
- **attrs** is dataclass's older, more powerful sibling (validators, converters). The stdlib `dataclass` is *"intentionally less powerful than attrs… for the sake of simplicity."* Only reach for it when a dataclass can't express what you need and you still don't want Pydantic's validation weight.

**Connect it to *you*.** Your loose `Dict[str, Any]` habit (profile gap #3) is the thing dataclasses replace. A dict says "some keys, some values, who knows" — every reader has to *discover* the shape. A `frozen` dataclass *declares* the shape once, the type checker enforces it, and `slots` catches your typos. That's the cheapest correctness win on your board, and it's the literal building block of the §10b skeleton you asked me to keep.

**Questions to pressure-test while you read (your style):**
- A `frozen=True` dataclass is also **hashable by default** (it can be a dict key / set member), while a normal mutable dataclass is **not** (`__hash__` is set to `None`). Why is "immutable ⇒ safe to hash" not just a convention but a *correctness requirement*? (Think: what breaks if a dict key's hash changes after insertion?)
- You have `@dataclass(slots=True)`. Now try to `@functools.cached_property` one of its methods, or pin an arbitrary attribute on an instance. What breaks, and why is that the *same* mechanism that makes slots save memory? (One C-struct slot per declared field, no `__dict__`.)
- Map your `PipeState` from yesterday onto this: which fields should be the stable typed core, and which are the "artifacts" (your 10d insight)? Could the artifacts container itself be a frozen dataclass holding an immutable mapping — and what would `replace()` look like for an append-only update?

---

## 2. `typing.Protocol` — duck typing that the type checker can actually see

<details>
<summary><b>Vocabulary for this section</b> — every term and abbreviation used below (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **ABC** | abstract base class | Python's inheritance-based way of declaring a contract, `abc.ABC` |
| **PEP** | Python Enhancement Proposal | the numbered design document; PEP 544 is the one that introduced Protocols |

**Terms**

| Term | Definition |
|---|---|
| **Duck typing** | if it has the method you need, it will do — no declared relationship required |
| **Static duck typing** | the same idea, but written down so a type checker can verify it before the code runs |
| **`typing.Protocol`** | the class you subclass to declare a contract by shape: the methods and attributes a type must have |
| **Structural subtyping** | membership decided by shape — you match if you have the right methods with the right signatures |
| **Nominal subtyping** | membership decided by declared lineage — you match only if you inherited from the named base |
| **Signature** | a method's name, parameters and return type together |
| **Type checker** | mypy or pyright, which verifies annotations statically rather than at runtime |
| **Static check** | verification done by reading the code, before it runs |
| **Runtime check** | verification done while the program is executing |
| **`isinstance()`** | the runtime test "is this object of that type"; on a Protocol it fails unless you opt in |
| **`@runtime_checkable`** | the decorator that lets `isinstance` work on a Protocol — checking method *names* only, not signatures |
| **`TypeError`** | the error raised when an operation gets a type it cannot handle |
| **Coupling** | how much one piece of code must know about another; the thing Protocols remove here |
| **Dependency inversion** | making both sides depend on an abstraction, rather than the concrete one depending on the framework |
| **Dependency arrow** | which module imports which; Protocols reverse it so the implementations import nothing |
| **Information hiding** | keeping a decision inside one module so nothing else has to know it |
| **Deep seam** | a boundary where a simple interface can hide a lot — Ousterhout's framing, carried over from reading 06-11 |
| **Retrofit** | making an existing class (including third-party code you cannot edit) satisfy a contract |
| **Accidental match** | an unrelated type satisfying a Protocol by coincidence, because the required shape was too generic |
| **File-like / iterable / context manager** | Python's long-standing informal contracts, now expressible as Protocols |
| **`__subclasshook__`** | the hook that lets an ABC accept classes structurally rather than only by inheritance |
| **Framework-less** | building the pipeline from plain classes and functions instead of adopting an orchestration framework |
| **Graph-lite pipeline** | the learner's own design: steps wired as a small graph without a framework |
| **Node / step** | one unit of work in that pipeline — the thing the `Step` Protocol describes |
| **Contract** | what a caller may rely on: which methods exist, what they take, what they return |
| **Frozen dataclass** | an immutable data object; here the data half, with the Protocol as the behaviour half |
| **Decomposition** | how responsibilities are split across units — here, behaviour contract apart from data container |

</details>

🔗 **Primary (tutorial, your level):** [Python Protocols: Leveraging Structural Subtyping — Real Python](https://realpython.com/python-protocol/)
🔗 **The spec (why it exists, conceptually):** [PEP 544 — Protocols: structural subtyping](https://peps.python.org/pep-0544/)
🔗 **Reference:** [Protocols and structural subtyping — typing docs](https://typing.python.org/en/latest/reference/protocols.html)

**The one idea.** Python has always had **duck typing**: if it has a `.read()` method, it's "file-like" — no inheritance required. The cost was that a *type checker* couldn't see that contract; "file-like" lived only in your head and the docstring. A `Protocol` writes that contract down so **mypy/pyright can check it statically** — duck typing you can verify before runtime. The phrase to hold: **static duck typing** (a.k.a. *structural* subtyping).

```python
from typing import Protocol

class Step(Protocol):
    def run(self, state: PipeState, deps: Deps) -> PipeState:
        ...   # no body — it's a contract, not an implementation

# This class satisfies Step WITHOUT importing or inheriting it:
class Translate:
    def run(self, state: PipeState, deps: Deps) -> PipeState:
        ...
# mypy now accepts `Translate()` anywhere a `Step` is expected.
```

**Nominal vs structural — the distinction that makes it click:**
- **Nominal subtyping** (classic inheritance / ABCs): you're a `Step` *only if you declared* `class Translate(Step)`. Membership is **by name/lineage**.
- **Structural subtyping** (Protocol): you're a `Step` *if you have the right methods with the right signatures*. Membership is **by shape**. "Two classes with the same methods are structural subtypes of one another."

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/12-dataclasses-and-protocols-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    subgraph Nominal["Nominal (ABC / inheritance)"]
        direction TB
        ABC["class Step(ABC)"] --> T1["class Translate(Step)"]
        ABC --> T2["class Score(Step)"]
        note1["Each step must IMPORT and<br/>INHERIT Step. Tight coupling.<br/>Can't retrofit a 3rd-party class."]
    end
    subgraph Structural["Structural (Protocol)"]
        direction TB
        P["class Step(Protocol)<br/>def run(state, deps) -> state"]
        C1["class Translate<br/>(has .run)"] -. "matches by shape" .-> P
        C2["class Score<br/>(has .run)"] -. "matches by shape" .-> P
        C3["3rd-party class<br/>(has .run)"] -. "also matches!" .-> P
        note2["Steps know NOTHING about Step.<br/>Zero coupling. Retrofit anything."]
    end
```

</details>
<!-- DIAGRAM:END -->

**Why this is the *right* tool for your `Step` (the keeper).** With an ABC, every step must `import Step` and inherit it — the steps now *depend on* the framework. With a Protocol, the dependency arrow **reverses**: the runner depends on the *shape* `Step`, and the step classes know nothing about it. This is **dependency inversion done with zero coupling** — exactly the "deep seam" / information-hiding instinct from your Ousterhout reading. It's also why Protocols are how Python's own "file-like" / "iterable" / "context manager" contracts are now typed.

**Two caveats worth holding:**
- **`isinstance()` doesn't work by default.** A Protocol is a *static* tool; `isinstance(x, Step)` raises `TypeError` unless you decorate it `@runtime_checkable`. And even then it only checks *method names exist*, **not signatures** — so a runtime `isinstance` Protocol check is weaker than what mypy verifies statically. Lean on the static check; use `@runtime_checkable` sparingly.
- **Accidental matches.** Structural matching is *by shape*, so unrelated types can satisfy a Protocol by coincidence — the Real Python example: a `str` satisfies a `Message` protocol that just needs `.encode() -> bytes`. The narrower/more distinctive your method names and signatures, the less this bites. (A physics-style sanity check: a contract that's too loose will admit noise.)

**Connect it to *you*.** This is the cleanest answer to "how do I make my framework-less graph-lite pipeline *typed* without dragging in a framework." Each node just *has a `run`*; the Protocol lets the type checker enforce the contract across all of them with no inheritance and no coupling — which is the entire appeal of staying framework-less in the first place. It's the typed expression of the architecture you already chose. (Direct line into **M14 Ch2 — framework vs framework-less** and **M05 Ch2**.)

**Questions to pressure-test while you read:**
- ABCs *can* also be used structurally via `__subclasshook__`, and ABCs give you `isinstance` for free. So when is an **ABC** still the better choice than a **Protocol**? (Hint: do you want to *share implementation* via the base class, or only *specify a contract*? Who "owns" the classes — you, or a third party?)
- A Protocol can require **attributes**, not just methods (`score: float` as a bare annotation in the Protocol body). How does a type checker verify a *frozen dataclass* satisfies an attribute-bearing Protocol — and does `slots=True` change anything about that?
- Yesterday you reached twice for "encapsulate state in a class with methods." Protocols let you go the *other* way — define the **behavior contract** (`Step`) separately from the **data** (`PipeState`). Is separating "what it does" (Protocol) from "what it holds" (dataclass) a cleaner decomposition than one class doing both? When would you *want* them fused?

---

## What we worked out — `frozen` vs `slots`: semantics vs storage (you drove this)

You pressure-tested every flag combination with sharp yes/no hypotheses — your usual mode — and we ended with a clean mental model. The keepers:

**The article's "a slots class may not have default values" is true only for *manual* `__slots__`.** That limitation is a name collision: a dataclass default lives as a **class variable** (`x = 5`), and `__slots__` wants to put a **member descriptor** at the same name — Python forbids the overlap. `@dataclass(slots=True)` (3.10+) sidesteps it by *building a new class* that lifts the defaults out of the body; it exists precisely to kill that footgun. So my skeleton's `slots=True` + defaults is fine; the article just predates the parameter.

**`frozen` and `slots` are orthogonal — semantics vs storage layout.** This was the through-line you arrived at by the end:

| | reassign a declared field | add a new attribute/method | mechanism |
|---|---|---|---|
| `frozen=True` | ❌ blocked | ❌ blocked | `__setattr__` raises on **every** write — "no writes, ever" |
| `slots=True` | ✅ allowed | ❌ blocked | no `__dict__`; no storage cell for unknown names |

- Your hypothesis "frozen lets me add new fields, only slots blocks it" was **half wrong**: `frozen` blocks adds too, because it bans *all* writes (not just reassignment of known fields). What's *unique* to `slots` is blocking new names **while still allowing mutation of existing ones** — the mutable-but-fixed-schema case `frozen` can't express.
- **Typo-catching:** `frozen` stops write-typos only as a side effect of banning all writes; `slots`'s typo-catch is the distinctive one — it's for the **mutable** object, where it lets the real reassignment through and rejects only the misspelled new name (`AttributeError`). Read-typos always raise regardless.
- **"Once `frozen=True`, is it safe to drop `slots=True`?" → Yes, no correctness/behavior harm.** With `frozen` present, `slots` is a pure perf/memory knob. Dropping it costs memory (only at high instance counts) and closes a deliberate `obj.__dict__[...] = ...` back-door (but `frozen` was never a hard security boundary anyway); it *gains back* `weakref` support and sheds the "slots builds a new class" footgun. Keep `slots` only when minting huge numbers of instances.
- **Adding a method to an *instance* is blocked** (instances are sealed) — and the deeper point: a function assigned to an instance attribute isn't a bound method anyway (no `self` injection; the descriptor protocol only fires for functions on the **class**). To add behavior, put it on the class — `frozen`/`slots` govern instances, not the class object.

**The one-liner:** `frozen` = *immutability (semantics)*; `slots` = *storage layout (a perf knob that also forbids unknown names)*. Reach for `frozen` to flow immutable state; add `slots` for footprint/typo-discipline on **mutable** objects.

## What we worked out — how to check Protocol conformance (static-first)

You asked the right question — "if `isinstance` doesn't work, how do I check?" — and the answer is a mindset shift:

**You normally don't check at runtime at all.** A Protocol's home is the **static checker**: annotate the parameter as the protocol type, run mypy/pyright, and it verifies structural conformance *including signatures, parameter and return types* — before the code runs. That's the thorough check; at runtime you just rely on duck typing because the shape was already proven.

**The runtime escape hatch (`@runtime_checkable` + `isinstance`) is real but shallow** — use it only when control flow genuinely needs capability detection, and know its three edges:
1. **Signatures are ignored** — it checks only that a method *by that name exists*. A wrong-arity `run` still passes `isinstance`.
2. **`issubclass` raises `TypeError`** for any protocol with non-method (data) members.
3. **Opt-in & shallow** — without `@runtime_checkable`, `isinstance` refuses; with it, it's essentially bundled `hasattr` checks (presence, not correctness).

**The clean split you landed on:** *Protocol = static contract; Pydantic = runtime validation.* Opposite ends on purpose. If you need runtime *signature/type* checking (which `isinstance` won't give you), that's Pydantic's job, at your boundaries — and it's covered later in **M05 Ch2** (as a typing/validation tool) and **M13 Ch1/Ch4** (as the LLM-output guardrail for your reliability gap). You chose to leave the plan as-is.

---

## Sources
- [Data Classes in Python — Real Python](https://realpython.com/python-data-classes/)
- [`dataclasses` — Python documentation](https://docs.python.org/3/library/dataclasses.html)
- [Why not…? (attrs vs dataclasses vs namedtuple vs Pydantic) — attrs docs](https://www.attrs.org/en/stable/why.html)
- [Battle of the Data Containers — Towards Data Science](https://towardsdatascience.com/battle-of-the-data-containers-which-python-typed-structure-is-the-best-6d28fde824e/)
- [Python Protocols: Leveraging Structural Subtyping — Real Python](https://realpython.com/python-protocol/)
- [PEP 544 — Protocols: structural subtyping (static duck typing)](https://peps.python.org/pep-0544/)
- [Protocols and structural subtyping — typing documentation](https://typing.python.org/en/latest/reference/protocols.html)

*Finalized 2026-06-12. The two "What we worked out" sections are the durable record — read them first on review: (1) `frozen` vs `slots` = semantics vs storage, orthogonal, and `slots` is droppable once `frozen` is present; (2) Protocol conformance is checked **statically** by default, with `@runtime_checkable` a shallow escape hatch — Protocol is the static contract, Pydantic the runtime validator. Primer for M05 Ch2.*
