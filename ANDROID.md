# multiply.by as an Android app (Google Play)

Notes for packaging the multiply.by games as an Android app, gathered on 2026-11-20. Nothing is
built yet. This file sits in the site's web folder, so nginx serves it at /ANDROID.md (as for every
.md file); it is tracked in git (listed in the repo's whitelist .gitignore).

## Decisions so far

- **Bundle the games inside the app**, not a Trusted Web Activity (TWA) of the website. The site
  will carry ads on About and Build It (not yet; none today); the games have none and never will.
  A TWA shows the whole origin, ads included. A bundled app ships only the game pages.
- **ABOUT and BUILD IT** (in every game's menu) open the phone's browser, outside the app, only
  behind a **parental gate** (for example "Ask a grown-up: what is 7 + 8?" with a typed answer).
  Google's Families policy is strict about children leaving a kids' app for pages with ads.
- **Build machine:** a Google Cloud VM, `android-build` (below). This web server can't build
  Android (1 GB RAM, no Java). GitHub Actions is the alternative (free, builds from the repo, key
  kept as a secret).

## Still to decide

- **Package name** (application id). It can never change after publishing. Suggested:
  `by.multiply.app`.
- **App name** on the phone and in the store. Today the web manifest says "multiply.by";
  something like "Multiply.by – Times Tables" reads better.
- **Developer account:** personal or organization (Functional AI Inc.), see Play requirements.
- Whether Divide (/divide/) and the older /match/ go in the app.

## How the app works (planned)

- A minimal Android app: one Activity with a full-screen WebView. No Capacitor or framework
  needed; Kotlin, Gradle, AndroidX `webkit`.
- **Same addresses inside the app.** `WebViewAssetLoader` from `androidx.webkit` answers requests
  for `https://multiply.by/...` from files in the app's assets (`setDomain("multiply.by")`, with a
  path handler for `/`). We own the domain, so using it here is fine. The result: pages load
  unchanged, with their absolute links working (the front page strip links to
  `https://multiply.by/train/` etc.), localStorage per origin works as on the website (saved
  progress, `multiply_last_game`), and SOURCE's relative `prompt.txt` link resolves to the bundled
  copy. No generated page is edited (the site's rule: never edit a generated page by hand).
- **Folder addresses need a custom path handler.** `WebViewAssetLoader.AssetsPathHandler` serves
  exact file paths only: it does not turn `/train/` (or `/`) into `/train/index.html`, as nginx
  does. Every link between pages is a folder address (the front page strip, HOME, the /games/
  tiles), so the app needs its own `PathHandler` that adds `index.html` to a path ending in `/`
  and sets the MIME type from the extension (`text/html`, `text/plain` for `prompt.txt`,
  `image/png`, ...). An address without the trailing slash (`/train`) should be redirected or
  served the same way.
- `shouldOverrideUrlLoading` / `shouldInterceptRequest` decide each address:
  - a bundled path: served from assets;
  - `/about/` or `/build-it/`: blocked in the WebView; the parental gate, then the browser
    (`Intent.ACTION_VIEW`);
  - any other site (share links, divide.by, ...): the browser, also behind the gate;
  - anything else under multiply.by that isn't bundled: a 404 page in the app.
- **Service worker:** the pages register `/sw.js` (through `pwa.js`). In the app it isn't needed
  (everything is local). Either let `/sw.js` 404 inside the app (registration fails quietly; check
  that it throws nothing to the console), or route service-worker requests through the same
  loader with `ServiceWorkerControllerCompat`. Simplest is the 404. The install prompt in
  `pwa.js` does nothing in a WebView anyway.
  - Checked in `pwa.js` (2026-11-20): `startOffline()` ends with `.catch(function () {})`, so a
    failed registration throws no JavaScript error. It also registers only when the page looks
    installed (`isInstalled()`) or a service worker is already registered, which a fresh WebView
    probably never does, so `/sw.js` may never be requested. Still check the console on a
    device: Chromium can log a failed request ("Failed to load resource: 404") even when the
    script catches it, and the play tests treat console errors as failures.
- WebView settings: JavaScript on, DOM storage on, `mediaPlaybackRequiresUserGesture = false`
  only if a game's sounds fail (the games start audio after a tap, so it should not be needed).
  The Web Audio chimes and the share menu should be checked on a real phone.
- The share button: `navigator.share` works in WebView only through a bridge. Without one, the
  games fall back to their desktop share menu or copy-link, which open other apps/sites: those
  must go through the parental gate too, or be hidden in the app.
  - **Simplest: hide sharing in the app.** Gating every share target (email, X, Facebook, ...)
    adds code for little use in a children's app. Hiding the share icon needs no edit to a
    generated page: inject a small CSS rule after each page loads
    (`WebViewCompat.addDocumentStartJavaScript`, or `evaluateJavascript` in `onPageFinished`),
    or have the custom path handler add it to the served HTML. Its selector must match every
    game's share icon, which each build names differently, so check every page. A safer
    alternative is a `navigator.share` bridge (a `@JavascriptInterface` that starts Android's
    share sheet behind the parental gate): the games then use their phone share path and the
    desktop menu never appears.
- Portrait orientation (as the web manifest), back button: WebView history back, then exit.

## What goes in the app

The pages and sizes on 2026-11-20 (each game is one self-contained HTML file):

| Page | Bytes |
|---|---|
| / (front page: base game + strip) | 69,825 |
| /base/ | 63,991 |
| /games/ | 17,915 |
| /monster/ | 83,358 |
| /train/ | 177,703 |
| /dino/ | 78,525 |
| /robot/ | 108,750 |
| /plane/ | 156,447 |
| /space/ | 385,380 |
| /chinese/ | 105,870 |
| /blocks/ | 120,701 |
| /evolution/ | 341,414 |
| /divide/ (if included) | 59,688 |

Plus each game's `prompt.txt` (SOURCE), `/prompt.txt` and `/base/prompt.txt`, the strip
thumbnails (`/thumbnails/*.png`), the /games/ screenshots (`/build-it/*.png`; together about
1.8 MB with the thumbnails), the icons and the manifest. About 4 MB in all: small for an app.

A script (to write) gathers the current live files into the app's `assets/` folder, so a release
is: run the script, build, upload. A new or rebuilt game reaches the app only with a new release
(the website updates instantly; the app does not).

## Build machine (Google Cloud VM `android-build`)

Created 2026-11-20 09:18 UTC by Claude Code (gcloud from the web server), for building the app.
**Keep it stopped when not building.**

### The VM

| Setting | Value |
|---|---|
| Name | `android-build` (instance id 7764053744562318987) |
| Project | `functional-ai` (gcloud account: the site owner's Google account) |
| Zone / region | `us-east1-b` / `us-east1` (the project's default) |
| Machine type | e2-standard-4: 4 vCPU, 16 GB RAM, standard (not preemptible / spot) |
| Boot disk | `android-build`, 50 GB pd-balanced, deleted with the VM (auto-delete on) |
| Image | Ubuntu 24.04 LTS, `ubuntu-2404-noble-amd64-v20261105` (family `ubuntu-2404-lts-amd64`, project `ubuntu-os-cloud`) |
| Network | `default` network and subnetwork; internal IP 10.142.15.228; an **ephemeral** external IP (a new one at every start; not needed: SSH goes through IAP) |
| Service account | the project's default Compute Engine account, default scopes (Storage read-only, Logging, Monitoring, ...) |
| Shielded VM | vTPM and integrity monitoring on, Secure Boot off (the defaults) |
| Maintenance | live migrate, automatic restart |
| Labels / network tags | none |
| Startup script | in the instance metadata, key `startup-script` (below) |

It was created with:

```
gcloud compute instances create android-build --zone=us-east1-b --machine-type=e2-standard-4 \
  --image-family=ubuntu-2404-lts-amd64 --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB --boot-disk-type=pd-balanced \
  --metadata-from-file=startup-script=startup.sh
```

### Cost

About $0.13 an hour while running (e2-standard-4 in us-east1). Stopped (TERMINATED), only the
50 GB disk is billed, about $5 a month. Deleting the VM deletes its disk too.

### What is installed (checked 2026-11-20)

- OpenJDK 17.0.21 (`openjdk-17-jdk-headless`), plus `unzip`, `zip`, `git`, `curl`.
- Android SDK in `/opt/android-sdk`: cmdline-tools (`cmdline-tools/latest`, from
  `commandlinetools-linux-11076708_latest.zip`), platform-tools 37.0.3, platforms android-35 and
  android-36, build-tools 35.0.0 and 36.0.0. SDK licenses accepted.
- Gradle 8.14.3 in `/opt/gradle-8.14.3` (link `/opt/gradle`).
- Environment for every login shell, `/etc/profile.d/android.sh`: `ANDROID_HOME` and
  `ANDROID_SDK_ROOT` = `/opt/android-sdk`; PATH adds the cmdline-tools, platform-tools and Gradle
  bin folders.
- Disk: 4.2 GB used of 48 GB.
- Setup log: `/var/log/android-setup.log` (ends with a SUMMARY block); marker file
  `/opt/android-setup.done`.

### History

1. Created; the startup script ran once (about 3 minutes), wrote its log and the marker, and
   powered the VM off.
2. Started again only to read the log (SSH without IAP hung; with `--tunnel-through-iap` it
   worked), then stopped. Status now: TERMINATED.

### Using it

```
gcloud compute instances start android-build --zone=us-east1-b
gcloud compute ssh android-build --zone=us-east1-b --tunnel-through-iap
gcloud compute instances stop android-build --zone=us-east1-b
gcloud compute instances describe android-build --zone=us-east1-b --format='value(status)'
```

- **SSH needs `--tunnel-through-iap`**; without it the connection hangs.
- Copy files with `gcloud compute scp --tunnel-through-iap ...` (e.g. the built `.aab` back).
- On a start, the startup script runs again but exits at once (the marker file exists), so the
  VM stays up.
- To delete it (VM and disk): `gcloud compute instances delete android-build --zone=us-east1-b`.

### The startup script (as installed in the metadata)

```bash
#!/bin/bash
# One-time setup of an Android build machine; powers the VM off when done.
# Later boots skip it (the marker file exists), so a started VM stays up for work.
MARK=/opt/android-setup.done
LOG=/var/log/android-setup.log
[ -f "$MARK" ] && exit 0
exec >>"$LOG" 2>&1
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y openjdk-17-jdk-headless unzip zip git curl

SDK=/opt/android-sdk
mkdir -p $SDK/cmdline-tools
cd /tmp
curl -fsSLo tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q tools.zip -d $SDK/cmdline-tools && mv $SDK/cmdline-tools/cmdline-tools $SDK/cmdline-tools/latest
SM=$SDK/cmdline-tools/latest/bin/sdkmanager
yes | $SM --sdk_root=$SDK --licenses >/dev/null
for p in "platform-tools" "platforms;android-35" "build-tools;35.0.0" "platforms;android-36" "build-tools;36.0.0"; do
  $SM --sdk_root=$SDK --install "$p" || echo "SKIPPED: $p"
done
yes | $SM --sdk_root=$SDK --update || true

GV=8.14.3
curl -fsSLo gradle.zip https://services.gradle.org/distributions/gradle-$GV-bin.zip && unzip -q gradle.zip -d /opt && ln -sfn /opt/gradle-$GV /opt/gradle

cat > /etc/profile.d/android.sh <<'P'
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH=$PATH:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:/opt/gradle/bin
P
chmod -R a+rX $SDK

set +x
echo "===== SUMMARY ====="
java -version 2>&1 | head -1
/opt/gradle/bin/gradle --version 2>/dev/null | grep '^Gradle'
$SM --sdk_root=$SDK --list_installed 2>/dev/null | grep -E 'platform|build-tools|cmdline'
df -h / | tail -1
echo "===== DONE ====="
touch "$MARK"
sync
poweroff
```

## Google Play requirements

- **Upload an Android App Bundle (`.aab`)**, not an APK; build an APK too, to install on a phone
  for testing.
- **Target SDK:** Play requires a recent target API level for new apps (35 at least; check the
  current rule when submitting). SDK 36 is installed.
- **Signing:** an upload key (keystore) that must be kept safe, outside the web server and the
  repo, with its password. Turn on **Play App Signing** (Google holds the app signing key; a lost
  upload key can then be reset).
- **Developer account:** $25 once. A new **personal** account must run a **closed test with at
  least 12 testers for 14 days** before publishing to everyone. An **organization** account
  (Functional AI Inc.) skips that but needs a D-U-N-S number.
- **Families policy** (an app for children): target-age declaration, content-rating
  questionnaire, data-safety form (the games collect nothing; progress stays on the phone), and a
  **privacy policy URL**. The site has no privacy policy page yet: one is needed.
- **Store listing:** 512 x 512 icon (have `icon-512.png`), 1024 x 500 feature graphic, at least 2
  phone screenshots (can be made from the live pages with Playwright), short and full
  descriptions.

## Fixes to the site before packaging

- The web manifest's "maskable" icon is the same image as the normal one; Android crops maskable
  icons to a circle or squircle, so its edges may be cut off. The app's launcher icon needs an
  adaptive icon (foreground with padding plus background): make one from `icon.svg`.

## Not chosen, and why

- **TWA (Bubblewrap or PWABuilder):** the easiest route (a signed `.aab` in minutes from
  pwabuilder.com, plus `/.well-known/assetlinks.json` on the site), but it shows the whole
  website, including the pages that will carry ads, and needs the network on first open.
- **Building on this web server:** not enough memory, no Java.
