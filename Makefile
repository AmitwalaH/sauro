# The check suite from PROJECT.md, so it is one command for people and for CI.

.PHONY: check fmt clippy test bench clean

check: fmt clippy test

fmt:
	cargo fmt --all -- --check

clippy:
	cargo clippy --all-targets --all-features -- -D warnings

test:
	cargo test --all

# Benchmark gate. Exists from task 3 onward; until then it says so and passes.
bench:
	@if cargo metadata --no-deps --format-version 1 2>/dev/null | grep -q '"sauro-bench"'; then \
		cargo run -p sauro-bench -- --check-baseline; \
	else \
		echo "sauro-bench not present yet (task 3)"; \
	fi

clean:
	cargo clean
