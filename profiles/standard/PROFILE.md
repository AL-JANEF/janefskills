# Standard profile

The default for production engineering work. The router selects the minimum sufficient capabilities for the task (up to four plus their required dependencies), and verification depth follows the estimated risk.

## Operating rules

- Route first: classify the task, estimate risk, select capabilities, and state which were skipped.
- Verification follows estimated risk (floor `low`): the cheapest decisive check for a local change, focused tests plus repository gates at medium, and the full high tier once risk is high.
- Delegation is selective: one agent by default; bounded parallel work only when it has clear ownership and a net benefit.
- Independent defect-first review when risk is high or critical.
- When the estimated risk is high or critical, the profile escalates to `high-assurance` automatically and says so.
