#!/bin/sh
# CI entry point: runs the whole pipeline; output is long.
python -m pipeline.stages 2>&1
