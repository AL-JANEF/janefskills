.PHONY: validate test evals benchmark gate package

validate:
	python3 scripts/forge.py validate

test:
	python3 -m unittest discover -s tests -t . -p 'test_*.py'

evals:
	python3 evals/run_routing_eval.py --check

benchmark:
	python3 benchmarks/context_benchmark.py --check

gate:
	python3 scripts/quality_gate.py

package: gate
	python3 scripts/package_release.py
