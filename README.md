<h1 align="center">ddgr</h1>

<p align="center">
<a href="https://github.com/jarun/ddgr/releases/latest"><img src="https://img.shields.io/github/release/jarun/ddgr.svg?maxAge=600" alt="Latest release" /></a>
<a href="https://aur.archlinux.org/packages/ddgr"><img src="https://img.shields.io/aur/version/ddgr.svg?maxAge=600" alt="AUR" /></a>
<a href="http://formulae.brew.sh/formula/ddgr"><img src="https://img.shields.io/homebrew/v/ddgr.svg?maxAge=600" alt="Homebrew" /></a>
<a href="https://pypi.python.org/pypi/ddgr"><img src="https://img.shields.io/pypi/v/ddgr.svg?maxAge=600" alt="PyPI" /></a>
<a href="https://packages.debian.org/search?keywords=ddgr&searchon=names&exact=1"><img src="https://img.shields.io/badge/debian-10+-blue.svg?maxAge=2592000" alt="Debian Buster+" /></a>
<a href="https://apps.fedoraproject.org/packages/ddgr"><img src="https://img.shields.io/badge/fedora-26+-blue.svg?maxAge=2592000" alt="Fedora 26+" /></a>
<a href="https://software.opensuse.org/package/ddgr"><img src="https://img.shields.io/badge/opensuse%20leap-15.0+-blue.svg?maxAge=2592000" alt="openSUSE Leap 15.0+" /></a>
<a href="https://packages.ubuntu.com/search?keywords=ddgr&searchon=names&exact=1"><img src="https://img.shields.io/badge/ubuntu-18.04+-blue.svg?maxAge=2592000" alt="Ubuntu Bionic+" /></a>
</p>

<p align="center">
<a href="https://github.com/jarun/ddgr/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GPLv3-yellow.svg?maxAge=2592000" alt="License" /></a>
<a href="https://travis-ci.org/jarun/ddgr"><img src="https://travis-ci.org/jarun/ddgr.svg?branch=master" alt="Build Status" /></a>
</p>

<p align="center">
<a href="https://asciinema.org/a/212198"><img src="https://asciinema.org/a/212198.png" alt="Asciicast" width="734"/></a>
</p>

`ddgr` is a cmdline utility to search DuckDuckGo from the terminal. While [googler](https://github.com/jarun/googler) is extremely popular among cmdline users, in many forums the need of a similar utility for privacy-aware DuckDuckGo came up. [DuckDuckGo Bangs](https://duckduckgo.com/bang) are super-cool too! So here's `ddgr` for you!

Unlike the web interface, you can specify the number of search results you would like to see per page. It's more convenient than skimming through 30-odd search results per page. The default interface is carefully designed to use minimum space without sacrificing readability.

A big advantage of `ddgr` over `googler` is DuckDuckGo works over the Tor network.

`ddgr` isn't affiliated to DuckDuckGo in any way.

*Love smart and efficient utilities? Explore [my repositories](https://github.com/jarun?tab=repositories). Buy me a cup of coffee if they help you.*

<p align="center">
<a href="https://saythanks.io/to/jarun"><img src="https://img.shields.io/badge/say-thanks!-ff69b4.svg" /></a>
<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RMLTQ76JSXJ4Q"><img src="https://img.shields.io/badge/PayPal-donate-green.svg" alt="Donate via PayPal!" /></a>
</p>

### Table of contents

- [Features](#features)
- [Installation](#installation)
  - [Dependencies](#dependencies)
  - [From a package manager](#from-a-package-manager)
  - [Release packages](#release-packages)
  - [From source](#from-source)
  - [Running standalone](#running-standalone)
  - [Shell completion](#shell-completion)
- [Usage](#usage)
  - [Cmdline options](#cmdline-options)
  - [Configuration file](#configuration-file)
  - [Text-based browser integration](#text-based-browser-integration)
  - [Colors](#colors)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Collaborators](#collaborators)
- [In the Press](#in-the-press)

### Features

- Fast and clean (no ads, stray URLs or clutter), custom color
- Designed to deliver maximum readability at minimum space
- Instant answers (which appear in the html version of DDG)
- Specify the number of search results to show per page
- Navigate result pages from omniprompt, open URLs in browser
- Search and option completion scripts for Bash, Zsh and Fish
- DuckDuckGo Bang support (along with completion)
- Open the first result directly in browser (as in I'm Feeling Ducky)
- Non-stop searches: fire new searches at omniprompt without exiting
- Keywords (e.g. `filetype:mime`, `site:somesite.com`) support
- Limit search by time, specify region, disable safe search
- HTTPS proxy support, Do Not Track set, optionally disable User Agent
- Support custom url handler script or cmdline utility
- Comprehensive documentation, man page with handy usage examples
- Minimal dependencies

### Installation

#### Dependencies

`ddgr` requires Python 3.4 or later. Only the latest patch release of each minor version is supported.

`cjkwrap` is an _optional_ requirement to wrap CJK code points accurately.

To copy url to clipboard at the omniprompt, `ddgr` looks for `xsel` or `xclip` or `termux-clipboard-set` (in the same order) on Linux, `pbcopy` (default installed) on OS X, `clip` (default installed) on Windows and `clipboard` (default installed) on Haiku. It also supports GNU Screen and tmux copy-paste buffers in the absence of X11.

Note: v1.1 and below require the Python3 `requests` library to make HTTPS requests. This dependency is removed in the later releases.

#### From a package manager

- [AUR](https://aur.archlinux.org/packages/ddgr/) (`yay -S ddgr`)
- [Debian](https://packages.debian.org/search?keywords=ddgr&searchon=names&exact=1) (`apt-get install ddgr`)
- [Fedora](https://apps.fedoraproject.org/packages/ddgr) (`dnf install ddgr`)
- [FreeBSD](https://www.freshports.org/www/ddgr/) (`pkg install ddgr`)
- [Haiku](https://github.com/haikuports/haikuports/tree/master/www-client/ddgr) (`pkgman install ddgr`)
- [Homebrew](http://formulae.brew.sh/formula/ddgr) (`brew install ddgr`)
- [NixOS](https://github.com/NixOS/nixpkgs/tree/master/pkgs/applications/misc/ddgr) (`nix-env -i ddgr`)
- [openSUSE](https://software.opensuse.org/package/ddgr) (`zypper in ddgr`)
- [PyPI](https://pypi.org/project/ddgr/) (`pip3 install ddgr`)
- [Raspbian Testing](https://archive.raspbian.org/raspbian/pool/main/d/ddgr/) (`apt-get install ddgr`)
- [Slackware](http://slackbuilds.org/repository/14.2/network/ddgr/) (`slackpkg install ddgr`)
- [Snap Store](https://snapcraft.io/ddgr/) (`snap install ddgr`)
- [Source Mage](http://codex.sourcemage.org/test/utils/ddgr/) (`cast ddgr`)
- [Termux](https://pypi.org/project/ddgr/) (`pip3 install ddgr`)
- [Ubuntu](https://packages.ubuntu.com/search?keywords=ddgr&searchon=names&exact=1) (`apt-get install ddgr`)
- [Ubuntu PPA](https://launchpad.net/~twodopeshaggy/+archive/ubuntu/jarun/) (`apt-get install ddgr`)
- [Void Linux](https://github.com/void-linux/void-packages/tree/master/srcpkgs/ddgr) (`xbps-install -S ddgr`)

#### Release packages

Packages for Arch Linux, CentOS, Debian, Fedora, OpenSUSE Leap and Ubuntu are available with the [latest stable release](https://github.com/jarun/ddgr/releases/latest).

#### From source

If you have git installed, clone this repository. Otherwise download the [latest stable release](https://github.com/jarun/ddgr/releases/latest) or [development version](https://github.com/jarun/ddgr/archive/master.zip).

To install to the default location (`/usr/local`):

    $ sudo make install

To remove `ddgr` and associated docs, run

    $ sudo make uninstall

`PREFIX` is supported, in case you want to install to a different location.

#### Running standalone

`ddgr` is a standalone executable (and can run even on environments like Termux). From the containing directory:

    $ ./ddgr

#### Shell completion

Search keyword and option completion scripts for Bash, Fish and Zsh can be found in respective subdirectories of [`auto-completion/`](auto-completion). Please refer to your shell's manual for installation instructions.

### Usage

#### Cmdline options

```
usage: ddgr [-h] [-n N] [-r REG] [-C] [--colors COLORS] [-j] [-t SPAN]
            [-w SITE] [-x] [-p URI] [-I] [--unsafe] [--noua] [--json] [--gb]
            [--np] [--url-handler UTIL] [--show-browser-logs] [-v] [-d]
            [KEYWORD [KEYWORD ...]]

DuckDuckGo from the terminal.

positional arguments:
  KEYWORD               search keywords

optional arguments:
  -h, --help            show this help message and exit
  -n N, --num N         show N (0<=N<=25) results per page (default 10); N=0
                        shows actual number of results fetched per page
  -r REG, --reg REG     region-specific search e.g. 'us-en' for US (default);
                        visit https://duckduckgo.com/params
  -C, --nocolor         disable color output
  --colors COLORS       set output colors (see man page for details)
  -j, --ducky           open the first result in a web browser; implies --np
  -t SPAN, --time SPAN  time limit search [d (1 day), w (1 wk), m (1 month)]
  -w SITE, --site SITE  search sites using DuckDuckGo
  -x, --expand          Show complete url in search results
  -p URI, --proxy URI   tunnel traffic through an HTTPS proxy; URI format:
                        [http[s]://][user:pwd@]host[:port]
  -I, --noinstant       disable instant answer
  --unsafe              disable safe search
  --noua                disable user agent
  --json                output in JSON format; implies --np
  --gb, --gui-browser   open a bang directly in gui browser
  --np, --noprompt      perform search and exit, do not prompt
  --url-handler UTIL    custom script or cli utility to open results
  --show-browser-logs   do not suppress browser output (stdout and stderr)
  -v, --version         show program's version number and exit
  -d, --debug           enable debugging

omniprompt keys:
  n, p, f               fetch the next, prev or first set of search results
  index                 open the result corresponding to index in browser
  o [index|range|a ...] open space-separated result indices, ranges or all
  O [index|range|a ...] like key 'o', but try to open in a GUI browser
  d keywords            new DDG search for 'keywords' with original options
                        should be used to search omniprompt keys and indices
  x                     toggle url expansion
  c index               copy url to clipboard
  q, ^D, double Enter   exit ddgr
  ?                     show omniprompt help
  *                     other inputs are considered as new search keywords
```

#### Configuration file

`ddgr` doesn't have any! Use aliases, environment variables and auto-completion scripts.

#### Text-based browser integration

`ddgr` works out of the box with several text-based browsers if the `BROWSER` environment variable is set. For instance,

    $ export BROWSER=w3m

or for one-time use,

    $ BROWSER=w3m ddgr query

Due to certain graphical browsers spewing messages to the console, `ddgr` suppresses browser output by default unless `BROWSER` is set to one of the known text-based browsers: currently `elinks`, `links`, `lynx`, `w3m` or `www-browser`. If you use a different text-based browser, you will need to explicitly enable browser output with the `--show-browser-logs` option. If you believe your browser is popular enough, please submit an issue or pull request and we will consider whitelisting it. See the man page for more details on `--show-browser-logs`.

If you need to use a GUI browser with `BROWSER` set, use the omniprompt key `O`. `ddgr` will try to ignore text-based browsers and invoke a GUI browser. Browser logs are always suppressed with `O`.

#### Colors

The color configuration is similar to that of [`googler` colors](https://github.com/jarun/googler#colors). The default color string is `oCdgxy`. `ddgr` recognizes the environment variable `DDGR_COLORS`. Details are available in the `ddgr` man page.

### Examples

1. DuckDuckGo **hello world**:

       $ ddgr hello world
2. **I'm Feeling Ducky** search:

       $ ddgr -j lucky ducks
3. **DuckDuckGo Bang** search `hello world` in Wikipedia:

       $ ddgr !w hello world
       $ ddgr \!w hello world // bash-specific, need to escape ! on bash
    Bangs work at the omniprompt too. To look up bangs, visit https://duck‐duckgo.com/bang?#bangs-list.
4. **Bang alias** to fire from the cmdline, open results in a GUI browser and exit:

       alias bang='ddgr --gb --np'
       $ bang !w hello world
       $ bang \!w hello world // bash-specific, need to escape ! on bash
5. **Website specific** search:

       $ ddgr -w amazon.com digital camera
    Site specific search continues at omniprompt.
6. Search for a **specific file type**:

       $ ddgr instrumental filetype:mp3
7. Fetch results on IPL cricket from **India** in **English**:

       $ ddgr -r in-en IPL cricket
    To find your region parameter token visit https://duckduckgo.com/params.
8. Search **quoted text**:

       $ ddgr it\'s a \"beautiful world\" in spring
9. Show **complete urls** in search results (instead of only domain name):

       $ ddgr -x ddgr
10. Use a **custom color scheme**, e.g., one warm color scheme designed for Solarized Dark:

        $ ddgr --colors bjdxxy hello world
        $ DDGR_COLORS=bjdxxy ddgr hello world
11. Tunnel traffic through an **HTTPS proxy**, e.g., a local Privoxy instance listening on port 8118:

        $ ddgr --proxy localhost:8118 hello world
    By default the environment variable `https_proxy` (or `HTTPS_PROXY`) is used, if defined.
12. Look up `n`, `p`, `o`, `O`, `q`, `d keywords` or a result index at the **omniprompt**: as the omniprompt recognizes these keys or index strings as commands, you need to prefix them with `d`, e.g.,

        d n
        d g keywords
        d 1

### Troubleshooting

1. Some users have reported problems with a colored omniprompt (refer to issue [#40](https://github.com/jarun/ddgr/issues/40)) with iTerm2 on OS X. To force a plain omniprompt:

       export DISABLE_PROMPT_COLOR=1

### Collaborators

- [Arun Prakash Jana](https://github.com/jarun)
- [Johnathan Jenkins](https://github.com/shaggytwodope)
- [SZ Lin](https://github.com/szlin)
- [Alex Gontar](https://github.com/mosegontar)

Copyright © 2016-2018 [Arun Prakash Jana](mailto:engineerarun@gmail.com)

### In the Press

- [Fossbytes](https://fossbytes.com/search-duckduckgo-from-terminal-ddgr/)
- [Information Security Squad](http://itsecforu.ru/2017/11/21/%D0%BA%D0%B0%D0%BA-%D0%B8%D1%81%D0%BA%D0%B0%D1%82%D1%8C-%D0%B2-duckduckgo-%D0%B8%D0%B7-%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D0%BD%D0%BE%D0%B9-%D1%81%D1%82%D1%80%D0%BE%D0%BA%D0%B8-linux/)
- [LinOxide](https://linoxide.com/tools/search-duckduckgo-command-line/)
- [OMG! Ubuntu!](http://www.omgubuntu.co.uk/2017/11/duck-duck-go-terminal-app)
- [Tecmint](https://www.tecmint.com/search-duckduckgo-from-linux-terminal/)
