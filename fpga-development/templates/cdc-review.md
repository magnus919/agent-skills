# Clock and CDC review

## Clock inventory

| Clock | Source | Frequency/phase | Reset release | Timing relation |
|---|---|---:|---|---|
| | | | | |

## Crossing inventory

| Signal/data | Source → destination | Kind | Protocol | Loss/duplication policy | Protection |
|---|---|---|---|---|---|
| | | level/pulse/bus/stream | | | |

## Evidence

- Synchronizer or FIFO implementation and target attributes:
- Gray encoder one-bit-transition assertion and pointer width/extra-wrap-bit convention:
- Gray-vector max-delay/bus-skew constraint, endpoint query, and post-route report:
- Per-domain reset synchronizer, release cycle, recovery/removal evidence, and PLL-lock dependency:
- Reset coordination:
- CDC tool/report/version:
- Timing constraints and exception rationale:
- Assertions/formal or directed tests:
- Reported violations and disposition:

## Gate

- Atomicity proven for multi-bit values: yes/no
- Pulse capture guaranteed under stated rate: yes/no
- Full/empty and overflow/underflow behavior tested: yes/no
- Any waiver: exact scope, owner, expiry, and evidence:
- Decision: PASS / FAIL / INCONCLUSIVE

## Review instructions

For a pulse, calculate the minimum event spacing and destination sampling opportunity. For a stream, calculate worst backlog from maximum producer minus minimum consumer rate and include reset recovery. For a bus, state how atomicity is preserved. Review reset reconvergence separately from steady-state transfer.

## Example decision

`FAIL`: a 100 MHz one-cycle pulse enters a 25 MHz domain through two flops; it may be missed. Replace with a toggle/handshake and test back-to-back events at the stated rate.
