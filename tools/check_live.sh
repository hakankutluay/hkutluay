#!/usr/bin/env bash
# Post-launch checks for hkutluay.com: every page, the redirects, the old App Store URLs, and email DNS.
# Usage: tools/check_live.sh        Exit status is non-zero if any check fails.
set -u
fail=0

# expect <url> <status> [text the redirect target must contain]
expect() {
  local url=$1 want=$2 target=${3:-} out code location
  out=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 20 "$url")
  code=${out%% *}
  location=${out#* }
  if [[ $code == "$want" && ( -z $target || $location == *"$target"* ) ]]; then
    echo "ok   $code $url${location:+ → ${location}}"
  else
    echo "FAIL $code $url${location:+ → ${location}} (wanted $want${target:+ → …${target}…})"
    fail=1
  fi
}

for path in / /chronolyze/ /chronolyze/privacy/ /chronolyze/support/ /reelo/ /reelo/privacy/ /reelo/support/ \
  /assets/site.css /sitemap.xml /robots.txt; do
  expect "https://hkutluay.com$path" 200
done
expect "https://hkutluay.com/chronolyze/no-such-page/" 404
expect "http://hkutluay.com/" 301 "https://hkutluay.com/"
expect "https://www.hkutluay.com/" 301 "hkutluay.com/"

# URLs the App Store listings point at today.
for old in chronolyze-site/privacy.html chronolyze-site/support.html reelo-site/privacy.html reelo-site/support.html; do
  expect "https://hakankutluay.github.io/$old" 301 "hkutluay.com/$old"
  expect "https://hkutluay.com/$old" 200
done

mx=$(dig +short MX hkutluay.com)
if grep -q "zoho.eu" <<<"$mx"; then
  echo "ok   MX still points at Zoho"
else
  echo "FAIL MX records changed: ${mx:-<none>}"
  fail=1
fi

exit $fail
