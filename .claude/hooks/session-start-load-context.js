#!/usr/bin/env node
// SessionStart hook. Prints a short, dense project grounding line so the model has immediate context.
// Uses spawnSync (argv array, no shell) and fs.readdirSync — no string-interpolated commands.
"use strict";

const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const repoRoot = process.env.CLAUDE_PROJECT_DIR || path.resolve(__dirname, "..", "..");

function safeRun(cmd, args) {
  try {
    const r = spawnSync(cmd, args, { cwd: repoRoot, encoding: "utf8" });
    if (r.status !== 0) return "(unavailable)";
    return (r.stdout || "").trim();
  } catch {
    return "(unavailable)";
  }
}

const lastCommit = safeRun("git", ["log", "-1", "--oneline"]);
const branch = safeRun("git", ["rev-parse", "--abbrev-ref", "HEAD"]);

let appCount = "(?)";
try {
  const appsDir = path.join(repoRoot, "apps");
  if (fs.existsSync(appsDir)) {
    const entries = fs.readdirSync(appsDir, { withFileTypes: true });
    appCount = String(entries.filter((e) => e.isDirectory()).length);
  }
} catch {}

let migrationStatus = "(no migrations)";
try {
  const r = spawnSync("python", ["manage.py", "showmigrations", "--plan"], {
    cwd: repoRoot,
    encoding: "utf8",
  });
  if (r.status === 0) {
    const lines = (r.stdout || "").trim().split("\n");
    const unapplied = lines.filter((l) => l.startsWith("[ ]"));
    migrationStatus =
      unapplied.length === 0
        ? "all applied"
        : `${unapplied.length} pending`;
  }
} catch {}

let pythonVer = "?";
try {
  const r = spawnSync("python", ["--version"], { encoding: "utf8" });
  if (r.status === 0) pythonVer = (r.stdout || r.stderr || "").replace(/^Python\s+/, "").trim();
} catch {}

const lines = [
  "Django backend (Python " + pythonVer + ")",
  "branch: " + branch,
  "last commit: " + lastCommit,
  "apps: " + appCount,
  "migrations: " + migrationStatus,
];
process.stdout.write(lines.join("\n") + "\n");
process.exit(0);
