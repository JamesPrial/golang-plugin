---
name: go-property-testing
description: Property-based testing patterns using testing/quick and custom generators
---

# Property-Based Testing

Property-based testing verifies that invariants hold across many automatically generated inputs, rather than checking specific input/output pairs.

## When to Use Property Tests

- Functions with mathematical properties (commutativity, associativity)
- Invertible operations (encode/decode, serialize/deserialize)
- Functions where the output has known constraints regardless of input
- Complementary to table-driven tests — covers the space between known cases

## Using testing/quick

```go
import "testing/quick"

func Test_Encode_Decode_RoundTrip(t *testing.T) {
    roundTrip := func(input string) bool {
        encoded := Encode(input)
        decoded, err := Decode(encoded)
        if err != nil {
            return false
        }
        return decoded == input
    }

    if err := quick.Check(roundTrip, nil); err != nil {
        t.Error(err)
    }
}
```

## Common Properties to Test

| Property | Definition | Example |
|---|---|---|
| Round-trip | Decode(Encode(x)) == x | Serialization, compression |
| Idempotent | F(F(x)) == F(x) | Normalization, formatting |
| Commutative | F(a, b) == F(b, a) | Set operations, merge |
| Monotonic | a < b implies F(a) <= F(b) | Sorting, ranking |
| Invariant | P(F(x)) == true for all x | Length bounds, type constraints |
| Inverse | F(x) and G(x) undo each other | Add/Remove, Push/Pop |

## Custom Generators

When `testing/quick` can't generate your types automatically:

```go
// Implement quick.Generator for custom types
func (o Order) Generate(rand *rand.Rand, size int) reflect.Value {
    items := make([]Item, rand.Intn(size)+1)
    for i := range items {
        items[i] = Item{
            SKU:   fmt.Sprintf("SKU-%d", rand.Intn(1000)),
            Price: rand.Float64() * 100,
        }
    }
    return reflect.ValueOf(Order{
        ID:    fmt.Sprintf("ORD-%d", rand.Intn(10000)),
        Items: items,
    })
}
```

## Configuration

```go
// Increase iterations for thorough checking
config := &quick.Config{
    MaxCount: 1000,           // default is 100
    MaxCountScale: 0,         // multiplier
    Rand:     rand.New(rand.NewSource(42)), // deterministic for CI
}

if err := quick.Check(property, config); err != nil {
    t.Error(err)
}
```

## Combining with Table Tests

Property tests complement table-driven tests — they don't replace them:

```go
// Table test: specific known cases
func Test_Sort_KnownCases(t *testing.T) {
    tests := []struct{ input, want []int }{
        {[]int{3, 1, 2}, []int{1, 2, 3}},
        {nil, nil},
    }
    // ...
}

// Property test: invariants over random input
func Test_Sort_Properties(t *testing.T) {
    sorted := func(input []int) bool {
        result := Sort(input)
        // Property 1: output is same length
        if len(result) != len(input) { return false }
        // Property 2: output is ordered
        for i := 1; i < len(result); i++ {
            if result[i] < result[i-1] { return false }
        }
        return true
    }
    if err := quick.Check(sorted, nil); err != nil {
        t.Error(err)
    }
}
```
