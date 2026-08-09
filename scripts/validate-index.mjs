import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const html = readFileSync("index.html", "utf8");
const inlineScripts = [...html.matchAll(/<script(?!(?:[^>]*)\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
  .map((match) => match[1]);
const forbiddenTelemetryGraphics = [
  "telemetryHighlights",
  "jfMetricCards",
  "jf-controls",
  "Auto-refresh",
  "jf-skeleton",
];

if (inlineScripts.length === 0) {
  throw new Error("No inline scripts found in index.html.");
}

for (const forbidden of forbiddenTelemetryGraphics) {
  if (html.includes(forbidden)) {
    throw new Error(`Removed telemetry graphic marker is still present: ${forbidden}`);
  }
}

const extractedScriptPath = "/tmp/jafafa-inline.js";
writeFileSync(extractedScriptPath, inlineScripts.join("\n;\n"));
execFileSync("node", ["--check", extractedScriptPath], { stdio: "inherit" });
console.log(`Validated index.html with ${inlineScripts.length} inline script block(s).`);
