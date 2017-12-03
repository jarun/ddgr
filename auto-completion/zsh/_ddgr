#compdef ddgr
#
# Completion definition for ddgr.
#
# Author:
#   Arun Prakash Jana <engineerarun@gmail.com>
#

setopt localoptions noshwordsplit noksharrays

_ddgr_query_caching_policy () {
    # rebuild if cache is more than a day old
    local -a oldp
    oldp=( $1(Nm+1) )
    (( $#oldp ))
}

_ddgr_complete_query () {
    local prefix=$words[CURRENT]
    [[ -n $prefix && $prefix != -* ]] || return

    local cache_id=ddgr_$prefix
    zstyle -s :completion:${curcontext}: cache-policy update_policy
    [[ -z $update_policy ]] && zstyle :completion:${curcontext}: cache_policy _ddgr_query_caching_policy

    local -a completions
    if _cache_invalid $cache_id || ! _retrieve_cache $cache_id; then
        completions=( ${(f)"$(ddgr --complete $prefix 2>/dev/null)"} )
        _store_cache $cache_id completions
    fi

    compadd $@ -- $completions
}

local -a args
args=(
    '(- : *)'{-h,--help}'[show help text and exit]'
    '(-n --num)'{-n,--num}'[show N (0<=N<=25) results per page]:val'
    '(-r --reg)'{-r,--reg}'[region-specific search]:reg-lang'
    '(-C --nocolor)'{-C,--nocolor}'[disable color output]'
    '(--colors)--colors[set output colors]:six-letter string'
    '(-j --ducky)'{-j,--ducky}'[open the first result in web browser]'
    '(-t --time)'{-t,--time}'[limit search duration]:d/w/m'
    '(-w --site)'{-w,--site}'[search a site using DuckDuckGo]:domain'
    '(-x --expand)'{-x,--expand}'[show complete URL in results]'
    '(-p --proxy)'{-p,--proxy}'[specify proxy]:[http[s]://][user:pwd@]host[:port]'
    '(--unsafe)--noua[disable strict search]'
    '(--noua)--noua[disable user agent]'
    '(--json)--json[output in JSON format; implies --np]'
    '(--gb --gui-browser)'{--gb,--gui-browser}'[open a bang directly in gui browser]'
    '(--np --noprompt)'{--np,--noprompt}'[perform search and exit]'
    '(--url-handler)--url-handler[cli script or utility]:url opener'
    '(--show-browser-logs)--show-browser-logs[do not suppress browser output]'
    '(- : *)'{-v,--version}'[show version number and exit]'
    '(-d --debug)'{-d,--debug}'[enable debugging]'
    '*:::query:_ddgr_complete_query'
)
_arguments -S -s $args
