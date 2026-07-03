# Test-goblin compatibility profile

The repository originally reserved a `test-goblin` optional extra for future goblin-style generative, fuzzing and mutation workflows. During v6, the extra was converted from an unresolved placeholder package into a practical compatibility profile.

## Current extra

```toml
[project.optional-dependencies]
test-goblin = [
  "hypothesis>=6.148.0",
  "mutmut>=3.3.0",
  "pytest-randomly>=4.0.0",
]
```

## Rationale

The project needs adversarial testing behaviours more than it needs a specific package name. The current profile provides:

| Capability | Tool |
|---|---|
| Generative/property tests | Hypothesis |
| Mutation testing | mutmut |
| Order-sensitivity detection | pytest-randomly |

## Intended future direction

If a maintained Python test-goblin package or a better equivalent becomes available, add it to this profile rather than replacing the pytest/Hypothesis/mutmut foundation. The quality goal is stable: >90% library coverage plus property and mutation testing over high-risk parsers, normalisers, crosswalk scoring and licence gates.
