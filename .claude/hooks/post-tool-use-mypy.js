#!/usr/bin/env node
// PostToolUse hook. Runs mypy type-check on edited Python files.
// Only runs on .py files, skips migrations and __pycache__.
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  let input = {};
  try {
    input = raw.trim() ? JSON.parse(raw) : {};
  } catch {
    process.exit(0);
  }

  // Extract the file path from tool input
  const filePath =
    input.tool_input?.file_path ||
    input.tool_input?.path ||
    "";

  if (!filePath || !filePath.endsWith(".py")) process.exit(0);

  // Skip migrations, __pycache__, and test fixtures
  if (
    filePath.includes("/migrations/") ||
    filePath.includes("__pycache__") ||
    filePath.includes("/conftest.py")
  ) {
    process.exit(0);
  }

  const repoRoot = process.env.CLAUDE_PROJECT_DIR || path.resolve(__dirname, "..", "..");

  const r = spawnSync(
    "mypy",
    [
      "--no-error-summary",
      "--no-color-output",
      "--hide-error-context",
      "--show-error-codes",
      filePath,
    ],
    {
      cwd: repoRoot,
      encoding: "utf8",
      timeout: 30_000,
    }
  );

  if (r.status === 0) {
    process.exit(0);
  }

  // Only show first 10 lines of errors to avoid flooding
  const lines = ((r.stdout || "") + "\n" + (r.stderr || ""))
    .split("\n")
    .filter((l) => l.trim())
    .slice(0, 10);

  if (lines.length > 0) {
    process.stdout.write("\n[mypy] Type errors found:\n" + lines.join("\n") + "\n");
  }
  process.exit(0);
});
