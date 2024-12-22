dolma -c configs/dedupe-by-text.json dedupe --processes 192


# dolma dedupe \
#     --documents 's3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/source-added/documents/submissions/raw-00004-of-10060.jsonl.gz' \
#     --dedupe.paragraphs.attribute_name 'bff_duplicate_paragraph_spans' \
#     --dedupe.skip_empty \
#     --bloom_filter.file bf/deduper_bloom_filter.bin \
#     --bloom_filter.estimated_doc_count '50_000'\
#     --no-bloom_filter.read_only \
#     --bloom_filter.desired_false_positive_rate '0.0001' \
#     --processes 188

# 's3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/documents/*/*.gz'


# dolma dedupe \
#     --documents 's3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/source-added/documents/submissions/raw-00004-of-10060.jsonl.gz' \
#     --dedupe.paragraphs.attribute_name 'bff_duplicate_paragraph_spans' \
#     --dedupe.skip_empty \
#     --bloom_filter.file bf/deduper_bloom_filter.bin \
#     --bloom_filter.estimated_doc_count '17_100_000_000'\
#     --no-bloom_filter.read_only \
#     --bloom_filter.desired_false_positive_rate '0.0001' \
#     --processes 188