# Data Model: Landing Page Design Polish

**Feature**: 002-landing-page-polish
**Date**: 2026-03-30

## Summary

No data model changes. This feature is purely UI/UX — no new entities, no Firestore changes, no server-side logic changes.

## i18n Message Keys (New)

The following keys must be added to all three locale files (`en.json`, `pt.json`, `es.json`):

| Key | Purpose | Example (EN) |
|-----|---------|-------------|
| `nav_features` | Navbar anchor link label | "Features" |
| `nav_pricing` | Navbar anchor link label | "Pricing" |
| `nav_waitlist` | Navbar anchor link label | "Waitlist" |
| `nav_menu_open` | Hamburger menu aria-label (open) | "Open menu" |
| `nav_menu_close` | Hamburger menu aria-label (close) | "Close menu" |
| `skip_to_content` | Skip link text | "Skip to main content" |
| `form_email_label` | Visually hidden input label | "Email address" |
| `pricing_join_waitlist` | CTA button on Free/PAYG cards | "Join the waitlist" |
| `pricing_popular_badge` | Badge on Pay-as-you-go card | "Most popular" |
| `hero_scroll_hint` | Scroll indicator aria-label | "Scroll down" |
| `hero_product_name` | Product name in hero | "The Loop" |

## Existing Keys Unchanged

All current message keys in `en.json`, `pt.json`, `es.json` remain unchanged.
