# Research and Evidence

Use this reference when the guide contains current hours, prices, events,
transit, booking requirements, safety conditions, or recommendations that need
source support.

## Research boundary

Research the smallest set of facts needed to make the guide useful. Start from
the trip thesis and anchor candidates; do not create an encyclopedia of the
destination. Research should answer questions such as:

- Is the place open on the proposed day and at the proposed time?
- Does it require advance booking, a timed entry, a minimum spend, or a local
  account?
- How long does the transfer actually take for this route and pace?
- What does the stated price include, in which currency, and under what date or
  seating assumptions?
- Is the recommendation compatible with the travelers' stated constraints?

## Source hierarchy

Prefer sources in this order:

1. official venue, operator, museum, park, or restaurant page;
2. government, transit authority, or official tourism source;
3. official booking channel named by the operator;
4. a reputable local publication or specialist source for discovery and context;
5. community reports only as leads, never as sole support for a consequential
   current claim.

Use search results and aggregators to discover candidates, then open the primary
source before presenting a current fact. A source that only repeats another
listing is not independent confirmation.

## Evidence ledger

Store a source entry for every current or consequential claim:

```json
{
  "id": "S1",
  "title": "Official venue page",
  "url": "https://example.org/venue",
  "retrieved": "2026-08-07",
  "supports": ["opening hours", "reservation method"],
  "notes": "Hours vary by weekday; verify the holiday exception before booking."
}
```

Use the source IDs in the content model. The rendered guide should show a
compact source note near practical claims and a readable source list at the
end. Record retrieval dates in ISO format. If a source has no publication or
update date, say so rather than inventing freshness.

## Facts, inference, and uncertainty

Keep these categories distinct in both the model and prose:

- **Fact:** directly supported by a cited source.
- **Inference:** an editorial judgment about fit, sequence, or atmosphere.
- **Estimate:** a range derived from stated assumptions.
- **Unknown:** information the research could not verify.

Use language that reflects the category. “The operator lists…” is different from
“this should suit a slow morning.” “Budget approximately…” is different from a
promised total. Do not turn an inference into a fact by putting it in a table.

## Costs and reservations

Show currency, date assumptions, and what is included. Prefer ranges where price
changes by time, seating, season, or exchange rate. Distinguish:

- admission or cover charge;
- food and drink estimate;
- transportation;
- booking fee or minimum spend;
- refundable versus non-refundable commitment.

Do not book or purchase anything. A booking link is a pointer, not evidence that
availability exists. Mark availability as unverified unless the user or a
booking tool has explicitly confirmed it.

## Research stop conditions

Stop and report a limitation when:

- the only available evidence is stale or contradictory;
- a page is inaccessible and no authoritative alternative exists;
- an exact price, opening hour, or event schedule cannot be confirmed;
- the request would require visa, medical, legal, or safety advice beyond the
  source and agent's authority.

A useful guide can contain a clearly labeled unknown. It must not hide the gap
behind confident prose.
