---
name: Nested Pressable on web
description: Why nesting Pressable inside Pressable causes a React hydration error on web and how to fix it.
---

## Rule
Never nest a `<Pressable>` (or any other interactive element) inside another `<Pressable>` in this Expo app.

**Why:** On web, Expo renders `Pressable` as a `<button>`. Nesting `<button>` inside `<button>` is invalid HTML and triggers a React hydration error:
> "In HTML, button cannot be a descendant of <button>."

This silently works on native but breaks web preview.

**How to apply:** When a card or row needs an overall tap target *and* independent action buttons (e.g. "helpful", "delete"), wrap the whole card in a `<View>`, put a `<Pressable>` just around the tappable body content, and render the action buttons as *sibling* `<Pressable>`s below it — not children of the outer pressable.
