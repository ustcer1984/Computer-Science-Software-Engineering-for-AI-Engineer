# M01 · Ch1 · §1 — From Source Code to a Running Program

> **Module:** How Computers & Operating Systems Work
> **Chapter:** The execution model
> **Section:** Compilation, interpretation, and what Python *actually* does
> **Status:** ✅ finalized 2026-06-08 — personalized with applied notes from our Q&A (see §10).

**Estimated study time:** 2–3 hours including reflection.
**Prerequisites:** You can read basic Python and a little C. No prior CS (computer science) theory needed.

---

## Why this section exists (for *you*)

You write Python every day and ship it to AWS Lambda. You've felt these things without a model for *why*:

- Python "feels slow," yet your `numpy`/`torch`/LLM code is fast.
- A Lambda **cold start** is sluggish; a warm one is snappy.
- Heavy `import`s at the top of a handler cost you real latency.
- A `.pyc` file appears in `__pycache__/` and you've never thought about it.

Every one of those is the *execution model* leaking into your daily work. By the end of this section
you should be able to answer, precisely: **"When I run `python handler.py`, what actually happens, step
by step, from text on disk to electrons doing arithmetic?"** That question is the foundation the rest
of M01 (memory, concurrency, I/O, OS) builds on.

A physics analogy to hold onto: source code is like a *theoretical model on paper*. The CPU is the
*physical apparatus*. Between them sits an entire chain of translation — and just like in the lab, most
of your performance surprises live in that translation layer, not in the equations.

---

## 1. The core problem: text can't *do* anything

<details>
<summary><b>Vocabulary for this section</b> — the two translation strategies and the words around them (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **CPU** | central processing unit | the chip that actually executes instructions |
| **JIT** | just-in-time (compilation) | compiling parts of a program to machine code while it is already running — see §6 |

**Terms**

| Term | Definition |
|---|---|
| **Source code** | the human-readable program text you type into a `.py` or `.c` file |
| **Byte** | one unit of storage, eight bits; a source file on disk is just a sequence of bytes |
| **Machine code** | numbers the CPU decodes directly as operations — the only language hardware understands |
| **Instruction** | one primitive machine-code operation, e.g. add two numbers or jump somewhere else |
| **Translation** | turning source text into machine code; the whole subject of this section |
| **Compilation** | translating the **entire** program into machine code **before** running it |
| **Compiler** | the program that does that translation |
| **Interpretation** | translating and executing the program **one piece at a time, as it runs** |
| **Interpreter** | the program that does that — it stays running while your code runs |
| **Ahead of time** | before execution starts; the opposite of "while running" |
| **Runtime** | the period while the program is executing (also used loosely for the machinery that supports it) |

</details>

Your source file is just bytes — characters in a file. A CPU has no idea what `def`, `for`, or
`response = llm(prompt)` mean. A CPU understands exactly one language: **machine code** — numbers that
encode primitive operations. So *something* must translate your human-readable text into those numbers.

There are two classic strategies for that translation, and understanding their difference is the whole
game:

- **Compilation** — translate the *entire* program ahead of time into machine code, then run the result.
- **Interpretation** — translate-and-execute the program *one piece at a time*, as it runs.

Everything else ("Is Python compiled or interpreted?", "Why is C faster?", "What's a JIT?") is a
consequence of where a language sits between these two poles.

---

## 2. What the machine actually understands (just enough CPU)

<details>
<summary><b>Vocabulary for this section</b> — CPU vocabulary, instruction sets and the portability terms (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **CPU** | central processing unit | the chip that executes instructions |
| **ISA** | instruction set architecture | the published contract of which instructions exist and how they are encoded, e.g. x86-64 or ARM64 |
| **AMD** | Advanced Micro Devices | the other major maker of x86-64 chips alongside Intel |
| **ARM** | Advanced RISC Machines | the instruction-set family used by Apple Silicon and AWS Graviton |
| **AWS** | Amazon Web Services | Amazon's cloud platform |
| **OS** | operating system | the software that owns the hardware and runs your programs on it |

**Terms**

| Term | Definition |
|---|---|
| **Fetch–decode–execute cycle** | the one loop a CPU repeats forever: read the next instruction, work out what it means, do it |
| **Instruction** | one primitive operation: add, copy a value, compare, jump |
| **Register** | one of a handful of ultra-fast storage slots **inside** the CPU where arithmetic actually happens |
| **Memory** | the much larger, much slower store outside the CPU that instructions and data are read from |
| **Jump** | an instruction that changes which instruction runs next, instead of simply continuing |
| **Machine code** | the binary encoding of instructions — what the CPU literally reads |
| **Assembly** | a human-readable, one-to-one text alias for machine code, e.g. `addq %rax, %rbx` |
| **x86-64** | the 64-bit Intel/AMD instruction set; also written amd64 |
| **ARM64** | the 64-bit ARM instruction set; also written aarch64 |
| **Apple Silicon** | Apple's own ARM64 laptop and desktop chips (M1, M2, …) |
| **AWS Graviton** | Amazon's own ARM64 server chips, used by ARM Lambdas and EC2 instances |
| **Docker image** | a packaged filesystem plus metadata that a container runs from; built for one ISA |
| **`linux/amd64`** | a platform tag naming an OS plus an ISA that an image was built for |
| **Emulation** | software that pretends to be another ISA so foreign machine code can run — correct, but slow |
| **Lambda** | AWS's serverless function service — you supply code, AWS supplies the machine |

</details>

You can't reason about compilation vs interpretation without knowing what they're translating *to*.
Here's the minimum mental model of a CPU — we'll go deeper in §4 (memory) and Ch1 §4 (I/O).

A CPU repeats one loop, billions of times a second — the **fetch–decode–execute cycle**:

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/01-source-to-running-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    A["1 · FETCH<br/>next instruction from memory"] --> B["2 · DECODE<br/>figure out what it means"]
    B --> C["3 · EXECUTE<br/>do it: add, compare, load…"]
    C -->|repeat, billions of times/sec| A
```

</details>
<!-- DIAGRAM:END -->

- **Instructions** are tiny: "add these two numbers," "copy this value from memory to a register,"
  "if this is zero, jump to instruction #5021." That's the whole vocabulary. No "loops," no "functions,"
  no "strings" — those are abstractions *we* build on top.
- **Registers** are a handful of ultra-fast slots *inside* the CPU where the actual arithmetic happens.
  Think of them as the CPU's hands — it can only work on what it's holding.
- **Machine code** is the binary encoding of these instructions. **Assembly** is a human-readable
  one-to-one alias for machine code (e.g. `addq %rax, %rbx`). An **instruction set architecture (ISA)**
  — x86-64 (Intel/AMD) or ARM64 (Apple Silicon, AWS Graviton) — defines which instructions exist.

> **This already touches your work:** ISAs are *why* a Docker image built for `linux/amd64` won't run on
> an Apple Silicon Mac without emulation, and why AWS Graviton (ARM) Lambdas are cheaper but need
> ARM-compatible builds. Same source code, *different machine code*. We'll return to this in M09.

The takeaway: **the gap between `response = llm(prompt)` and "add %rax, %rbx" is enormous.** Who crosses
that gap, and *when*, is the difference between a compiler and an interpreter.

---

## 3. The two strategies

<details>
<summary><b>Vocabulary for this section</b> — compiler, interpreter and the trade-offs between them (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **AOT** | ahead-of-time (compilation) | translating the whole program to machine code before it runs — the strategy in §3a |
| **CPU** | central processing unit | the chip that executes instructions |
| **ISA** | instruction set architecture | which instructions exist on a given chip family, e.g. x86-64 or ARM64 |
| **OS** | operating system | the software that runs your program on the hardware |
| **GCC** | GNU Compiler Collection | the standard open-source C compiler, invoked as `gcc` |

**Terms**

| Term | Definition |
|---|---|
| **Compiler** | a program that reads your whole source and writes out machine code before anything runs |
| **Object file (`.o`)** | the machine-code output of compiling one source file, not yet a runnable program |
| **`-O2`** | a compiler flag asking for a standard level of optimization |
| **Optimization** | the compiler rearranging, merging or deleting your code so it does the same thing faster |
| **Inlining** | pasting a small function's body into its caller so there is no call at all |
| **Whole-program optimization** | optimizing with the whole source in view, which an interpreter can never do |
| **Compile time** | when the compiler runs — errors caught here never reach production |
| **Runtime** | when the program actually executes |
| **Edit→run loop** | how long it takes to go from changing a line to seeing the result |
| **Portable** | runs unchanged on different machines; compiled output is **not**, because it is tied to one ISA plus one OS |
| **Target** | the ISA plus OS a compiler is producing code for |
| **Interpreter** | a program that reads your source and performs it statement by statement, with your code as its input data |
| **Dispatch** | the interpreter's per-operation cost of deciding which action a given piece of code calls for |
| **Runtime error** | a failure that only appears when the offending line is actually reached |
| **Intermediate representation** | a middle language, lower-level than source and higher-level than machine code |
| **Bytecode** | the usual such middle language — instructions for an abstract machine rather than a real CPU |
| **Implementation** | a specific program that runs a language (CPython, PyPy, GCC) — "compiled vs interpreted" is a property of *this*, not of the language |
| **`Dict[str, Any]`** | a Python type annotation; used here only as an example of a mistake an interpreter finds late |

</details>

### 3a. Compilation (ahead-of-time)

A **compiler** reads your *entire* program and produces a machine-code file *before* it ever runs. C is
the canonical example:

```c
// add.c
int add(int a, int b) { return a + b; }
```

```bash
gcc -O2 -c add.c -o add.o      # compile to machine code, ahead of time
```

The `add.o` is now native machine code for your CPU's ISA (instruction set architecture). When you run it, the CPU executes it
*directly* — no translator stands in between.

**Consequences (the trade-offs that matter):**

| Property | Why |
|---|---|
| ⚡ **Fast at runtime** | No translation overhead during execution — the CPU runs raw instructions. |
| 🔍 **Whole-program optimization** | The compiler sees everything and can rearrange, inline, and delete code (`-O2` above). |
| 🧱 **Catches errors before running** | Type mismatches, undeclared variables → caught at *compile time*, not in production. |
| 🐌 **Slow edit→run loop** | You must recompile after every change. |
| 📦 **Not portable** | The output is tied to one ISA + OS. Build once per target (amd64, arm64, …). |

### 3b. Interpretation

An **interpreter** is itself a program that reads your source and *performs* it on the fly, statement by
statement. There's no separate machine-code file — the interpreter *is* the running thing, and your code
is its *input data*.

**Consequences — almost the mirror image:**

| Property | Why |
|---|---|
| 🔁 **Fast edit→run loop** | Just run it again; no compile step. |
| 📦 **Portable** | Ship the same source anywhere the interpreter exists. |
| 🐌 **Slower at runtime** | Every line pays a translation/dispatch cost *while running*. |
| 🐛 **Many errors surface only at runtime** | The interpreter doesn't see line 200 until it gets there. (This is exactly why your `Dict[str, Any]` typos blow up in production — foreshadowing M05.) |

### 3c. The crucial correction: it's a spectrum, not a binary

Here's the thing most people get wrong, and the single most important idea in this section:

> **"Compiled vs interpreted" is not a property of a language — it's a property of an *implementation*,
> and almost every modern language uses *both* in layers.**

C *can* be interpreted (there are C interpreters). Python *can* be compiled. What actually happens is
that real-world languages compile to an **intermediate representation (bytecode)** and then interpret
*that*. Which brings us to Python.

---

## 4. What Python *actually* does (CPython)

<details>
<summary><b>Vocabulary for this section</b> — the CPython pipeline, bytecode and the `.pyc` cache (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **CPython** | the C implementation of Python | the standard `python` binary almost everyone runs |
| **VM** | virtual machine | a software "CPU" that executes bytecode instead of machine code |
| **REPL** | read-eval-print loop | the interactive `>>>` Python prompt |
| **CPU** | central processing unit | the real chip underneath |
| **AWS** | Amazon Web Services | Amazon's cloud platform |

**Terms**

| Term | Definition |
|---|---|
| **Bytecode** | a compact instruction set for an abstract Python machine — compiled from your source, but **not** your CPU's machine code |
| **Virtual machine (CPython VM)** | the big loop, written in C, that reads bytecode instructions and performs them |
| **Compile step** | Python turning your source text into bytecode; it happens every time you import, unless a cache hits |
| **`dis`** | the standard-library module that prints a function's bytecode |
| **Disassembly** | showing machine or byte code in readable instruction form |
| **`LOAD_FAST`** | a bytecode instruction: push a local variable onto the interpreter's value stack |
| **`BINARY_OP`** | a bytecode instruction: pop the top two values, apply an operator such as `+`, push the result |
| **`RETURN_VALUE`** | a bytecode instruction: return the top value to the caller |
| **`RESUME`** | a bookkeeping bytecode CPython emits at the start of a function body |
| **Local variable** | a name that lives only inside one function call |
| **`.pyc` file** | a file holding cached bytecode for one module |
| **`__pycache__/`** | the directory Python writes those `.pyc` files into, next to the source |
| **`cpython-313`** | the version tag in the cache filename — bytecode is not guaranteed compatible across Python versions |
| **Module** | one importable `.py` file (or package) of Python code |
| **`import`** | the statement that loads a module: compile it (or load its `.pyc`) **and run its top-level code** |
| **Top-level code** | statements at column zero in a module, which execute once at import time |
| **Cold start** | an invocation where AWS must create a fresh execution environment before your handler runs |
| **Warm invocation** | a later invocation reusing an environment that is already initialized |
| **Handler** | the function AWS Lambda calls for each request |
| **Lazy import** | moving an `import` inside a function so its cost is paid only if that code path is taken |
| **`boto3`** | the AWS SDK for Python — a large, slow-to-import library |

</details>

When people say "Python is interpreted," they're hiding two steps. Here's the real pipeline for
**CPython** (the standard implementation — the `python` binary you almost certainly use):

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/01-source-to-running-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TD
    S["your_code.py<br/>(source text)"]
    BC["Bytecode (.pyc)<br/>a compact instruction set for an<br/>abstract Python machine — NOT your CPU"]
    VM["CPython VM<br/>a bytecode interpreter,<br/>written in C"]
    CPU["Your CPU"]

    S -->|"(1) COMPILE<br/>Python compiler turns source into bytecode"| BC
    BC -->|"(2) INTERPRET"| VM
    VM -->|"each bytecode op runs C code,<br/>which is already machine code"| CPU
```

</details>
<!-- DIAGRAM:END -->

So Python **is compiled** — just not to machine code. It's compiled to **bytecode**: instructions for an
abstract "Python machine" (the CPython **Virtual Machine**). Then the VM — a big loop written in C —
*interprets* that bytecode, and *that C code* is what's actually been compiled to machine code.

You can see all of this directly. Open a Python REPL (read-eval-print loop) and run:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

You'll see something like:

```
  2           RESUME                   0
  3           LOAD_FAST                0 (a)
              LOAD_FAST                1 (b)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

**That is Python bytecode.** `LOAD_FAST` ("push a local variable onto a stack"), `BINARY_OP` ("add the
top two"), `RETURN_VALUE` — these are the instructions the CPython VM (virtual machine) actually executes. Notice they're
*higher-level* than CPU instructions (they know about "local variables" and "+"), but *lower-level* than
your source. They're the in-between language.

### The `.pyc` mystery, solved

That `__pycache__/add.cpython-313.pyc` file you've seen? It's the **cached bytecode** from step (1). On
the next run, if the source hasn't changed, Python skips recompiling and loads the `.pyc` directly. It's
a startup optimization — and it's why the cache is keyed by Python version (`cpython-313`): bytecode is
not guaranteed stable across versions.

> **Connecting to your Lambda cold starts:** A cold start pays for (a) spinning up the runtime, (b)
> *importing your modules* — which means compiling their source to bytecode (or loading `.pyc`) **and
> executing all the top-level code** (every top-level `import boto3`, every module-level constant). This
> is precisely why the advice "do heavy imports lazily, inside the handler" works: you defer that
> compile-and-execute cost until it's actually needed, and warm invocations skip it entirely. You were
> already doing lazy imports in the chatbot service — now you know *what* you were saving.

---

## 5. Why this makes Python "slow" — and why your ML code isn't

<details>
<summary><b>Vocabulary for this section</b> — interpreter overhead and the native-library escape hatch (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **VM** | virtual machine | here, the CPython bytecode interpreter loop |
| **CPU** | central processing unit | the chip doing the arithmetic |
| **ML** | machine learning | the numerical workloads in the heading |
| **LLM** | large language model | a transformer-based text model, e.g. the one behind a chat API |
| **CUDA** | Compute Unified Device Architecture | NVIDIA's platform for writing code that runs on its GPUs |

**Terms**

| Term | Definition |
|---|---|
| **Dispatch** | the VM deciding, for each bytecode instruction, which chunk of C code to run — implemented as a big `switch` |
| **`switch`** | a C construct that jumps to one of many branches based on a value |
| **Operand** | one of the values an operation works on |
| **Dynamically typed** | types belong to values at runtime, not to variables, so `a + b` must be re-examined on **every** execution |
| **Boxing / unboxing** | wrapping a raw number in a full heap object (and later unwrapping it) so it can carry type and bookkeeping |
| **Heap** | the memory region where objects that outlive a single call are allocated |
| **Object header** | the bookkeeping bytes every Python object carries in front of its actual value |
| **Reference count** | CPython's per-object tally of how many names point at it; maintained on nearly every operation |
| **Per-operation overhead** | fixed cost paid once per Python-level operation — the reason a tight Python loop is 10–100x slower than C |
| **Precompiled** | already translated to machine code before your program started |
| **Native code** | machine code running directly on the CPU, with no interpreter in between |
| **Fortran** | an old numerical language; much classic linear-algebra library code is still written in it |
| **Pointer** | a memory address handed to native code so it can work on the data in place |
| **Contiguous array** | a block of raw numbers laid out back-to-back, which native code can scan at full speed |
| **`numpy` / `torch`** | Python libraries whose heavy work runs in precompiled C, Fortran or CUDA |
| **Fine-grained work** | many tiny operations — where Python's per-operation tax dominates |
| **Coarse-grained work** | few large operations — where the tax is amortized to nothing |
| **Vectorize** | rewrite an element-by-element Python loop as one whole-array library call |
| **Glue code** | code whose job is to orchestrate other components rather than do the heavy computation itself |

</details>

Now the payoff. Why is a Python loop ~10–100× slower than the same loop in C?

Because for *every single operation*, the CPython VM does a lot of work that compiled C does once, ahead
of time:
- dispatch on the bytecode op (a big `switch`),
- figure out the runtime *types* of the operands (Python is dynamically typed — `a + b` could be ints,
  floats, strings, or your custom class; the VM must check *every time*),
- box/unbox objects (even an integer is a heap object with a header — more in §2 on memory),
- manage reference counts.

That per-operation overhead is the price of Python's flexibility and fast edit loop.

**So why is `numpy`/`torch`/your LLM (large language model) inference fast?** Because the heavy work *isn't done in Python*. When
you call `numpy.dot(a, b)` or run a model, Python spends a few bytecode ops to hand a pointer to a big
array down into **precompiled C / Fortran / CUDA (Compute Unified Device Architecture)** code, which does the million multiply-adds at native
speed and hands one result back. Python is the *conductor*; the *orchestra* is compiled native code.

> **The practical heuristic this gives you:** Python is slow at *fine-grained* work (tight loops over
> individual elements) and perfectly fine as *glue* that orchestrates coarse-grained native operations.
> "Vectorize it" (push the loop down into numpy/torch) is the same idea as "don't let the conductor play
> every note." This intuition will pay off in M07 (architecture) and M13 (building with LLMs).

---

## 6. The third option: JIT compilation

<details>
<summary><b>Vocabulary for this section</b> — just-in-time compilation and the engines that use it (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **JIT** | just-in-time (compilation) | compile hot code to machine code **while** the program runs |
| **JS** | JavaScript | the browser's language |
| **GIL** | global interpreter lock | the CPython lock that lets only one thread execute Python bytecode at a time |
| **CPython** | the C implementation of Python | the standard `python` binary |
| **CPU** | central processing unit | the chip that runs the compiled result |

**Terms**

| Term | Definition |
|---|---|
| **Hot path** | code that executes many times, and so is worth the cost of compiling properly |
| **Profiling** | the engine watching which code actually runs a lot, to decide what to compile |
| **Warm-up** | the early period where a JIT is still interpreting and profiling, so the program is slow |
| **Steady state** | the later period where the hot paths are compiled and the program runs at full speed |
| **V8** | Google's JavaScript engine, used by Chrome and Node.js — a JIT |
| **Node** | Node.js, JavaScript running outside the browser on V8 |
| **PyPy** | an alternative Python implementation built around a JIT; often 5–10x faster than CPython on pure-Python loops |
| **Free-threaded build** | an experimental CPython build compiled without the GIL, so threads can run Python code in parallel |
| **Experimental** | shipped but not yet default or guaranteed stable — it may change or be removed |
| **Cold vs warm** | the same warm-up/steady-state pattern seen in AWS Lambda cold and warm invocations |

</details>

If interpretation is flexible-but-slow and compilation is fast-but-rigid, can we get both? Yes — **JIT
(Just-In-Time) compilation**: start by interpreting, watch which code runs *a lot* ("hot" paths), and
compile *those* to machine code on the fly while the program runs.

You already rely on JITs without knowing it:
- **JavaScript V8** (Chrome, Node) is a JIT (just-in-time) — it's why the JS (JavaScript) in your `arena-concept-experiment`
  frontend is far faster than its "scripting language" reputation suggests. (More in M11.)
- **PyPy** is an alternative Python implementation with a JIT — often 5–10× faster than CPython for
  pure-Python loops.
- **CPython itself** gained an *experimental* JIT in 3.13 (and a separate experimental free-threaded /
  "no-GIL" build) — both maturing through 3.14. We'll treat the GIL (Global Interpreter Lock) properly in Ch1 §3 (concurrency);
  for now just file away: *the execution model is still actively evolving.*

JITs trade a warm-up cost (the first runs are slow while the engine profiles and compiles) for steady-
state speed — which, note, is *another* flavor of the cold-vs-warm pattern you see in Lambda.

---

## 7. The one-page mental model

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/01-source-to-running-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    A["<b>Pure compilation</b><br/>C, Rust, Go<br/>AOT → machine code<br/>─────<br/>⚡ fast runtime<br/>🐌 slow edit loop<br/>🔍 errors caught early"]
    B["<b>Hybrid (the real world)</b><br/>Java, C#, Python/CPython<br/>AOT → bytecode → interpret<br/>─────<br/>📦 flexible + portable<br/>middling speed<br/>🐛 errors mostly at runtime"]
    C["<b>JIT</b><br/>JS/V8, PyPy<br/>interpret, then compile hot paths<br/>─────<br/>warm-up cost,<br/>fast steady state"]
    D["<b>Pure interpretation</b><br/>a naive tree-walker<br/>translate every line, every time<br/>─────<br/>maximum flexibility,<br/>slowest"]

    A --- B --- C --- D
```

</details>
<!-- DIAGRAM:END -->

*The arrow runs from "who translates everything up front" (left) to "who translates each line every time" (right).*

**The five things to remember:**
1. A CPU only runs **machine code**; everything else is translation on top of it.
2. **"Compiled vs interpreted" describes an *implementation*, not a language** — and it's a spectrum.
3. **CPython compiles your source to *bytecode*, then interprets that bytecode** in a C-based VM.
   (`dis.dis` lets you *see* the bytecode; `.pyc` *caches* it.)
4. Python is "slow" because of **per-operation interpreter overhead on dynamic types** — which is why
   pushing work into **native libraries** (numpy/torch) reclaims the speed.
5. **JIT** is the hybrid: interpret first, compile the hot paths later — trading warm-up for steady-state.

---

## 8. Check your understanding

Try these before our Q&A — jot a one-line answer to each. We'll dig into whichever ones are fuzzy.

1. In your own words: is Python "compiled," "interpreted," or both? Defend your answer in two sentences.
2. What exactly is in a `__pycache__/*.pyc` file, and what problem does it solve?
3. You have a pure-Python function summing a list of 10 million numbers in a `for` loop, and it's too
   slow. Give *two* fundamentally different ways to speed it up, and explain *which layer of the
   execution model* each one attacks.
4. Why can the same Python source run unchanged on your laptop and on a Graviton (ARM) Lambda, when a
   compiled C binary generally can't?
5. A teammate says "let's rewrite the hot loop in C." Under what circumstances is that worth it, and
   under what circumstances is it pointless? Tie your answer to §5.

<details>
<summary>Answers</summary>

1. **Both — and the question itself is subtly wrong.** "Compiled vs interpreted" is a property of an
   *implementation*, not a language (§3c). CPython **compiles** your source to **bytecode**, then a
   bytecode **interpreter** written in C executes that bytecode (§4). So Python is compiled — just not to
   machine code — and interpreted from there on, which puts it in the hybrid middle of §7's spectrum
   alongside Java and C#.
2. **Cached bytecode** — the output of step (1) of §4's pipeline, frozen to disk. It solves **startup
   cost**: on the next run, if the source is unchanged, Python skips re-compiling and loads the `.pyc`
   directly. That's why the filename carries the interpreter version (`cpython-313`) — bytecode is not
   guaranteed stable across Python versions, so a cache from another version must not be reused. It is
   the same cost that shows up as Lambda **INIT** time (§10c).
3. **(a) Push the loop down into native code** — `numpy.arange(...).sum()` or any vectorized call — and
   **(b) change the execution engine**, e.g. run it under **PyPy**'s JIT (just-in-time compiler), or
   CPython 3.13's experimental one. They attack different layers: (a) removes Python from the inner loop
   entirely, so the per-operation VM overhead of §5 (bytecode dispatch, dynamic type checks, boxing,
   refcounting) is paid once instead of ten million times; (b) leaves your code as-is and attacks the
   *interpretation step itself*, compiling the hot loop to machine code at run time (§6). Rewriting the
   loop in C is a variant of (a), not a third lever.
4. **Because Python is translated late and C is translated early.** The `.py` ships as source; the
   translation to machine code happens on the *target* machine, by an interpreter that AWS already built
   for ARM64 (§1's interpretation column, §10a). A C binary was translated **ahead of time** into machine
   code for one **ISA** plus one OS (§3a), so an x86-64 `.o` is meaningless to a Graviton core. The
   caveat that bites in practice: *pure* Python is portable, but **native extension wheels**
   (`pydantic-core`, `numpy`, `psycopg`) ship pre-compiled `.so` files per ISA and are not — that's the
   `invalid ELF header` failure in §10a.
5. **Worth it only when the loop is genuinely CPU-bound and fine-grained; pointless when the time is
   spent elsewhere.** §5's model says Python's tax is per-operation interpreter overhead, so you only
   recover it if the program actually spends its time executing many small Python operations. If the
   service is **I/O-bound** — waiting on an LLM call, Postgres, S3 — the CPU tax is noise and C buys
   nothing (§10b). If the hot work is already inside numpy/torch/Pydantic, it is *already* native and
   there is nothing to reclaim. And even in the genuine CPU-bound case, try **vectorizing** first: same
   lever, a fraction of the cost and no new build toolchain.

</details>

## 9. Optional: get your hands dirty (10 min, no setup beyond Python)

```python
import dis, time

# (a) See the bytecode for something with a branch and a loop:
def classify(x):
    total = 0
    for i in range(x):
        if i % 2 == 0:
            total += i
    return total

dis.dis(classify)          # read the bytecode; find the loop and the branch

# (b) Feel the interpreter overhead vs a native library:
import statistics
data = list(range(10_000_000))

t = time.perf_counter()
s1 = sum(data)             # 'sum' is C-level, but still iterates Python objects
print("builtin sum:", time.perf_counter() - t)

# Try the same with numpy if available:
# import numpy as np; arr = np.arange(10_000_000)
# t = time.perf_counter(); s2 = int(arr.sum()); print("numpy sum:", time.perf_counter()-t)
```

Notice how `numpy.sum` (operating on a native contiguous array) compares to iterating Python objects.
Bring the numbers to our chat if anything surprises you.

---

## 10. Applied — captured from our session Q&A

These are the real-world threads we worked through on 2026-06-08, distilled here so you can re-derive
them later. Each is the execution model from §1–§6 hitting your actual AWS work.

### 10a. "My laptop is x86-64 — how can it build an *ARM* Lambda?" (ties to §2, ISAs)

Split "create a Lambda" into two things:
- **Deploying** (CDK/CLI) is just **API calls + config** — architecture-independent. Your laptop tells
  AWS "make a function, `Architectures: [arm64]`, here's the package." AWS runs it on its Graviton HW.
- **The code artifact** is where ISA matters:
  - **Pure Python is portable** — it isn't machine code; AWS's ARM-compiled interpreter runs your
    source/bytecode (this is exactly §1's "late translation" point).
  - **Native extensions are NOT portable** — `pydantic-core` (Rust), `psycopg`, `numpy` ship
    pre-compiled `.so` for one ISA. x86 wheels won't load on ARM → `invalid ELF header` /
    `ImportModuleError`.
- **How an x86 host produces ARM artifacts:** download pre-built `aarch64` wheels (a *download*, no
  execution), build under **QEMU-emulated Docker** (`--platform linux/arm64`; what CDK Docker bundling
  does), or **cross-compile** (a compiler's output ISA is independent of the host it runs on).
- **Principle:** *the architecture a binary runs on is set by the build target, not the build machine.*

### 10b. "Does Lambda support compiled languages? Is Python the bottleneck?" (ties to §5)

- Lambda is **polyglot**: managed runtimes (Python, Node, Java, .NET, Ruby), **custom runtime**
  (`provided.al2023` + a `bootstrap` binary → Go, **Rust**, **C/C++** via the Lambda Runtime API), or
  **container images** (anything, up to 10 GB). Go/Rust are native AOT (ahead-of-time) — §1's left column.
- **But check the bottleneck first.** Your backends are **I/O-bound** — they spend ~95% of wall-clock
  *waiting* on the LLM, Postgres, S3, HF Hub. Python being slow *per CPU op* is irrelevant when the op
  is "await a 3s LLM call." Rust can't make the remote call faster. And the CPU-heavy bits you do run
  (Pydantic→Rust, JSON, crypto, numpy) are **already native** under Python (§5's conductor/orchestra).
- **Switch a language only when CPU-bound or cold-start-bound** — and even then, Lambda is
  per-function polyglot, so you'd rewrite *one* hot function, not the system.

### 10c. Cold-start latency — why "slow first hit, fast refresh" (ties to §1's import cost)

- A **cold start** = AWS provisions a container, then **INIT** (imports = compile-to-bytecode + run all
  top-level code), then opens resources (DB conn, secrets), *then* runs your handler. A **warm**
  invocation reuses all of that and jumps straight to the handler — your fast refresh.
- **Low traffic makes it worse, not better:** idle containers get reclaimed, so most real users hit a
  cold path. This was the arena leaderboard "UI hangs for seconds on first load" symptom.
- **Diagnose before fixing:** CloudWatch `REPORT` → `Init Duration` (cold-only). And beware a **dev DB (database)
  that auto-pauses** (Aurora Serverless v2) — it produces the *same* symptom and no Lambda fix helps.

### 10d. Cold-start mitigations (full plan in `temp/arena-cold-start-latency-plan.md`)

- **Cache / precompute** the cacheable (e.g. leaderboard → scheduled job → S3/CloudFront): ms latency,
  near-zero cost, no cold start. Best for read-heavy, staleness-tolerant endpoints.
- **Trim init** (lazy imports, smaller package) — free; attacks INIT directly.
- **SnapStart** (supports Python): snapshot the initialized runtime → big cold-start cut, low cost,
  keeps Python. Re-init unique state (DB conns/RNG — random number generator) in a restore hook.
- **Provisioned Concurrency**: keep N envs pre-warmed → cold start *eliminated*, but an **ongoing bill**
  (roughly USD 9–11 a month for PC=2 @ 512 MB 24/7, x86; ~20% less on ARM; schedule it to cut cost).
  Use only where SnapStart isn't enough.
- **Frontend perceived performance** (loading skeletons + stale-while-revalidate via React Query/SWR) —
  so a slow response never *feels* like a freeze.
- **Architecture takeaway:** scale-to-zero serverless trades cold-start latency for cost; the answer is
  *cache the cacheable, warm the latency-critical, never block the UI on a network call.*

---

## References (optional, for depth)

- Python docs — `dis` module (the authoritative bytecode reference): https://docs.python.org/3/library/dis.html
- CPython internals, "Your Guide to the Python Interpreter" — Anthony Shaw (book) or his PyCon talks.
- "Compilers vs Interpreters" — Computerphile (YouTube), good 10-min visual primer.
- PEP 659 — Specializing Adaptive Interpreter (the groundwork behind CPython's recent speedups & JIT).

---

### What's next
✅ **Finalized 2026-06-08.** This section is marked done in `courses/plan.md`; §10 captures the applied
AWS threads from our discussion for future review. The next section (**§2 — the call stack**) builds
directly on the "instructions and registers" idea from §2 here.
