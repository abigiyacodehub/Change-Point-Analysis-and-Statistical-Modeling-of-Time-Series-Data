---
name: Playwright headless Chromium on Nix
description: System libraries and LD_LIBRARY_PATH quirks needed to run Playwright's headless Chromium inside the Replit NixOS container.
---

`pip install playwright && playwright install chromium` downloads the
browser fine, but launching it on the Replit NixOS container fails with
missing shared library errors unless the right Nix packages are present:

- First error: `libnspr4.so: cannot open shared object file` → install
  `nspr`, `nss` via `installSystemDependencies`.
- Second error (after adding those): `libgbm.so.1: cannot open shared
  object file` → `mesa` alone isn't enough; the actual lib lives in a
  `mesa-libgbm-*` store path that isn't automatically on
  `LD_LIBRARY_PATH`. Also needed: `at-spi2-core`, `cups`, `libdrm`,
  `libxkbcommon`, `alsa-lib`, `xorg.libXcomposite`, `xorg.libXdamage`,
  `xorg.libXfixes`, `xorg.libXrandr`, `xorg.libxshmfence`, `pango`,
  `cairo`.
- Even with those installed, launching still failed until
  `LD_LIBRARY_PATH` explicitly included the `mesa-libgbm-*` store path
  (found via `ls /nix/store/*mesa*/lib/libgbm*`) — prepend it to
  `LD_LIBRARY_PATH` in the same shell command that launches Playwright.

**Why:** Nix packages aren't on the dynamic linker's default search path
the way apt packages are; `installSystemDependencies` makes them
available in the environment but some binaries (like Playwright's
prebuilt Chromium) resolve dependent libraries via `LD_LIBRARY_PATH`
rather than an rpath that already points at the Nix store.

**How to apply:** Also note that `installSystemDependencies` reboots
workflows/dev servers — restart any manually-started background
processes (e.g. `nohup ... &`) after calling it, in the same or a
subsequent command, before trying to screenshot/hit them again.
