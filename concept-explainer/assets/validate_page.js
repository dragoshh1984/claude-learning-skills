// Validate an explainer page: JS syntax of inline scripts + KaTeX-render all math.
const fs = require("fs"), vm = require("vm");
const path = require("path");
const katex = require(path.join(__dirname, "vendor/katex/katex.min.js"));
const file = process.argv[2];
let html = fs.readFileSync(file, "utf8");
// strip vendored scripts (katex/hljs/autorender = first 4 <script>), keep the rest
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let errs = 0;
for (const [i, s] of scripts.entries()) {
  if (s.includes("katex") && i < 4 && s.length > 50000) continue; // vendored
  try { new vm.Script(s); } catch (e) { console.log(`SCRIPT ${i} SYNTAX ERROR: ${e.message}`); errs++; }
}
// math: work on content with scripts removed
const content = html.replace(/<script>[\s\S]*?<\/script>/g, "");
const exprs = [];
for (const m of content.matchAll(/\$\$([\s\S]+?)\$\$/g)) exprs.push([m[1], true]);
const noDisplay = content.replace(/\$\$[\s\S]+?\$\$/g, "");
for (const m of noDisplay.matchAll(/\$([^$\n]+?)\$/g)) exprs.push([m[1], false]);
const dec = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
for (const [ex, disp] of exprs) {
  try { katex.renderToString(dec(ex), { displayMode: disp, throwOnError: true }); }
  catch (e) { console.log(`KATEX ERROR in ${disp ? "$$" : "$"}${ex.slice(0, 70)}...: ${e.message.slice(0, 120)}`); errs++; }
}
console.log(`${file.split("/").slice(-2).join("/")}: ${scripts.length} scripts, ${exprs.length} math exprs, ${errs} errors`);
process.exit(errs ? 1 : 0);
