#!/bin/bash

timeout=10
command="apt-get install -y cmake"
area="6"    # Asia
timezone="79"    # Tokyo

expect -c "
    set timeout ${timeout}
    spawn ${command}
    expect \"Geographic area: \"
    send \"${area}\n\"
    expect \"Time zone: \"
    send \"${timezone}\n\"
    expect \"root@\"
    exit 0
"
