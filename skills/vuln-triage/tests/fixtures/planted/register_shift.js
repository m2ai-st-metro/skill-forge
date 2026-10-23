// Register-shift probes (JS): template-literal execSync, interpolated fetch.
const { execSync } = require("child_process");

function convert(userFile) {
  // probe: JS template-literal command injection
  return execSync(`convert ${userFile} out.png`);
}

async function pull(id) {
  // probe: SSRF via interpolated URL
  return fetch(`https://internal.example/${id}`);
}

async function proxy(req) {
  // probe: SSRF via property-access argument (must flag)
  return fetch(req.url);
}

function dynamic(userExpr) {
  // probe: JS eval on untrusted input
  return eval(userExpr);
}

function embedded(req) {
  // probe: dangerous call embedded mid-line (must flag under CMD_INJECTION)
  const out = process.env.DEBUG ? execSync(`echo ${req.body}`) : null;
  return out;
}

module.exports = { convert, pull, proxy, dynamic, embedded };
