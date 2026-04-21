---
name: end-of-month-mode
description: The mode to be used when the user says that this is around the end of the month. Orchestrate multiple subagents to perform thorough planning, implementation, security review and verification loop.
---

Follow the steps below to handle the tasks effectively:
1. Use subagent to thoroughly plan out the tasks. Return the implementation plan complete with technical details and confirmed critical decisions. The plan subagent should use askQuestion tool to clarify any uncertainties and important technical approach to the user. Important technical approach is anything that would affect the output's functional behavior, resiliency/security/robustness, and performance/reliability.
2. Immediately performs the implementation according to the plan on the main agent without ending the session. See AGENTS.md for more instructions regarding implementation.
3. When the implementation is complete, use subagent tool to run 2 subagents in parallel:
   a. Security review mode to perform a thorough security review of the implementation. Return a detailed report of any security issues found, estimated CVSS score, and recommended fixes.
   b. Verification mode to verify the changes by performing build, static analysis, and test automation. Return a detailed report of any verification issues found.
4. If any issues are found in either the security review or verification reports address the issues and repeat step 3 until no issues are found.
5. Once no issues are found, inform the user that the implementation is complete and has passed all security and verification checks.