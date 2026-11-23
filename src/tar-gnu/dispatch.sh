#!/bin/sh
# Todo el intérprete que tar llama: una vez por miembro regular, con los bytes del miembro por la entrada estándar.
# NO posee bucle, NI orden de categorías, NI dados, NI aritmética de "cuándo parar". Todo eso vive en el archivo:
# el orden de los miembros, el contenido de las tarjetas y un miembro `stop-over` que lleva el límite.
# Lo que sí posee es el significado de cinco palabras (begin, card, stop-over, show y "cualquier otra cosa es un error").
# Todo llega del archivo, así que todo se comprueba con un patrón estricto antes de usarse.
set -u
db=${TARPROG_DB:?TARPROG_DB must name the demo database}
name=${TAR_FILENAME-}
size=${TAR_SIZE:-0}

q() { sqlite3 "$db" "$@"; }   # fontanería de persistencia: un sqlite3 por miembro
# Un registro malo falla en modo cerrado. tar NO se detiene cuando esto sale con un estado distinto de cero (informa del estado y sigue
# con el siguiente miembro), así que el fallo también se escribe en la base de datos y todo miembro posterior se rechaza.
refuse() {
    echo "tarprog: refused '$name': $1" >&2
    [ -f "$db" ] && q "insert into trace(name, outcome) values ('$(printf %s "$name" | tr -cd 'A-Za-z0-9._-')', 'refused: $1');
                       update runs set faulted = 1 where id = (select max(id) from runs);" 2>/dev/null
    exit 1
}

[ "$size" -le 256 ] 2>/dev/null || refuse "member bigger than 256 bytes"
body=$(cat)   # diminuto, por la comprobación anterior

case $name in
    [0-9][0-9][0-9].begin|[0-9][0-9][0-9].card|[0-9][0-9][0-9].stop-over|[0-9][0-9][0-9].show) op=${name#???.} ;;
    *) refuse "unknown record type" ;;
esac

if [ "$op" != begin ]; then
    [ -f "$db" ] || refuse "no begin record yet"
    [ "$(q 'select faulted from runs order by id desc limit 1')" = 0 ] || refuse "an earlier record was refused"
fi

line() { printf '%s\n' "$body" | sed -n "$1p"; }
case $op in
begin)   # format=tarprog/1 / seed=N / label=DEMO ONLY
    [ "$(line 1)" = "format=tarprog/1" ] && [ "$(line 3)" = "label=DEMO ONLY" ] && [ -z "$(line 4)" ] || refuse "bad begin record"
    seed=$(line 2); case $seed in seed=[0-9]|seed=[0-9][0-9]*) seed=${seed#seed=} ;; *) refuse "bad seed" ;; esac
    case $seed in *[!0-9]*) refuse "bad seed" ;; esac
    q "create table if not exists runs(id integer primary key, seed integer not null, halted integer not null default 0,
         faulted integer not null default 0, demo_only integer not null default 1 check (demo_only = 1));
       create table if not exists demo_timecards(run_id integer not null, category text not null
         check (category in ('Meetings','Coding','Debugging','Learning')),
         hours integer not null check (hours between 10 and 19), running_total integer not null,
         week text not null, demo_only integer not null check (demo_only = 1));
       create table if not exists trace(n integer primary key, name text, outcome text);
       insert into runs(seed) values ($seed);"
    echo "# DEMO ONLY run $(q 'select max(id) from runs')"
    ;;
card)    # category=Name / hours=NN
    cat_=$(line 1); hrs=$(line 2)
    case $cat_ in category=Meetings|category=Coding|category=Debugging|category=Learning) cat_=${cat_#category=} ;; *) refuse "bad category" ;; esac
    case $hrs in hours=1[0-9]) hrs=${hrs#hours=} ;; *) refuse "bad hours" ;; esac
    [ -z "$(line 3)" ] || refuse "extra lines in card"
    week=$(date +%G-W%V)
    if [ "$(q 'select halted from runs order by id desc limit 1')" = 1 ]; then outcome="ignored: halted"
    else
        q "insert into demo_timecards select r.id, '$cat_', $hrs,
             $hrs + coalesce((select max(running_total) from demo_timecards where run_id = r.id), 0), '$week', 1
           from (select max(id) as id from runs) r;"
        outcome=ok
    fi
    ;;
stop-over)   # limit=N : detén la máquina si el total acumulado supera N
    lim=$(line 1); case $lim in limit=[0-9]|limit=[0-9][0-9]*) lim=${lim#limit=} ;; *) refuse "bad limit" ;; esac
    case $lim in *[!0-9]*) refuse "bad limit" ;; esac
    q "update runs set halted = 1 where id = (select max(id) from runs)
         and (select coalesce(max(running_total), 0) from demo_timecards where run_id = runs.id) > $lim;"
    outcome=ok
    ;;
show)
    run=$(q 'select max(id) from runs')
    q -separator '	' "select category, hours, running_total, week, 'DEMO ONLY' from demo_timecards where run_id = $run order by rowid;"
    echo "# committed total=$(q "select coalesce(max(running_total),0) from demo_timecards where run_id = $run") entries=$(q "select count(*) from demo_timecards where run_id = $run") DEMO ONLY"
    ;;
esac
q "insert into trace(name, outcome) values ('$name', '${outcome:-ok}');"
