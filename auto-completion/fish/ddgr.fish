#
# Fish completion definition for ddgr.
#
# Author:
#   Arun Prakash Jana <engineerarun@gmail.com>
#

function __fish_ddgr_non_option_argument
    not string match -- "-*" (commandline -ct)
end

function __fish_ddgr_complete_query
    ddgr --complete (commandline -ct) ^/dev/null
end

complete -c ddgr -s h -l help            --description 'show help text and exit'
complete -c ddgr -s n -l num    -r       --description 'show N (0<=N<=25) results per page'
complete -c ddgr -s r -l reg    -r       --description 'region-specific search'
complete -c ddgr -s C -l nocolor         --description 'disable color output'
complete -c ddgr -l colors      -r       --description 'set output colors'
complete -c ddgr -s j -l ducky           --description 'open the first result in web browser'
complete -c ddgr -s t -l time            --description 'limit search duration (d/w/m)'
complete -c ddgr -s w -l site   -r       --description 'search a site using DuckDuckGo'
complete -c ddgr -s x -l expand          --description 'show complete URL in results'
complete -c ddgr -s p -l proxy  -r       --description 'specify proxy'
complete -c ddgr -l unsafe               --description 'disable strict search'
complete -c ddgr -l noua                 --description 'disable user agent'
complete -c ddgr -l json                 --description 'output in JSON format; implies --np]'
complete -c ddgr -l gb -l gui-browser    --description 'open a bang directly in gui browser'
complete -c ddgr -l np -l noprompt       --description 'perform search and exit'
complete -c ddgr -l url-handler -r       --description 'cli script or utility'
complete -c ddgr -l show-browser-logs    --description 'do not suppress browser output'
complete -c ddgr -s v -l version         --description 'show version number and exit'
complete -c ddgr -s d -l debug           --description 'enable debugging'
complete -c ddgr -n __fish_ddgr_non_option_argument -a '(__fish_ddgr_complete_query)'
