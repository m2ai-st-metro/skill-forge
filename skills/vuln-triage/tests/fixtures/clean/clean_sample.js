// Clean JS fixture: none of these lines may be flagged.
const { execFileSync } = require("child_process");

function listDir() {
  // execFile with array args, no shell string: not command injection
  return execFileSync("ls", ["-l"]);
}

async function status() {
  // constant URL: not SSRF
  return fetch("https://status.example.com/api");
}

module.exports = { listDir, status };
