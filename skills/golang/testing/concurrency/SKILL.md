---
name: go-concurrency-testing
description: Patterns for testing concurrent Go code - race detection, goroutine leaks, context cancellation
---

# Concurrency Testing

Testing concurrent code requires specific patterns to catch races, leaks, and cancellation bugs.

## Race Detection

Always run concurrent tests with `-race`:

```bash
go test -race ./...
```

Design tests that exercise concurrent paths:

```go
func Test_Cache_ConcurrentAccess(t *testing.T) {
    cache := NewCache()

    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(2)
        go func(key string) {
            defer wg.Done()
            cache.Set(key, "value")
        }(fmt.Sprintf("key-%d", i))
        go func(key string) {
            defer wg.Done()
            _ = cache.Get(key)
        }(fmt.Sprintf("key-%d", i))
    }
    wg.Wait()
}
```

## Goroutine Leak Detection

Check that functions don't leak goroutines:

```go
func Test_Worker_NoGoroutineLeak(t *testing.T) {
    before := runtime.NumGoroutine()

    w := NewWorker()
    w.Start()
    w.Process(task)
    w.Stop()

    // Allow goroutines to wind down
    time.Sleep(100 * time.Millisecond)

    after := runtime.NumGoroutine()
    if after > before+1 { // +1 tolerance for runtime goroutines
        t.Errorf("goroutine leak: before=%d after=%d", before, after)
    }
}
```

For more robust detection, use a polling approach:

```go
func assertNoGoroutineLeak(t *testing.T, before int) {
    t.Helper()
    deadline := time.Now().Add(2 * time.Second)
    for time.Now().Before(deadline) {
        after := runtime.NumGoroutine()
        if after <= before+1 {
            return
        }
        time.Sleep(50 * time.Millisecond)
    }
    t.Errorf("goroutine leak: started with %d, now %d", before, runtime.NumGoroutine())
}
```

## Context Cancellation

Test that functions respect context cancellation:

```go
func Test_Fetch_RespectsContextCancel(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    cancel() // cancel immediately

    _, err := Fetch(ctx, "key")
    if !errors.Is(err, context.Canceled) {
        t.Errorf("expected context.Canceled, got %v", err)
    }
}

func Test_Fetch_RespectsContextDeadline(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 1*time.Millisecond)
    defer cancel()

    time.Sleep(10 * time.Millisecond) // ensure deadline passes

    _, err := Fetch(ctx, "key")
    if !errors.Is(err, context.DeadlineExceeded) {
        t.Errorf("expected DeadlineExceeded, got %v", err)
    }
}
```

## Channel Tests

Test channel-based communication patterns:

```go
func Test_Producer_SendsAllItems(t *testing.T) {
    items := []string{"a", "b", "c"}
    ch := Producer(items)

    var received []string
    for item := range ch {
        received = append(received, item)
    }

    if len(received) != len(items) {
        t.Errorf("received %d items, want %d", len(received), len(items))
    }
}

func Test_Pipeline_ClosesOnContextCancel(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    ch := Pipeline(ctx, infiniteSource())

    // Read a few items
    <-ch
    <-ch

    cancel()

    // Channel should close after context cancellation
    select {
    case _, ok := <-ch:
        if ok {
            // May receive buffered items, that's fine
        }
    case <-time.After(time.Second):
        t.Error("channel not closed after context cancellation")
    }
}
```

## Concurrent Stress Tests

For functions that must be safe under concurrent access:

```go
func Test_Counter_ConcurrentIncrement(t *testing.T) {
    counter := NewCounter()
    n := 1000

    var wg sync.WaitGroup
    wg.Add(n)
    for i := 0; i < n; i++ {
        go func() {
            defer wg.Done()
            counter.Increment()
        }()
    }
    wg.Wait()

    if got := counter.Value(); got != n {
        t.Errorf("counter = %d, want %d (likely race condition)", got, n)
    }
}
```

## Common Mistakes

```go
// WRONG: Non-deterministic timing dependency
func Test_Async_Bad(t *testing.T) {
    go doWork()
    time.Sleep(100 * time.Millisecond) // fragile!
    checkResult(t)
}

// CORRECT: Use synchronization primitives
func Test_Async_Good(t *testing.T) {
    done := make(chan struct{})
    go func() {
        doWork()
        close(done)
    }()
    select {
    case <-done:
        checkResult(t)
    case <-time.After(5 * time.Second):
        t.Fatal("timed out waiting for work")
    }
}
```
