# M02 · Ch1 · §1 — How a Request Travels: the round-trips behind one `https://` call

> **Module:** Networking & The Web
> **Chapter:** The request lifecycle
> **Section:** What actually happens between typing a URL (or calling an API) and the first byte
> coming back — DNS, IP/routing, the TCP handshake, the TLS (Transport Layer Security)
> handshake, HTTP, and QUIC (Quick UDP Internet Connections) / HTTP-3 — all
> read as a **sequence of round-trips**, with a real latency budget on top.
> **Status:** ✅ finalized 2026-08-12 (body prepared 2026-08-04). Body went untouched; the Q&A drove
> the §2b IPv4/IPv6/NAT (Network Address Translation) paragraph into a real-world thread — *IPv6's actual adoption status, why AWS
> bills for public IPv4, and whether an AWS backend can run purely on IPv6* — captured in **§11 Applied**.
> **Prerequisites:** M01 Ch4 §3 (why I/O dominates latency — the round-trip as the unit of latency,
> Little's Law, the four levers, latency ≠ bandwidth). This section *is* that chapter's payoff, one
> level up: the network path is where those round-trips actually live.

**Estimated study time:** 2.5–3 hours including the `curl`/`dig` hands-on.

---

## Why this section exists — and how it's pitched

You ship HTTP APIs, API Gateway, and WebSockets every day, and they work. This module's job is to
convert that working intuition into **mechanism you can budget and debug** — so that "the API is
slow" becomes "we're paying three extra round-trips because connections aren't being reused," and "it
works locally but not in prod" becomes "split-horizon DNS" or "an idle NAT (Network Address Translation) dropped the socket."

M01 built the single machine from the bottom up (execution → memory → concurrency → I/O & syscalls).
This module connects machines. The organizing idea is the one you already earned in **M01 Ch4 §3**:

> **Latency is round-trips.** On a network path, almost nothing is computed — the time is spent
> waiting for signals to travel there and back. So the way to read *any* networked request is: **count
> the round-trips, price each one, and find which are on the critical path.**

We'll walk one `https://api.example.com/v1/thing` call from URL to first byte, layer by layer, and end
with a concrete latency budget that shows why the *handshakes*, not the data, dominate a first
request — and why connection reuse (which you already do) is the highest-leverage fix.

Because you work above this layer already, the pitch is **deep and comparative**, not "what is DNS."
The value is in the mechanism (why the handshake is 1 RTT, why HOL blocking exists), the real numbers
(the speed-of-light floor), the comparisons (TCP vs UDP vs QUIC, IPv4 vs IPv6), and the failure modes
you may have hit without naming.

---

## 1. The layered model — just enough

<details>
<summary><b>Vocabulary for this section</b> — the layer names, their units, and the abbreviations used in the table and diagram (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **OSI** | Open Systems Interconnection | the 7-layer reference model; used here only as shared jargon ("layer-7 proxy") |
| **TCP/IP** | Transmission Control Protocol / Internet Protocol | the 4-layer model the internet actually implements |
| **TCP** | Transmission Control Protocol | the transport that gives you a reliable, ordered byte stream |
| **UDP** | User Datagram Protocol | the transport that just sends a datagram, with no reliability or ordering |
| **QUIC** | (a name, not an acronym) | a modern transport built on UDP that carries its own reliability and encryption |
| **IP** | Internet Protocol | the layer that gets a packet across networks to the right host |
| **HTTP** | HyperText Transfer Protocol | the application protocol this whole module is about |
| **gRPC** | (a recursive name; "g" varies by release) | a binary remote-procedure-call protocol that runs over HTTP/2 |
| **DNS** | Domain Name System | the system that turns names into IP addresses |
| **TLS** | Transport Layer Security | the encryption layer that turns `http://` into `https://` |
| **MAC** | media access control | the hardware-level address of a network interface on one physical network |
| **URL** | uniform resource locator | the address of a resource, e.g. `https://api.example.com/v1/thing` |
| **L2 / L3 / L4 / L7** | layer 2 / 3 / 4 / 7 | shorthand for how deep into the headers a device reads — link / IP / port / application |
| **v4 / v6** | version 4 / version 6 | the two IP address formats in use |

**Terms**

| Term | Definition |
|---|---|
| **Encapsulation** | each layer wraps the layer above in its own header, like nested envelopes; the peer's matching layer unwraps it |
| **Layer** | one level of the stack, with a single job and a narrow interface to the level above and below |
| **Header** | the metadata a layer prepends to the data it was handed |
| **Payload** | the data a layer was handed, which it treats as opaque |
| **Message** | the application layer's unit — one HTTP request or response |
| **Segment** | TCP's unit: a numbered chunk of the byte stream |
| **Datagram** | UDP's unit: one self-contained packet, sent with no setup and no delivery promise |
| **Packet** | the Internet layer's unit, addressed host-to-host |
| **Frame** | the link layer's unit, addressed to the next physical hop only |
| **Port number** | a 16-bit number identifying *which program* on a host a segment belongs to |
| **IP address** | the address of a host on the internet |
| **Switch** | a device that forwards frames using MAC addresses — a layer-2 device |
| **Router** | a device that forwards packets using IP addresses — a layer-3 device |
| **Load balancer** | a device that spreads requests across several servers; layer-4 if it decides on ports, layer-7 if it reads the URL or headers |
| **`Host` header** | the HTTP header naming which site the request is for, so one IP can serve many sites |
| **WebSocket** | a long-lived, two-way connection negotiated over HTTP |
| **Deep module** | a module with a lot of functionality behind a small interface — the M04 term for what a good layer is |
| **Leaky abstraction** | an abstraction whose hidden mechanism still shows through, e.g. TCP's "reliable stream" leaking packet loss as unexplained latency |

</details>

A networked request is built like a set of **nested envelopes**. Each layer wraps the layer above in
its own header, sends it, and the peer's matching layer unwraps it. This is **encapsulation**, and it
is the single structural idea that makes the whole stack comprehensible.

The industry uses two maps. The **OSI (Open Systems Interconnection) 7-layer model** is the vocabulary ("that's a layer-7 load
balancer," "a layer-4 proxy"); the **TCP/IP 4-layer model** is what the internet actually implements.
You need OSI only as *shared jargon*; reason with the TCP/IP four:

**Table 1** — the TCP/IP layers: the job, the unit, and the kind of address each one uses.

| TCP/IP layer | Job | Unit | Examples | "Address" it uses |
|---|---|---|---|---|
| **Application** | what the two programs say to each other | message | HTTP, gRPC, WebSocket, DNS | URL / path |
| **Transport** | deliver to the right *program*, reliably or not | segment / datagram | **TCP**, **UDP**, QUIC | port number |
| **Internet** | get a packet across networks to the right *host* | packet | **IP** (v4/v6), routing | IP address |
| **Link** | move bits across one physical hop | frame | Ethernet, Wi-Fi | MAC address |

<!-- DIAGRAM:START -->
![Diagram 1](diagrams/01-how-a-request-travels-1.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph L1["Link frame — src/dst MAC"]
      direction TB
      subgraph L2["IP packet — src/dst IP address"]
        direction TB
        subgraph L3["TCP segment — src/dst port, seq/ack"]
          direction TB
          subgraph L4["TLS record — encrypted"]
            direction TB
            APP["HTTP request<br/>GET /v1/thing"]
          end
        end
      end
    end
```

</details>
<!-- DIAGRAM:END -->

*Each layer adds its own header around the payload it's handed. Your `GET` is wrapped by TLS (Transport Layer Security), then
TCP (which port? which byte-offset?), then IP (which host?), then the link frame (which next hop?).
The receiver unwraps in reverse. A "layer-N device" is one that reads down to layer N's header: a
switch reads the frame (L2), a router reads IP (L3), a load balancer reading ports is L4, one reading
the URL/`Host` header is L7.*

Two carry-overs from M04 land here exactly. **Layering is decomposition** (§1): each layer is a deep
module hiding its mechanism behind a narrow interface (TCP hands IP a packet; neither knows the
other's internals). And every layer is a **leaky abstraction** (M04 Ch2 §1 §7): TCP *sells* you a
reliable ordered byte stream, but packet loss leaks through as latency you can't see in the API — a
theme we'll hit repeatedly.

---

## 2. Names → addresses: DNS

<details>
<summary><b>Vocabulary for this section</b> — the resolver chain, the record types, and every abbreviation used below (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **DNS** | Domain Name System | the distributed database that translates names to IP addresses |
| **TTL** | time to live | how many seconds an answer may be cached before it must be looked up again |
| **TLD** | top-level domain | the last label of a name — `.com`, `.org`, `.sg` |
| **NS** | name server | a record naming which servers are authoritative for a domain |
| **A** | address | a record mapping a name to an IPv4 address |
| **AAAA** | (four As, i.e. four times the size of an A record) | a record mapping a name to an IPv6 address |
| **CNAME** | canonical name | a record making one name an alias for another; costs an extra resolution |
| **MX** | mail exchanger | a record naming the mail servers for a domain |
| **TXT** | text | a free-text record, used for verification and policy data |
| **SPF** | Sender Policy Framework | a `TXT` record listing who may send mail for a domain |
| **NXDOMAIN** | non-existent domain | the DNS answer meaning "this name does not exist" |
| **UDP** | User Datagram Protocol | the connectionless transport classic DNS rides on — one datagram each way |
| **TCP** | Transmission Control Protocol | the reliable transport DNS falls back to for large answers |
| **TLS** | Transport Layer Security | the encryption layer used by the private DNS variants |
| **DoH** | DNS over HTTPS | DNS queries tunnelled inside an HTTPS connection |
| **DoT** | DNS over TLS | DNS queries sent over a dedicated TLS connection |
| **HTTPS** | HTTP Secure | HTTP carried inside TLS |
| **IPv4 / IPv6** | Internet Protocol version 4 / version 6 | the 32-bit and 128-bit address formats |
| **CDN** | content delivery network | a globally distributed cache serving content from near the user |
| **VPC** | Virtual Private Cloud | a private, isolated network inside a cloud provider |
| **ISP** | internet service provider | the company that connects you to the internet, and usually runs your default resolver |
| **OS** | operating system | here, the local machine's own DNS cache |
| **ms** | milliseconds | thousandths of a second |

**Terms**

| Term | Definition |
|---|---|
| **Stub resolver** | the minimal DNS client built into your OS or application; it asks a recursive resolver and nothing else |
| **Recursive resolver** | the server that does the whole root → TLD → authoritative walk on your behalf and caches the answer |
| **Root servers** | the top of the DNS hierarchy; they tell you which servers handle `.com`, `.org` and so on |
| **Authoritative server** | the server that holds the real records for a domain — the final source of truth |
| **Record** | one entry in the DNS database: a name, a type, a value, and a TTL |
| **Cold cache** | the state where nothing is cached yet, so the full resolution walk runs |
| **Negative caching** | caching the *absence* of a record, so a just-created name still looks missing for a while |
| **Split-horizon DNS** | the same name answering differently depending on where you ask from — private address inside a VPC, public address outside |
| **Anycast** | announcing the same IP address from many locations so routing sends each client to the nearest one |
| **Round-trip** | one out-and-back exchange with a remote machine; the unit of latency accounting in this section |
| **Handshake** | the setup exchange a connection-oriented protocol runs before carrying data |
| **Cold start** | the extra one-time cost paid the first time, before caches and connections are warm |

</details>

You typed a name (`api.example.com`); IP routes to *numbers*. **DNS** (the Domain Name System) is the
distributed database that translates one to the other, and it's the **first round-trip of most
requests** — often an invisible latency source.

The resolution chain, first time (nothing cached):

<!-- DIAGRAM:START -->
![Diagram 2](diagrams/01-how-a-request-travels-2.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    APP["your app /<br/>stub resolver"] -->|"api.example.com?"| R["recursive<br/>resolver<br/>(ISP / 8.8.8.8)"]
    R -->|"1 . (root)?"| ROOT["root<br/>servers"]
    ROOT -->|"ask .com"| R
    R -->|"2 .com?"| TLD["TLD<br/>servers (.com)"]
    TLD -->|"ask example.com's NS"| R
    R -->|"3 api.example.com?"| AUTH["authoritative<br/>server<br/>(example.com)"]
    AUTH -->|"A = 93.184.x.x, TTL 300"| R
    R -->|"answer + cache for TTL"| APP
```

</details>
<!-- DIAGRAM:END -->

Mechanism worth owning:

- **It's a cache hierarchy, not a lookup every time.** Your OS caches, the browser caches, and above
  all the **recursive resolver** caches every answer for its **TTL** (time-to-live, seconds). The full
  root→TLD (Top-Level Domain)→authoritative walk happens only on a cold cache; the common case is a single \~1–20 ms hop
  to a nearby resolver, or a hit in local cache (≈ 0). *This is why a first request to a new host is
  slower — the cold DNS walk is a real, one-time round-trip tax*, exactly the cold-start shape from
  M01 Ch4 §3 §9.
- **Record types you'll actually meet:** `A` (name → IPv4), `AAAA` (→ IPv6), `CNAME` (alias → another
  name — costs an extra resolution), `NS` (which servers are authoritative), `MX` (mail), `TXT`
  (SPF — Sender Policy Framework — and other verification records). A CNAME chain to your
  CDN (Content Delivery Network) is common, and each hop is latency.
- **Transport:** classic DNS rides **UDP** (one datagram each way — fast, no handshake; §5), falling
  back to TCP for large answers. Modern privacy variants **DoH/DoT** (DNS over HTTPS/TLS) wrap it in
  TLS — more secure, but now with a handshake cost.
- **Anycast** makes "the root servers" and public resolvers fast: the *same* IP is announced from many
  locations and routing sends you to the nearest. The same trick underlies CDNs (§7's "move closer").

**Failure modes ("it's always DNS," and it often is):** a stale record cached for its full TTL after
you cut over a service (why you *lower TTL before* a migration); **negative caching** (a `NXDOMAIN`
cached, so a just-created record "doesn't exist" for a while); and **split-horizon DNS** — the same
name resolving to a private address inside a VPC (Virtual Private Cloud) and a public one outside, the classic "works in prod,
not from my laptop" (and vice-versa).

---

## 2b. Finding the host: IP & routing (and why NAT complicates your WebSockets)

<details>
<summary><b>Vocabulary for this section</b> — routing terms, the NAT vocabulary, and the one symbol in the text (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **IP** | Internet Protocol | the best-effort, connectionless delivery layer |
| **IPv4 / IPv6** | Internet Protocol version 4 / version 6 | the 32-bit (\~4.3 billion addresses) and 128-bit address formats |
| **NAT** | Network Address Translation | rewriting addresses so many private hosts share one public IP |
| **TCP** | Transmission Control Protocol | the reliable transport built on top of IP, covered in §4 |
| **STUN** | Session Traversal Utilities for NAT | a helper protocol that tells a host what its public address looks like from outside |
| **TURN** | Traversal Using Relays around NAT | a helper protocol that relays traffic through a third-party server when a direct path is impossible |
| **AS** | autonomous system | one network under a single routing administration, e.g. an ISP or a large cloud |
| **AWS** | Amazon Web Services | the cloud provider used in the applied section |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| ${2}^{128}$ | "two to the one hundred and twenty-eighth" | the size of the IPv6 address space — 128 bits, each independently 0 or 1 |

**Terms**

| Term | Definition |
|---|---|
| **Best-effort delivery** | the network will try to deliver a packet, and promises nothing about arrival, ordering or duplication |
| **Connectionless** | no setup exchange; each packet is routed independently of every other |
| **Hop** | one router-to-router step along the path |
| **Default gateway** | the router your machine sends everything non-local to |
| **Longest-prefix match** | the forwarding rule: pick the most specific route that covers the destination address |
| **`traceroute`** | a tool that reveals the chain of routers a packet passes through |
| **Public address** | an address reachable from anywhere on the internet |
| **Private address** | an address usable only inside one network, and not routable on the public internet |
| **Dialable** | able to receive an inbound connection because it has a stable, reachable address |
| **Peer-to-peer** | two clients connecting directly to each other rather than through a server |
| **NAT mapping** | the translation entry a NAT box keeps per connection so replies find their way back |
| **Idle timeout** | how long a NAT or firewall keeps that mapping without traffic before silently discarding it |
| **WebSocket** | a long-lived two-way connection over HTTP — the thing a dropped NAT mapping kills |
| **Heartbeat / keepalive** | a small periodic message sent purely to keep a mapping or connection alive |
| **Latency floor** | the minimum possible delay, set by distance and hop count before any protocol overhead |

</details>

With an IP in hand, the packet has to *get there*. The **Internet layer (IP)** is a **best-effort,
connectionless** delivery service: it will try to move a packet toward its destination address and
makes **no promise** it arrives, arrives once, or arrives in order. (All the reliability you rely on
is added *above* it, by TCP — §4.)

- **The journey is hops.** Your packet goes to your default gateway, then router to router across
  autonomous systems, each making a **longest-prefix-match** forwarding decision on the destination IP
  and passing it on. `traceroute` (§10) shows you the actual chain. Every hop and every kilometre is
  latency (§3).
- **IPv4 vs IPv6 — a real comparison.** IPv4's \~4.3 billion addresses ran out; the two responses were
  **NAT** (Network Address Translation — many private hosts behind one public IP) and **IPv6**
  ($2^{128}$ addresses, so every device can have a public one). NAT is now everywhere, and it has a
  consequence that touches your daily work: a NATed host has **no stable, dialable public address**, so
  *inbound* connections don't just work — which is why peer-to-peer needs STUN/TURN (helper protocols that
  discover a public address or relay traffic through a third party) and why **your
  server must accept the connection** (the client dials out). It also means a **NAT/firewall keeps a
  per-connection mapping with an idle timeout**, and when it silently drops an idle mapping, a
  long-lived **WebSocket** dies — the reason those connections need **heartbeats/keepalives** (a live
  anchor we'll return to in Ch4 real-time).

The takeaway for budgeting: the number of *hops* and the *distance* set a hard latency floor before
any protocol overhead — which §3 puts a number on.

> **The v4/v6 split is also an economics story.** Why does AWS hand almost everything an IPv4 address
> and *charge* you for a static one? Why is IPv6 still only \~half-deployed after 25 years — and can an
> AWS backend run *purely* on IPv6? That real-world thread is worked in **§11 Applied**.

---

## 3. The physics floor: distance is latency

<details>
<summary><b>Vocabulary for this section</b> — the latency terms and every symbol in the round-trip formula (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **RTT** | round-trip time | the time for a message to reach the far end and its reply to come back |
| **CDN** | content delivery network | a globally distributed cache serving content from near the user |
| **ms** | milliseconds | thousandths of a second |
| **km** | kilometres | distance |
| **m/s** | metres per second | speed |

**Symbols used in the formulas**

| Symbol | Reads as | Meaning |
|---|---|---|
| $\text{RTT}_{\min}$ | "R-T-T min" | the smallest possible round-trip time on a path — the floor set by distance alone |
| $\text{distance}$ | "distance" | the one-way path length between the two machines |
| $c$ | "c" | the speed of light in vacuum, about ${3}\times10^{8}$ m/s |
| $\frac{2}{3}c$ | "two-thirds c" | the actual signal speed in fibre, roughly ${2}\times10^{8}$ m/s |
| ${2} \times \text{distance}$ | "two times distance" | the round trip — out and back — hence the factor of two |
| $\approx$ | "approximately equals" | the two sides are close, not exactly equal |

**Terms**

| Term | Definition |
|---|---|
| **Latency** | the delay before data arrives — distinct from **bandwidth**, which is how much arrives per second |
| **Bandwidth** | throughput per unit time; adding more of it does *not* shorten a round trip |
| **Fibre** | optical cable, where signals travel at about two-thirds the speed of light |
| **Round-trip** | one out-and-back exchange; the unit in which setup cost is counted |
| **Edge / PoP** | a provider location close to users, used to shorten the physical distance |
| **Regional replica** | a copy of a service deployed nearer to its users for the same reason |
| **Same-region** | both machines inside one data-centre region, where the floor is under a millisecond |

</details>

Here is the number that reframes everything. Signals in fibre travel at about **two-thirds the speed
of light** — roughly $2\times10^{8}$ m/s. So a round trip has a **hard floor set by distance alone**,
before any software:

$$\text{RTT}_{\min} \approx \frac{2 \times \text{distance}}{\frac{2}{3}c}$$

- New York ↔ London (\~5,600 km): floor ≈ **56 ms** RTT (round-trip time). Real-world: \~70–80 ms.
- Singapore ↔ US-East (\~15,000 km): floor ≈ **150 ms** RTT. Real-world: \~200+ ms.
- Same data-centre / same region: **< 1 ms**.

You cannot beat this with a faster server or more bandwidth — it's geometry. It is the physical basis
of M01 Ch4's **"move closer"** lever (CDNs, edge, regional replicas) and of why **each extra
round-trip on a cross-ocean path costs \~150 ms**. Hold that number; it makes the next three sections
quantitative.

---

## 4. The reliable pipe: TCP

<details>
<summary><b>Vocabulary for this section</b> — the handshake, the reliability machinery, and the TCP-vs-UDP vocabulary (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TCP** | Transmission Control Protocol | turns IP's unreliable packets into a reliable, ordered byte stream |
| **UDP** | User Datagram Protocol | fire-and-forget datagrams: no handshake, no ordering, no retransmission |
| **IP** | Internet Protocol | the best-effort packet layer TCP is built on |
| **RTT** | round-trip time | the time for a message and its reply |
| **SYN** | synchronize | the first handshake packet, carrying the sender's starting sequence number |
| **ACK** | acknowledge | a packet confirming which bytes have been received |
| **SYN-ACK** | synchronize-acknowledge | the server's combined reply: yes, and here is my starting sequence number |
| **HOL** | head-of-line | the blocking pattern where one stalled item holds up everything queued behind it |
| **`cwnd`** | congestion window | how much data TCP allows in flight before waiting for acknowledgements |
| **QUIC** | (a name, not an acronym) | the UDP-based transport that fixes TCP's head-of-line blocking; §7 |
| **VoIP** | voice over IP | real-time voice traffic, a typical UDP user |
| **HTTP** | HyperText Transfer Protocol | the application protocol carried over TCP here |
| **DNS** | Domain Name System | name resolution, a typical UDP user |
| **ms** | milliseconds | thousandths of a second |

**Terms**

| Term | Definition |
|---|---|
| **Byte stream** | the abstraction TCP sells: an ordered, gap-free sequence of bytes, as if you were writing to a file |
| **3-way handshake** | the SYN / SYN-ACK / ACK exchange that opens a TCP connection — one full RTT before any data |
| **Sequence number** | the number identifying where a byte sits in the stream, so the receiver can reorder and spot gaps |
| **Retransmission** | resending data that was not acknowledged within a timeout |
| **Flow control** | the receiver advertising how much it can buffer, so a fast sender cannot drown a slow one |
| **Sliding window** | the mechanism implementing flow control: a moving range of bytes the sender may have outstanding |
| **Congestion control** | the sender limiting its rate to avoid overloading the *network* — distinct from flow control, which protects the *receiver* |
| **Slow start** | the ramp-up phase: a new connection sends cautiously and grows its window as acknowledgements return |
| **In-flight** | sent but not yet acknowledged |
| **Head-of-line blocking** | in-order delivery means one lost segment stalls every byte behind it, even bytes that already arrived |
| **Warm connection** | one that is already open and has already ramped up its congestion window — hence faster than a new one |
| **Connection reuse** | sending later requests over an already-open connection instead of paying setup again |
| **Datagram** | one self-contained UDP packet, delivered or lost independently |
| **Fire-and-forget** | send it and do not track whether it arrived |

</details>

IP gives you unreliable packets; **TCP** turns them into the **reliable, ordered, byte-stream**
abstraction almost everything above assumes. It costs a round-trip up front and adds machinery you
should recognize.

**The 3-way handshake — one full RTT before any data:**

- Client → **SYN** (*synchronize* — can we talk? here's my starting sequence number)
- Server → **SYN-ACK** (yes; here's mine)
- Client → **ACK** (*acknowledge* — got it) — and only now can the client send the HTTP request.

That's **1 RTT of pure setup** — \~150 ms on our cross-ocean path, spent before a single byte of your
request goes out. Remember it for the budget.

**What TCP adds on top of IP** (the reliability that leaks as latency):

- **Sequence numbers + ACKs + retransmission:** every byte is numbered; the receiver acknowledges;
  unacknowledged data is resent after a timeout. Loss → a retransmit wait → your "reliable stream"
  mysteriously stalls (the leak).
- **Flow control (sliding window):** the receiver advertises how much it can buffer, so a fast sender
  can't drown a slow receiver.
- **Congestion control (slow-start, `cwnd`):** TCP *ramps up* — it starts cautious and grows the
  in-flight window as ACKs return. Consequence: a brand-new connection is **slow for its first few
  round-trips**, which is *another* reason connection reuse wins (a warm connection has already ramped).
- **Head-of-line (HOL) blocking:** because the stream must be delivered *in order*, one lost segment
  stalls *everything* behind it, even bytes that already arrived. This is TCP's built-in limitation
  and the specific thing QUIC (§7) sets out to fix.

**TCP vs UDP — the fork.** **UDP** is the other transport: fire-and-forget datagrams, **no handshake,
no ordering, no retransmit, no congestion control** — just "send this packet, maybe it arrives." It
trades reliability for zero setup latency and no HOL (head-of-line) blocking. Use TCP when you need every byte in
order (HTTP, databases); use UDP when you need speed and can tolerate/handle loss yourself (DNS,
real-time video/VoIP, games) — and, as we'll see, as the *foundation QUIC builds its own smarter
reliability on top of.*

---

## 5. Securing it: TLS (as a latency line-item)

<details>
<summary><b>Vocabulary for this section</b> — the TLS handshake as a latency line-item (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **TLS** | Transport Layer Security | the protocol that encrypts and authenticates a connection before HTTP flows |
| **HTTPS** | HTTP Secure | HTTP carried inside TLS; the `https://` scheme |
| **RTT** | round-trip time | the time for a message and its reply |
| **0-RTT** | zero round-trip time | resumption that lets a client send data on its very first flight, costing no extra round trip |
| **TCP** | Transmission Control Protocol | the reliable transport TLS normally runs on top of |
| **DNS** | Domain Name System | name resolution, the first round-trip of a cold request |
| **HTTP** | HyperText Transfer Protocol | the application protocol that finally carries your request |
| **ms** | milliseconds | thousandths of a second |

**Terms**

| Term | Definition |
|---|---|
| **TLS handshake** | the exchange in which client and server agree keys and the server proves its identity, before any HTTP is sent |
| **TLS 1.2** | the older version, needing about two round-trips of handshake |
| **TLS 1.3** | the modern default, needing one round-trip — and zero on resumption |
| **Resumption** | reusing key material from a recent session with the same host, so the handshake can be shortened |
| **Early data** | application data sent on the first 0-RTT flight, before the handshake completes |
| **Cold request** | the first request to a host, with nothing cached and no connection open |
| **Time to first byte** | how long after the request starts before the first byte of the response arrives |
| **Latency line-item** | treating a protocol step as a row in a budget: how many round-trips does it cost |

</details>

Almost every request today is `https://`, so after TCP connects, client and server run a **TLS
handshake** to agree on keys before any HTTP flows. Full crypto detail is M02 Ch3 / M10; here it's a
**latency line-item**, and the version matters:

- **TLS 1.2:** \~**2 RTT** of handshake.
- **TLS 1.3** (the modern default): **1 RTT** — and **0-RTT resumption** for a host you've talked to
  recently (send early data on the first flight). A major reason the modern web feels faster.

So a **first** `https://` request to a **new** host, cold, pays, in order: **DNS** (≈1 round-trip if
uncached) **+ TCP** (1 RTT) **+ TLS** (1 RTT) **+ HTTP** (1 RTT for request→first byte). On our
cross-ocean path that's roughly **4 × 150 ms ≈ 600 ms before the first useful byte** — and the actual
data was one of those four. *That ratio is the whole point of this section.*

---

## 6. The whole journey, assembled

<details>
<summary><b>Vocabulary for this section</b> — the four steps in the sequence diagram and their labels (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **DNS** | Domain Name System | step ①: name to IP address |
| **TCP** | Transmission Control Protocol | step ②: the reliable transport handshake |
| **TLS** | Transport Layer Security | step ③: the encryption handshake |
| **HTTP** | HyperText Transfer Protocol | step ④: the actual request and response |
| **RTT** | round-trip time | the time for a message and its reply — the unit each step is counted in |
| **SYN / SYN-ACK / ACK** | synchronize / synchronize-acknowledge / acknowledge | the three packets of the TCP handshake |

**Terms**

| Term | Definition |
|---|---|
| **ClientHello** | the first TLS message: the client's supported versions, ciphers and extensions |
| **ServerHello** | the server's reply, choosing the parameters and starting the key exchange |
| **Certificate** | the signed document by which the server proves it really is that hostname |
| **`200 OK`** | the HTTP status code meaning the request succeeded |
| **`GET`** | the HTTP method that asks for a representation of a resource without changing it |
| **Keep-alive** | holding the TCP connection open after a response so the next request skips steps ② and ③ |
| **Setup round-trip** | a round-trip spent on negotiation rather than on carrying your data — three of the four here |
| **Connection reuse** | sending the next request over that still-open connection |

</details>

<!-- DIAGRAM:START -->
![Diagram 3](diagrams/01-how-a-request-travels-3.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
sequenceDiagram
    participant C as Client
    participant R as DNS resolver
    participant S as Server
    Note over C,R: ① DNS (skipped if cached)
    C->>R: api.example.com ?
    R-->>C: 93.184.x.x
    Note over C,S: ② TCP handshake — 1 RTT
    C->>S: SYN
    S-->>C: SYN-ACK
    C->>S: ACK
    Note over C,S: ③ TLS 1.3 handshake — 1 RTT
    C->>S: ClientHello
    S-->>C: ServerHello + cert
    Note over C,S: ④ HTTP — 1 RTT to first byte
    C->>S: GET /v1/thing
    S-->>C: 200 OK (first byte)
    Note over C,S: reuse this connection → ②③ skipped next time
```

</details>
<!-- DIAGRAM:END -->

Four sequential round-trips, three of which are *setup*. The dashed lesson: keep the connection open
(HTTP keep-alive) and the next request to the same host pays only step ④.

---

## 7. QUIC & HTTP/3 — the modern reshuffle

<details>
<summary><b>Vocabulary for this section</b> — QUIC's vocabulary and the HTTP version lineage (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **QUIC** | (a name, not an acronym — originally "Quick UDP Internet Connections") | a transport built on UDP that carries its own reliability, ordering and encryption |
| **HTTP/1.1, HTTP/2, HTTP/3** | HyperText Transfer Protocol versions | the three wire formats in use; same meaning, different delivery |
| **UDP** | User Datagram Protocol | the bare datagram transport QUIC builds on |
| **TCP** | Transmission Control Protocol | the reliable transport HTTP/1.1 and HTTP/2 use |
| **TLS** | Transport Layer Security | the encryption layer; QUIC folds TLS 1.3 into its own handshake |
| **RTT** | round-trip time | the time for a message and its reply |
| **0-RTT** | zero round-trip time | resumption with no extra handshake round-trip |
| **HOL** | head-of-line | the blocking pattern where one stalled item holds up everything behind it |
| **OS** | operating system | relevant because TCP lives in the kernel and QUIC does not |
| **IP** | Internet Protocol | the addressing layer underneath |

**Terms**

| Term | Definition |
|---|---|
| **User space** | ordinary application code, outside the OS kernel — so QUIC can be updated by shipping a new app, not a new kernel |
| **Kernel** | the core of the operating system, where the TCP implementation lives and changes slowly |
| **Stream** | one independent ordered sequence of data inside a single connection |
| **Multiplexing** | carrying many streams over one connection at the same time |
| **Head-of-line blocking** | one lost packet stalling data behind it; in TCP it stalls *all* streams, in QUIC only its own |
| **Connection migration** | a connection surviving a change of network because it is identified by an ID rather than by addresses |
| **Connection ID** | the identifier QUIC uses in place of the address pair |
| **4-tuple** | source IP, source port, destination IP, destination port — how TCP identifies a connection, which is why changing network kills it |
| **Resumption** | reusing key material from a recent session to shorten or skip the handshake |

</details>

QUIC is what you get when you take the previous three sections seriously and ask "why are TCP and TLS
*two* separate handshakes, and why does one lost packet stall unrelated streams?" It's the transport
behind **HTTP/3**, and it's worth knowing because it's now a large fraction of real web traffic.

- **Built on UDP**, QUIC re-implements reliability, ordering, and congestion control *itself* — in
  user space — so it can evolve without waiting for OS kernels.
- **Merged connection + crypto setup: 1-RTT** (often **0-RTT** on resumption) to a *secure* connection,
  because it folds the TLS 1.3 handshake into the transport handshake — collapsing steps ② and ③ into
  one.
- **No cross-stream HOL blocking:** QUIC has independent streams, so a lost packet stalls only *its*
  stream, not the others (the fix for TCP's §4 limitation — decisive when a page pulls many objects).
- **Connection migration:** a connection is identified by an ID, not the IP+port 4-tuple, so it
  *survives* a network change (Wi-Fi → cellular) without re-handshaking — a real mobile win.

The pattern to notice: HTTP/1.1 → HTTP/2 (multiplexing over one TCP connection, but still one
TCP-level HOL queue) → HTTP/3 (QUIC, per-stream independence). Each step attacks **round-trips and
head-of-line blocking** — the two themes of this whole section.

---

## 8. The latency budget — put numbers on it

<details>
<summary><b>Vocabulary for this section</b> — the budget's phases and the three latency levers (click to expand)</summary>

**Abbreviations**

| Short | Stands for | Meaning |
|---|---|---|
| **DNS** | Domain Name System | the name-resolution phase of the budget |
| **TCP** | Transmission Control Protocol | the transport-handshake phase |
| **TLS** | Transport Layer Security | the encryption-handshake phase |
| **HTTP** | HyperText Transfer Protocol | the phase that actually carries the request and response |
| **RTT** | round-trip time | the unit each phase is measured in |
| **0-RTT** | zero round-trip time | TLS resumption that costs no extra round-trip |
| **CDN** | content delivery network | a globally distributed cache serving content from near the user |
| **PoP** | point of presence | one of a CDN's physical locations close to users |
| **HTTP/2** | HyperText Transfer Protocol version 2 | the version that multiplexes many requests over one connection |
| **ms** | milliseconds | thousandths of a second |

**Terms**

| Term | Definition |
|---|---|
| **Latency budget** | the total time to first byte, broken into the round-trips that make it up |
| **Time to first byte** | how long after a request starts before its first response byte arrives |
| **Cold** | nothing cached, no connection open — the full four round-trips |
| **Warm** | DNS cached and the connection still open, so only the HTTP round-trip remains |
| **Keep-alive** | holding a connection open between requests so setup is paid once, not per request |
| **Multiplexing** | sending many requests concurrently over one connection |
| **Prefetch** | resolving DNS or opening a connection ahead of time, before the request is actually needed |
| **Streaming** | sending the response body progressively so the client can start using it before the whole body exists |
| **First paint** | the moment a browser first draws something for the user |
| **Unit cost** | the size of one round-trip on a given path; moving closer shrinks it, reusing connections reduces how many you pay |

</details>

This is the payoff figure: the same first-byte cost, broken into its round-trips, for three real
scenarios. It makes M01 Ch4's abstractions ("count the round-trips," "amortize setup," "move closer")
concrete.

<!-- FIGURE:fig1 -->
![Grouped horizontal stacked bars of 'time to first byte,' broken into four phases — DNS, TCP handshake, TLS 1.3 handshake, and HTTP request-to-first-byte. Bar 1 'Same-region, cold' totals about 12 ms (all phases tiny). Bar 2 'Cross-ocean, cold' totals about 520 ms, made of four roughly-equal ~150 ms segments (a small DNS piece plus TCP, TLS, and HTTP each ~160 ms) — three of the four segments are setup. Bar 3 'Cross-ocean, warm (keep-alive + DNS cached)' totals about 160 ms: DNS, TCP, and TLS collapse to zero and only the single HTTP round-trip remains. The figure shows that on a long path the handshakes dominate a first request and that connection reuse removes three of the four round-trips.](diagrams/01-how-a-request-travels-fig1.svg)

**Figure 1** — time to first byte broken into its four phases — DNS, TCP, TLS and the request itself.

Read off the levers (all four from M01 Ch4 §3, now concrete):

- **Fewer round-trips.** Reuse connections (HTTP keep-alive) so DNS+TCP+TLS are paid **once**, not per
  request — the jump from bar 2 to bar 3, \~520 ms → \~160 ms, for free. TLS 1.3 / 0-RTT and HTTP/2
  multiplexing cut more. *This is the single highest-leverage web-latency fix, and it's the same
  connection-reuse move you already applied to the arena cold-start.*
- **Move closer.** A CDN/edge PoP near the user shrinks every RTT — it attacks the \~150 ms *unit
  cost*, turning bar 2 into bar 1. It's the only lever that beats the §3 physics floor (by shortening
  the distance).
- **Overlap & hide.** Fire independent requests concurrently (they share the warm connection), prefetch
  DNS/connections, and stream so first paint doesn't wait for the whole body.

---

## 9. Check your understanding

1. A colleague says "our API is slow, let's buy more bandwidth." The payload is 4 KB and the client is
   cross-ocean from the server. Why is bandwidth almost certainly the wrong lever, and what does the
   §8 budget say to look at instead?
2. Put the round-trips of a **first** `https://` GET to a **new** host in order, and say which one
   carries the actual application data. Then say which of them a **reused** connection skips.
3. What is head-of-line blocking in TCP, why does it happen, and how does QUIC/HTTP-3 avoid it?
4. You cut a service over to a new IP; some users hit the old box for hours. Name the DNS mechanism
   responsible and the one thing you should have done *before* the cutover.
5. A WebSocket that's idle for a few minutes keeps dropping in production but never on your local
   machine. Give the most likely network-layer cause and the standard mitigation.
6. Why is a brand-new TCP connection slow for its first few round-trips even on a fast link — and how
   does that reinforce the case for connection reuse?

<details>
<summary>Answers</summary>

1. Because the time is **round-trips, not bytes** (M01 Ch4 §3: latency ≠ bandwidth). A 4 KB body fits
   in a packet or two; on a \~150 ms-RTT path the cost is the **four sequential round-trips** (DNS, TCP,
   TLS, HTTP), \~600 ms cold — bandwidth changes none of them. Look at **eliminating round-trips**:
   connection reuse / keep-alive, TLS 1.3 + resumption, and a CDN/edge to cut the RTT unit cost.
2. Order: **DNS → TCP handshake → TLS handshake → HTTP request/response**. Only the **HTTP** step
   carries application data; the first three are setup. A **reused (keep-alive) connection skips DNS
   (cached), TCP, and TLS** — paying only the HTTP round-trip.
3. TCP guarantees **in-order** delivery of one byte stream, so if a segment is lost, every byte that
   arrived *after* it must wait in the buffer until the missing one is retransmitted — one loss stalls
   everything behind it. QUIC (HTTP/3) runs **independent streams** over UDP, so a loss stalls only its
   own stream; the others proceed.
4. **TTL-based caching** in resolvers held the old `A` record for its full TTL. Before the cutover you
   should have **lowered the record's TTL** (well ahead of time) so caches expire quickly, then changed
   the record — and raised the TTL back afterward.
5. A **NAT/firewall idle timeout** silently dropped the connection's mapping (locally there's no NAT
   between you and the server). Mitigation: **application-level heartbeats / keepalive pings** (or
   TCP keepalive) to keep the mapping alive — Ch4 real-time revisits this.
6. **TCP slow-start:** congestion control starts with a small window and grows it as ACKs return, so
   throughput ramps over the first few RTTs regardless of link speed. A **reused** connection has
   already ramped (and skipped the handshakes), so it's faster from the first byte — another reason to
   keep connections warm.

</details>

---

## 10. Optional: get your hands dirty (30–40 min) — watch the round-trips

Make the invisible round-trips visible on your own machine.

1. **The DNS walk:** `dig +trace api.github.com` — watch it descend root → TLD (Top-Level Domain) → authoritative. Then
   `dig api.github.com` twice and compare the reported query time (the second is cache-warm). Look at
   the TTL.
2. **The phase breakdown of one request** — the single most useful command here:
   ```bash
   curl -w "dns:%{time_namelookup}s  tcp:%{time_connect}s  tls:%{time_appconnect}s  ttfb:%{time_starttransfer}s  total:%{time_total}s\n" \
        -o /dev/null -s https://api.github.com
   ```
   The numbers are **cumulative** — DNS, then +TCP, then +TLS, then +time-to-first-byte. Subtract
   adjacent values to get each phase. Run it twice: the second is warmer. This is §8's budget for a
   real host.
3. **The hops:** `traceroute api.github.com` (or `mtr api.github.com` for a live, loss-annotated
   view). Count the hops and watch latency climb with distance.
4. **Reuse in action:** `curl -v https://api.github.com https://api.github.com` (two URLs, one
   command) and look for `Re-using existing connection` on the second — the handshakes vanish.
5. **In the browser:** DevTools → Network → click a request → *Timing* tab shows the exact same
   DNS/connect/TLS/TTFB (time-to-first-byte) waterfall for real page loads.

Deliverable: the four phase numbers for one cold and one warm request, and a one-line note on which
phase dominated and why.

---

## 11. Applied — the IPv6 question: adoption status, and why AWS bills you for IPv4

A reader question pushed §2b past the protocol into the real-world economics: *what is IPv6's actual
status? On AWS almost everything gets an IPv4 address, and a static IPv4 now costs extra — so can a
backend run purely on IPv6?* The answer is a useful map of where the transition really stands, and it
turns the abstract "IPv4 ran out" into a live architecture-and-cost decision.

**Adoption is split down the middle — and split by *side* of the connection.** The best public gauge,
Google's measurement of how many of its users arrive over IPv6, sits around **45–50%** in the
mid-2020s and climbs a few points a year. But the halves are lopsided by *who* you are: **eyeball and
mobile networks moved** (T-Mobile US runs IPv6-only internally with 464XLAT; large mobile carriers are
v6-heavy), while **enterprise and cloud *infrastructure* lag**. That asymmetry is exactly what you see
on AWS — the client side of the world is half-v6, the server side you build on is still v4-first.

**Why AWS shows IPv4 everywhere — and started charging for it.** A VPC (Virtual Private Cloud) is IPv4-first by design; IPv6
is opt-in (a dual-stack or IPv6-only subnet you enable deliberately), so every default template hands
out v4. Meanwhile IPv4 addresses became a *traded commodity* after exhaustion — a single address
trades for tens of dollars (roughly 30–60) and rising. So on **1 February 2024 AWS began charging
about 0.005 dollars per hour (\~3.6 dollars a month) for every public IPv4 address** — in-use ones too,
not just idle Elastic IPs — while **IPv6 addresses are free**. The price gap is a deliberate stick: it
prices in the real scarcity and nudges you toward v6. Your "pay extra for a static IPv4" is that
charge.

**Why IPv6 hasn't simply won** (the structural answer, deepening §2b):

1. **No backward compatibility.** A v6-only host cannot talk directly to a v4-only host — different
   wire formats. So you can't incrementally upgrade; through the whole transition you run *both* stacks
   (dual-stack), which is more work, not less. There's no individual first-mover reward, only a
   collective one — the single fact that keeps a 25-year-old protocol stuck at half.
2. **NAT defused the crisis.** Carrier-grade NAT let whole networks share one public v4 (the §2b NAT
   again), removing the scarcity urgency that would otherwise have forced migration.
3. **Chicken-and-egg → permanent dual-stack.** Content won't go v6-*only* while eyeballs are v4; ISPs
   keep v4 while content is v4. The stable equilibrium is dual-stack everywhere, not a switchover.

**Where v6 *does* win: when you personally run out of addresses.** Meta's data-center network has been
**IPv6-only since \~2015** — not ideology, but because they exhausted even *private* v4 space
(`10.0.0.0/8` is only about 16 million addresses; a hyperscaler blows through it). That's the tell for
the whole story: adoption follows real scarcity, and most people don't feel it.

**So — can an AWS backend run purely on IPv6?** The honest split, and the practical target:

- **Internal / east-west: yes.** IPv6-only subnets for compute, databases, and service-to-service
  traffic work today and shed the v4 charges.
- **Public ingress: no.** A v6-only endpoint is *unreachable* to the \~half of clients (and most
  corporate/guest networks) still on v4-only — you'd be silently invisible to them. Keep a **thin
  dual-stack edge** (CloudFront, an ALB — Application Load Balancer — or API Gateway) that terminates client IPv4 and forwards to
  the IPv6-only backend, concentrating v4 into a few *shared* edge addresses instead of one per
  instance.
- **Egress is the catch people miss.** An IPv6-only backend also can't *reach* IPv4-only destinations —
  and many third-party APIs still publish no `AAAA` record (quite possibly some of the LLM (large language model) providers a
  backend calls). AWS's fix is **NAT64 + DNS64**: Route 53 Resolver synthesizes an `AAAA`, the NAT
  Gateway translates the traffic to v4 on the way out — the mirror image of the dual-stack edge.

**Keeper:** *"purely IPv6, zero IPv4 anywhere" is not achievable for an app that both serves and calls
the public internet — but "**IPv6-only servers + a thin dual-stack edge + a NAT64 escape hatch**" is,
and it is precisely the cost-smart target the AWS pricing is steering you toward.* The whole IPv4→IPv6
saga in one line: **a protocol with no backward-compatibility, whose forcing function (scarcity) was
softened by NAT — so it migrates only where someone actually hits the wall.**

---

## Key terms (English · 大陆 简体 · 台灣 繁體)

| English | 大陆 (简体) | 台灣 (繁體) | Note |
|---|---|---|---|
| Network | 网络 | 網路 | ⚠ genuine split: 网络 (mainland) ↔ 網路 (Taiwan) |
| Protocol | 协议 | 協定 / 通訊協定 | ⚠ genuine split: 协议 ↔ 協定 |
| Server | 服务器 | 伺服器 | ⚠ genuine split: 服务器 ↔ 伺服器 |
| Packet | 数据包 | 封包 | ⚠ genuine split: 数据包 ↔ 封包 |
| Router | 路由器 | 路由器 | same |
| Handshake | 握手 | 握手 | same |
| Latency | 延迟 | 延遲 | script only |
| Bandwidth | 带宽 | 頻寬 | ⚠ genuine split: 带宽 ↔ 頻寬 |
| Round-trip time (RTT) | 往返时延 | 來回時間 / 往返時間 | ⚠ 往返时延 ↔ 來回時間 |
| Domain name resolution | 域名解析 | 網域名稱解析 | ⚠ 域名 ↔ 網域名稱 |
| Cache | 缓存 | 快取 | ⚠ genuine split: 缓存 ↔ 快取 |
| Port | 端口 | 連接埠 | ⚠ genuine split: 端口 ↔ 連接埠 |
| Encapsulation | 封装 | 封裝 | script only |
| Dual-stack (IPv4+IPv6) | 双栈 | 雙協定堆疊 / 雙堆疊 | ⚠ 双栈 ↔ 雙(協定)堆疊 (§11) |
| Address exhaustion | 地址耗尽 | 位址耗盡 | ⚠ genuine split: 地址 (mainland) ↔ 位址 (Taiwan) |

---

## References

- Cloudflare Learning Center — accessible, accurate primers on each piece:
  *What is DNS?* <https://www.cloudflare.com/learning/dns/what-is-dns/> ·
  *TLS handshake* <https://www.cloudflare.com/learning/ssl/what-happens-in-a-tls-handshake/> ·
  *What is QUIC / HTTP-3?* <https://www.cloudflare.com/learning/performance/what-is-http3/>
- High Performance Browser Networking, Ilya Grigorik (free online) — the definitive deep treatment of
  latency, TCP, TLS, HTTP/2. <https://hpbn.co/>
- The speed-of-light latency floor, illustrated — <https://hpbn.co/primer-on-latency-and-bandwidth/>
- IETF (Internet Engineering Task Force): TLS 1.3 (RFC 8446, 1-RTT/0-RTT) <https://datatracker.ietf.org/doc/html/rfc8446> ·
  QUIC (RFC 9000) <https://datatracker.ietf.org/doc/html/rfc9000> ·
  HTTP/3 (RFC 9114) <https://datatracker.ietf.org/doc/html/rfc9114>
- `curl` timing variables (`-w`) — <https://curl.se/docs/manpage.html#-w>

### What's next

This opens M02. Natural continuations inside the module:
- **Ch2 — HTTP deeply:** methods, status codes, headers, idempotency, caching, content negotiation —
  the application-layer message that step ④ above carries.
- **Ch3 — TLS & secure transport:** what the §5 handshake actually agrees on (certificates, the key
  exchange), deepened — and the bridge into M10 (security).
- **Ch4 — Real-time:** REST vs WebSockets vs SSE (Server-Sent Events) vs long-polling, and the NAT-idle-timeout/heartbeat
  story from §2b in full — closest to your arena work.

Or rotate scope: **M04 Ch3 (design patterns)** is teed up from Ch2, or **M01 Ch5** (OS landscape)
closes M01.
