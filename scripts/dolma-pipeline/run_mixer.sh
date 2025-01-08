
# dolma -c configs/thread-mixer-qaall.yaml mix --processes 192
# rm -r testmixtmpd
# dolma -c configs/filter-subreddits-mix.yaml mix --processes 192 2>&1 | tee output-dense-sub-filter.log
dolma -c configs/filter-subreddits-mix.yaml mix --processes 192
