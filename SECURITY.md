# Security policy

## What sauro does with the network

sauro fetches the URLs you give it and nothing else. It sends no telemetry and calls no
service of its own. The core runs no model. Fetched pages are stored locally, next to the
report, so a verdict can be reproduced later.

## Reporting a vulnerability

Do not open a public issue for a security problem. Use GitHub's private vulnerability
reporting on this repository (Security tab, "Report a vulnerability"). You will get an
acknowledgement within 72 hours and a plan within 14 days.

## What counts

- sauro fetching a URL it was not given
- sauro writing outside the directory it was told to write in
- a crafted page that makes sauro hang, crash, or consume unbounded memory
- a crafted page that makes sauro report Supported for a claim the page does not contain, in a
  way that a user could not see from the displayed span
- any secret or personal data leaving the machine

## What does not count

- sauro saying Unverifiable for a page behind a paywall or bot check. That is by design.
- A wrong verdict with the evidence span correctly displayed. That is a bug, not a
  vulnerability. Open a "Wrong verdict" issue.

## Supported versions

There is no release yet. Once there is, only the latest minor version gets fixes.
