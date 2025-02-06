alias ls='ls --color=auto'
export GPG_TTY=$(tty)
export EDITOR=nano
source /opt/asdf-vm/asdf.sh
alias yt-dl='docker run \
                  --rm -i \
                  -e PGID=$(id -g) \
                  -e PUID=$(id -u) \
                  -v "$(pwd)":/workdir:rw \
                  mikenye/youtube-dl'
uptime
