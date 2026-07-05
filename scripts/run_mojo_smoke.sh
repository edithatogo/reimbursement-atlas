#!/usr/bin/env bash
set -euo pipefail
uv tool run --prerelease=allow --from mojo-compiler==1.0.0b2 mojo mojo/fixed_width_tokenizer.mojo
