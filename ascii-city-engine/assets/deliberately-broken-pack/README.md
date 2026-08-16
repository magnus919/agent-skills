# Deliberately broken city pack

This fixture is intentionally invalid. Its manifest has an empty tile list, an inverted x bound, and an invalid retrieval date. Run `python3 scripts/validate-city-pack.py assets/deliberately-broken-pack` from the skill directory to demonstrate deterministic `FAIL` output and a nonzero exit.
