/*
 * BABY VPN - Facebook/Instagram access clock for Shadowrocket.
 *
 * 40 minutes allowed / 40 minutes blocked, repeating continuously.
 * Uses UTC (China is UTC+8 = six 80-minute periods later).
 * No remote request, no persistent timer, no update needed.
 *
 * [Rule] SCRIPT,BabySocialWindow,PROXY
 * [Script] BabySocialWindow = type=rule,engine=jsc,script-path=<this URL>,timeout=3
 * The original static FB/IG REJECT rules must follow the SCRIPT rule.
 */

// Facebook/Instagram domains only; Messenger and WhatsApp remain blocked.
const domains = [
  "facebook.com",
  "facebook.net",
  "fb.com",
  "fb.me",
  "fbcdn.net",
  "fbsbx.com",
  "instagram.com",
  "cdninstagram.com",
  "ig.me"
];

function isFacebookOrInstagram(hostname) {
  const host = String(hostname || "").toLowerCase().replace(/\.$/, "");
  if (!host) return false;
  if (host.includes("facebook") || host.includes("instagram")) return true;
  return domains.some(root => host === root || host.endsWith("." + root));
}

const requestHost = (typeof $request !== "undefined" && $request)
  ? $request.hostname
  : "";
const now = new Date();
const utcMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();
const allowedNow = (utcMinutes % 80) < 40;

// Only Facebook/Instagram matches cause PROXY; blocked windows fall through
// to the original REJECT rules, so errors fail closed for known domains.
$done({ matched: Boolean(allowedNow && isFacebookOrInstagram(requestHost)) });
