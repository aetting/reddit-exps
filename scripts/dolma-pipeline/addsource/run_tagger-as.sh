dolma tag \
    --experiment rmdel \
    --documents 's3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/source-added/documents/*/*.gz' \
    --taggers  removed_deleted \
    --processes 128
