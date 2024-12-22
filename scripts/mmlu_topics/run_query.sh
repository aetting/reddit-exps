
parent=/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_corr #parent comes from MMLU/queries so no change based on data being searched
# parent=/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/debugging

# for queries in "$parent"/*
# for queries in /home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_corr/professional_medicine_test.txt
# do
#     echo $queries
#     fname="${queries##*/}"
#     qname="${fname%.*}"
#     echo $qname
#     cat $queries | dolma-search query \
#         -i indexed/merged_qa_prefiltered \
#         -q - \
#         > search_outputs/test_merged_qa_mp/${qname}2.jsonl
# done


dolma-search query \
    -i indexed/merged_qa_all_prefiltered \
    -q - \
    -d $parent \
    -o search_outputs/merged_qa_all_mp/ \
    -p 192
