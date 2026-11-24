# Violet Afterdark for interactive Zsh.
[[ -o interactive ]] || return 0

typeset -gU path
path=("$HOME/.local/bin" "${path[@]}")
if ! command -v brew >/dev/null 2>&1; then
    if [[ -x /opt/homebrew/bin/brew ]]; then
        path=(/opt/homebrew/bin /opt/homebrew/sbin "${path[@]}")
    elif [[ -x /usr/local/bin/brew ]]; then
        path=(/usr/local/bin /usr/local/sbin "${path[@]}")
    fi
fi

if command -v eza >/dev/null 2>&1; then
    export EZA_COLORS='di=1;38;2;181;108;255:ln=38;2;98;214;232:da=38;2;144;128;165'
    alias ls='eza --icons=auto --group-directories-first'
    alias ll='eza --icons=auto --group-directories-first --long --all --git --header'
    alias lt='eza --icons=auto --group-directories-first --tree --level=2'
fi

if command -v fzf >/dev/null 2>&1; then
    if [[ -z ${FZF_DEFAULT_OPTS:-} ]]; then
        export FZF_DEFAULT_OPTS='--height=45% --layout=reverse --border=rounded --color=bg:#0D0914,bg+:#211332,fg:#DDD5E8,hl:#B56CFF,hl+:#E06CDB,border:#67418C,pointer:#62D6E8'
    fi
    if [[ -z ${FZF_CTRL_T_OPTS:-} ]] && command -v bat >/dev/null 2>&1; then
        export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 -- {}' --preview-window=right:55%:hidden --bind=ctrl-/:toggle-preview"
    fi
    if _violet_fzf_init=$(fzf --zsh 2>/dev/null); then
        eval "$_violet_fzf_init"
    fi
    unset _violet_fzf_init
fi
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init zsh)"
fi

if command -v tmux >/dev/null 2>&1; then
    function t {
        if [[ -n ${TMUX:-} ]]; then
            print 'Already inside tmux. Ctrl-b, then w shows your windows; d detaches.'
        else
            tmux new-session -A -s dev
        fi
    }
fi

if command -v fastfetch >/dev/null 2>&1; then
    function violet-info {
        fastfetch --config "$HOME/.config/violet-macos/fastfetch.jsonc" "$@"
    }
fi

if command -v starship >/dev/null 2>&1; then
    export STARSHIP_CONFIG="$HOME/.config/violet-macos/starship.toml"
    eval "$(starship init zsh)"
fi
