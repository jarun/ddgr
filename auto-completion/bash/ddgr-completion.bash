#
# Rudimentary Bash completion definition for ddgr.
#
# Author:
#   Arun Prakash Jana <engineerarun@gmail.com>
#

_ddgr () {
    COMPREPLY=()
    local IFS=$' \n'
    local cur=$2 prev=$3
    local -a opts opts_with_args
    opts=(
        -h --help
        -n --num
        -r --reg
        -C --nocolor
        --colors
        -j --ducky
        -t --time
        -w --site
        -x --expand
        -p --proxy
        --unsafe
        --noua
        --json
        --gb --gui-browser
        --np --noprompt
        --url-handler
        --show-browser-logs
        -v --version
        -d --debug
    )
    opts_with_arg=(
        -n --num
        -r --reg
        --colors
        -t --time
        -w --site
        -p --proxy
        --url-handler
    )

    if [[ $cur == -* ]]; then
        # The current argument is an option -- complete option names.
        COMPREPLY=( $(compgen -W "${opts[*]}" -- "$cur") )
    else
        # Do not complete option arguments; only autocomplete positional
        # arguments (queries).
        for opt in "${opts_with_arg[@]}"; do
            [[ $opt == $prev ]] && return 1
        done

        local completion
        COMPREPLY=()
        while IFS= read -r completion; do
            # Quote spaces for `complete -W wordlist`
            COMPREPLY+=( "${completion// /\\ }" )
        done < <(ddgr --complete "$cur")
    fi

    return 0
}

complete -F _ddgr ddgr
