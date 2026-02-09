---
name: go-fuzz-testing
description: Go fuzz testing patterns using built-in fuzzing support (Go 1.18+)
---

# Fuzz Testing

Go 1.18+ includes native fuzz testing. Use fuzzing when functions handle external input, parse data, or validate untrusted content.

## When to Fuzz

- Parsers (JSON, XML, custom formats)
- Validators (input sanitization, boundary checks)
- Encoders/decoders (round-trip property)
- Any function that should never panic on arbitrary input

## Basic Fuzz Test

```go
func Fuzz_Parse(f *testing.F) {
    // Seed corpus: known interesting inputs
    f.Add([]byte(`{"valid": true}`))
    f.Add([]byte(`{}`))
    f.Add([]byte(``))
    f.Add([]byte(`null`))

    f.Fuzz(func(t *testing.T, data []byte) {
        // Invariant: Parse must never panic
        result, err := Parse(data)
        if err != nil {
            return // errors are acceptable
        }
        // If parse succeeds, result must be usable
        if result == nil {
            t.Error("Parse returned nil result without error")
        }
    })
}
```

## Fuzz Invariants

Every fuzz test must check at least one invariant:

| Invariant | Description | Example |
|---|---|---|
| No panics | Function never panics on any input | Parser, validator |
| Round-trip | Encode(Decode(x)) == x | Serialization |
| Idempotent | F(F(x)) == F(x) | Normalization |
| Bounded output | Output length/size within limits | Compression |
| Error or valid | Returns error OR valid result, never garbage | Any function |

## Seed Corpus Best Practices

- Include valid inputs (happy path)
- Include empty/nil/zero inputs
- Include boundary values (max length, max int)
- Include known-bad inputs that should produce errors
- Include real-world samples from production when available

## Running Fuzz Tests

```bash
# Run for 30 seconds
go test -fuzz=Fuzz_Parse -fuzztime=30s ./...

# Run until failure
go test -fuzz=Fuzz_Parse ./...

# Run specific fuzz test
go test -fuzz=^Fuzz_Parse$ -fuzztime=10s ./pkg/parser/
```

## Common Mistakes

```go
// WRONG: No invariant checked
f.Fuzz(func(t *testing.T, data []byte) {
    Parse(data) // just calling it isn't enough
})

// CORRECT: Check meaningful invariant
f.Fuzz(func(t *testing.T, data []byte) {
    result, err := Parse(data)
    if err == nil && result.Valid() == false {
        t.Error("Parse returned invalid result without error")
    }
})
```
