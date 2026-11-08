# Development-loop agent rules

Read [repository rules](../../docs/cs/AGENTS.md)
([English](../../docs/en/AGENTS.md)) and the
[agreed dev-loop policy](../../docs/cs/DEV_LOOP_POLICY.md)
([English](../../docs/en/DEV_LOOP_POLICY.md)) before changing this lab.
The policy also covers its explicitly delegated CI and documentation changes.

Within an owner-delegated bounded implementation task, the controller-maintenance
agent may create feature branches, scoped commits, pushes and draft PRs without
another approval for each operation. Preserve local work and stage exact paths.
This does not authorize merge, deployment, new unregistered tasks, data destruction,
budget expansion or changes to the product roadmap. The model worker itself has
no GitHub credentials or authority to operate Git.

Before any merge, inspect the actual head diff, test/CI evidence and outstanding
security findings. Only the owner can explicitly approve that merge. Never apply
an approval label on the owner's behalf or suppress checks to obtain approval.

Keep the user-operated service in one stable worktree with ignored local settings.
Do not replace or rebuild n8n for routine controller changes. Worker/checker
containers remain automatically created/removed by the controller. Treat Git rules
as agent guidance; preserve the actual code-enforced task/file/auth/isolation limits.
