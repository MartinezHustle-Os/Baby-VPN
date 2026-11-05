// Baby VPN: Facebook + Instagram allowed 40 minutes, blocked 40 minutes.
// Time zone: Asia/Shanghai (UTC+08:00); anchored at 00:00 China time.
// Called by Shadowrocket's SCRIPT rule whenever it evaluates a new connection.
// Never contacts outside services, reads private data, or changes other apps.
(function () {
  var host = (typeof $request !== "undefined" && $request.hostname
    ? String($request.hostname) : "").toLowerCase().replace(/\.$/, "");
  var domains = [
    "cdninstagram.com", "facebook.com", "facebook.net",
    "fb.com", "fb.me", "fbcdn.net", "fbsbx.com",
    "ig.me", "instagram.com", "m.me",
    "messenger.com", "messengerkids.com"
  ];
  var target = host.indexOf("facebook") !== -1 ||
               host.indexOf("instagram") !== -1;
  for (var i = 0; i < domains.length && !target; i++) {
    var d = domains[i];
    target = host === d ||
             host.slice(-(d.length + 1)) === "." + d;
  }
  // 80-minute cycle, China Standard Time. 00:00-00:39 ALLOW,
  // 00:40-01:19 BLOCK, repeat; missed windows do not carry over.
  var chinaMinutes = ((Math.floor(Date.now() / 60000) + 480) % 1440 + 1440) % 1440;
  var allow = chinaMinutes % 80 < 40;
  // Match only during the allowed period. Matching routes through PROXY.
  // At other times the later static REJECT rules deny Facebook/Instagram.
  $done({matched: target && allow});
})();
