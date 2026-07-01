---
name: human-like-browser-operator
description: Operating principles for driving a browser (via Playwright, the Claude in Chrome extension, or computer-use) carefully and reliably — observe before acting, verify after acting, pace interactions naturally, and confirm before irreversible actions. Always apply this whenever performing multi-step browser automation tasks like filling forms, posting content, or navigating multi-page flows, even if the user doesn't explicitly ask for it.
---

# Human-like browser operator

Operate a browser the way a careful, competent person would: reliability first, natural pacing second. Never sacrifice correctness just to look more human — the point of these principles is to make automation more robust, not to disguise it.

## Think before acting

Before every interaction: check whether the page is still loading, identify the correct element (don't blindly click the first match), and check for dialogs, cookie banners, or overlays that might be blocking the real target.

## Read pages before interacting

On arriving at a page, take a snapshot or screenshot and orient: headings, labels, visible buttons, overall layout. Don't assume page structure from memory of how a similar site usually looks — confirm it.

## Clicking and typing

- Single-click unless the task explicitly needs double-click, right-click, or drag.
- After clicking, wait for and confirm the resulting UI change or navigation before continuing — don't fire a second click because the page "feels slow."
- When filling text fields, click in, confirm focus, enter the text, then verify what was actually entered (via snapshot) before submitting — don't assume a fill succeeded.

## Waiting

Wait for observable signals (element visible, button enabled, spinner gone, network idle) rather than arbitrary fixed sleeps.

## Scrolling and navigation

Scroll incrementally toward the target rather than jumping straight to the bottom. After following a link, verify the destination matches what was expected before continuing the task.

## Forms

For each field: read the label, confirm the expected value, enter it, verify formatting. Before submitting, check for validation errors and confirm you're clicking the actually-intended submit button.

## Error recovery

If something unexpected happens (cookie banner, modal, login timeout, captcha, validation error, disabled button), read what's actually on the page and adapt. Never retry the identical failing action repeatedly without changing approach.

## Multi-step tasks

After every major action: observe the result, confirm it succeeded, then decide the next step. Don't plan a long chain of clicks upfront and execute them blind — re-evaluate after each consequential step.

## Respect user data and irreversible actions

Never submit forms, post content, send messages, delete data, or make purchases without the user's explicit confirmation for that specific action — a prior approval doesn't carry over to a new instance of the same action type. This mirrors the broader rule already in force for this environment: posting publicly, sending messages, and other irreversible actions always need a fresh go-ahead.

## Verification

Don't assume an action worked — check the page for the actual evidence (success message, updated state, new content visible, changed URL/title).

## What this skill is not

This is not about evading a platform's bot/automation detection. It does not add artificial delays, randomized mouse jitter, or other camouflage whose only purpose is to make scripted activity look human to anti-automation systems. If a site's own detection flags automated behavior, that's a signal about the underlying activity (e.g. posting frequency) to take seriously and slow down for — not something to mask.
