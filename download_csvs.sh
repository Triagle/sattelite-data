#!/bin/bash
seq -f "%02g" 0 53 | xargs -I{} htmltab https://planet4589.org/space/stats/star/spl{}/index.html --output spl{}.csv
