# JVC: discovery reference and gap

Accessed 2026-10-29. **Baseline/lead only; no camera modification qualified.** This is a bounded search result, not evidence that modification is impossible.

## Search and retained finding

Query: `JVC digital camera firmware hack reverse engineering`. Some legacy brands were searched together; this is weaker coverage than an individual model investigation.

Vendor support lists camera-control software and selected firmware downloads. No primary modification workflow was qualified.

Source route: [JVC primary baseline](https://www.jvc.com/global/support/). A transfer, ordinary firmware-update or official control entry does not establish feature patching or recoverability. No device test was performed.

## Next evidence

Resolve exact still-camera/camcorder model, transport and archived host software; vendor controls may address the need without firmware changes.

A future record needs exact stock identity, a primary implementation, its evidence level and an operation-specific recovery record before recommending a modification.

## Manufacturer completeness audit — 2026-10-29

Pro GY/KY cameras, consumer Everio/GZ/GC/GR digital models; exclude analog-only camcorders.

**Finding: coverage remains incomplete.** Five Singapore professional camcorder identities extracted. Official API found via search has family wildcards, not exact product identities; direct API-page capture was unavailable. Current and legacy consumer/pro regional catalogs have not been reconciled.

Official Camcorder Web API has a model-family/firmware/API-version matrix. No replacement firmware qualified.

Source checks: [jvc-api](https://www.jvc.com/ca/pro/professional-video/documents/manuals/jvccamcorderapireference-v120-public/) (unavailable), [jvc-cameras](https://www.jvc.com/global/pro/camcorders/) (unavailable), [jvc-consumer](https://www.jvc.com/global/download/camcorder.html) (unavailable), [jvc-models](https://www.jvc.com/usa/pro/professional-video/) (unavailable), [jvc-sg](https://www.jvc.com/sg/pro/professional-camcorders/) (retrieved). Retrieval status is recorded separately from relevance; an HTTP response is not source validation.

Model evidence, split by source type:

- [inventory-jvc-official-1](inventory-jvc-official-1.md)

The [audit method and remaining gaps](evidence-scope.md) explain the denominator and completion boundary.

## Additional official control route

[JVC Camcorder Web API v1.20](https://www.jvc.com/ca/pro/professional-video/documents/manuals/jvccamcorderapireference-v120-public/) was readable through search retrieval, although direct capture failed. Its compatibility table pairs API versions with firmware and GY-HM650/660/8x0/200/25x/280, GY-LS300, GY-HC900/5x0 and KY-PZ families. Wildcards are source family labels, not an assertion that every product or regional variant was tested. Preserve that firmware/API binding before designing a controller.
