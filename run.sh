i=0;

for fn in *.gz; do
    zcat $fn | python cnt.py $fn.pkl &
    pids[${i}]=$!
    i++
done

for job in `jobs -p`
do
    wait $job
done

python join.py *.pkl df.pkl
