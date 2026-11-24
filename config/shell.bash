# Violet Afterdark. Personal overrides belong in ~/.config/bash/local.bash.
case $- in *i*) ;; *) return ;; esac

HISTCONTROL=ignoreboth
HISTSIZE=50000
HISTFILESIZE=100000
shopt -s histappend cmdhist checkwinsize

_violet_path() {
    [ -d "$1" ] || return 0
    case ":$PATH:" in *":$1:"*) ;; *) export PATH="$1:$PATH" ;; esac
}
_violet_path "$HOME/bin"
_violet_path "$HOME/.local/bin"
_violet_path /opt/gcc-15.2/bin
unset -f _violet_path
if [ -d /opt/gcc-15.2/lib64 ]; then
    case ":${LD_LIBRARY_PATH:-}:" in
        *:/opt/gcc-15.2/lib64:*) ;;
        *) export LD_LIBRARY_PATH="/opt/gcc-15.2/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
    esac
fi
[ ! -r "$HOME/.cargo/env" ] || . "$HOME/.cargo/env"
if tty -s; then export GPG_TTY="$(tty)"; fi

export CLICOLOR=1
export LS_COLORS='di=1;38;2;181;108;255:ln=38;2;98;214;232:ex=38;2;123;217;173:fi=0:*.zip=38;2;224;108;219:*.tar=38;2;224;108;219:*.gz=38;2;224;108;219:*.jpg=38;2;224;108;219:*.png=38;2;224;108;219'
export EZA_COLORS='da=38;2;144;128;165:uu=38;2;181;108;255:gu=38;2;98;214;232'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
[ ! -x /usr/bin/lesspipe ] || eval "$(SHELL=/bin/sh lesspipe)"
if command -v eza >/dev/null 2>&1; then
    alias ls='eza --icons=auto --group-directories-first'
    alias ll='eza --icons=auto --group-directories-first --long --all --git --header'
    alias la='eza --icons=auto --group-directories-first --all'
    alias lt='eza --icons=auto --group-directories-first --tree --level=2'
else
    alias ls='ls --color=auto'
    alias ll='ls -lah'
    alias la='ls -A'
fi
alias l='ls'
alias ..='cd ..'
alias ...='cd ../..'
if command -v tmux >/dev/null 2>&1; then
    t() {
        if [ -n "${TMUX:-}" ]; then
            printf 'Already inside tmux. Ctrl-b, then w shows your windows; d detaches.\n'
        else
            tmux new-session -A -s dev
        fi
    }
fi
# Preserve the existing Ubuntu long-command notification shortcut.
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history | tail -n1 | sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'
if ! command -v bat >/dev/null 2>&1 && command -v batcat >/dev/null 2>&1; then
    alias bat=batcat
fi

if ! shopt -oq posix && [ -r /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
fi
export FZF_DEFAULT_OPTS='--height=45% --layout=reverse --border=rounded --info=inline --prompt=❯\  --pointer=▶ --marker=◆ --color=bg:#0D0914,bg+:#211332,fg:#DDD5E8,fg+:#F2EBFA,hl:#B56CFF,hl+:#E06CDB,border:#67418C,header:#9080A5,info:#9080A5,prompt:#B56CFF,pointer:#62D6E8,marker:#E06CDB,spinner:#62D6E8'
if command -v fzf >/dev/null 2>&1; then
    if command -v bat >/dev/null 2>&1; then
        export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 -- {}' --preview-window=right:55%:hidden --bind=ctrl-/:toggle-preview"
    fi
    # --bash is available in the pinned release. Support Ubuntu's older package too.
    if [ -r /usr/share/doc/fzf/examples/key-bindings.bash ] && [[ $(command -v fzf) == /usr/bin/* ]]; then
        . /usr/share/doc/fzf/examples/key-bindings.bash
        [ ! -r /usr/share/bash-completion/completions/fzf ] || . /usr/share/bash-completion/completions/fzf
    else
        eval "$(fzf --bash)"
    fi
fi
command -v zoxide >/dev/null 2>&1 && eval "$(zoxide init bash)"

# Defer NVM's startup cost until first use. Loading NVM restores its real functions.
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
_violet_nvm_path() {
    # Nested shells retain an explicitly selected version. Fresh shells resolve
    # the default so npm-installed executables (including Codex) work immediately.
    case ":$PATH:" in *":$NVM_DIR/versions/node/"*"/bin:"*) return ;; esac
    local version=default depth candidate
    local -a candidates
    for ((depth=0; depth<16; depth++)); do
        [ -r "$NVM_DIR/alias/$version" ] || break
        read -r version < "$NVM_DIR/alias/$version" || :
    done
    case "$version" in
        system) return ;;
        node|stable) version='v' ;;
        *)
            if [[ "$version" =~ ^v?[0-9]+(\.[0-9]+){0,2}$ ]]; then
                version="v${version#v}"
            else
                # Delegate unusual or unresolved aliases to NVM itself.
                . "$NVM_DIR/nvm.sh"
                return
            fi ;;
    esac
    if [ "$version" = v ]; then
        candidates=("$NVM_DIR/versions/node/"v[0-9]*)
    else
        candidates=("$NVM_DIR/versions/node/$version" "$NVM_DIR/versions/node/$version".*)
    fi
    while IFS= read -r candidate; do
        if [ -x "$candidate/bin/node" ]; then
            export PATH="$candidate/bin:$PATH"
            return
        fi
    done < <(printf '%s\n' "${candidates[@]}" | sort -Vr)
    # A missing default version must retain NVM's normal diagnostics/behavior.
    . "$NVM_DIR/nvm.sh"
}
if [ -s "$NVM_DIR/nvm.sh" ]; then _violet_nvm_path; fi
unset -f _violet_nvm_path
if [ -s "$NVM_DIR/nvm.sh" ] && ! declare -F nvm >/dev/null; then
    _violet_load_nvm() {
        unset -f nvm node npm npx corepack yarn pnpm
        . "$NVM_DIR/nvm.sh"
        [ ! -s "$NVM_DIR/bash_completion" ] || . "$NVM_DIR/bash_completion"
        unset -f _violet_load_nvm
    }
    nvm() { _violet_load_nvm; nvm "$@"; }
    node() { _violet_load_nvm; node "$@"; }
    npm() { _violet_load_nvm; npm "$@"; }
    npx() { _violet_load_nvm; npx "$@"; }
    corepack() { _violet_load_nvm; corepack "$@"; }
    yarn() { _violet_load_nvm; yarn "$@"; }
    pnpm() { _violet_load_nvm; pnpm "$@"; }
fi

# One compact greeting per inherited session; never print into redirected output.
if [ -z "${FASTFETCH_SHOWN:-}" ] && [ -t 1 ] && [ -z "${SSH_CONNECTION:-}" ] && [ "${VIOLET_GREETING:-1}" != 0 ]; then
    export FASTFETCH_SHOWN=1
    command -v fastfetch >/dev/null 2>&1 && fastfetch 2>/dev/null
fi
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
else
    PS1='\[\e[38;2;181;108;255m\]\w\[\e[0m\]\n❯ '
fi
[ ! -r "$HOME/.bash_aliases" ] || . "$HOME/.bash_aliases"
[ ! -r "$HOME/.config/bash/local.bash" ] || . "$HOME/.config/bash/local.bash"
