.PHONY: validate test check install-dry-run

validate:
	./scripts/validate.sh

test:
	./scripts/test.sh

check: validate test

install-dry-run:
	./scripts/install.py --target both --force --dry-run
