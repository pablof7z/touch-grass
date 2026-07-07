<p align="center">
  <img src="./banner.jpg" alt="Person organizing colorful sticky notes on a wall" width="100%">
</p>

# Stop Teaching The Same Lesson Twice

The first time you ask an agent to """report a bug""" or """do marketing research,""" some friction is expected.

The third time, friction is a tax.

`chief-of-staff` turns repeated asks into remembered operating patterns. It learns what """done""" looks like for you, where truth lives, when to ask, and when to keep going.

## The Hook

You should not have to write a perfect process before work starts.

The process should emerge from real work, then get better every time you use it.

## What Changes

| You used to... | Now the system... |
| --- | --- |
| Re-explain preferences | Carries them into the next run |
| Rebuild the same checklist | Starts from a named workflow |
| Correct the same output shape | Records the shape that worked |
| Wonder why last time was weird | Keeps lessons attached to the task type |

## Show, Don""'t Tell

First request:

> """Can you report this bug properly?"""

Later request:

> """Report another bug."""

The second one should already know the pattern: where to file it, what evidence matters, what not to ask, and what counts as useful.

That is the product.

## Best For

People who delegate messy real-world tasks, not just isolated commands.

If your requests repeat, this profile should make each repetition cheaper.

## Install

```bash
npx awesome-agents add pablof7z/touch-grass --agent chief-of-staff --harness tenex-edge
```

Banner source: see [`banner-source.md`](banner-source.md).
