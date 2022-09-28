

# coords_ne = {(ne.begin, ne.end):ne.value for ne in cas.select('de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity')}

#print(coords_ne)

def label_categorizer(interval_token, interval_label) -> list:
    return [
        value for k, value in interval_label.items() if is_between(interval_token[0], interval_token[1], k)
    ]

def is_between(start, end, interval):
    return start >= interval[0] and end <= interval[1]

tokens = []
tags = []
is_first = True
chunk_prefix = {
    True: "B-",
    False: "I-",
    "Default": "O"
}
"""
with open('test.txt', mode='w', encoding='utf-8') as f:
    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        for token in cas.select_covered('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token', sentence):
            result_cat = label_categorizer((token.begin, token.end), coords_ne)
            mention = token.get_covered_text()
            if len(result_cat) > 0:
                tokens.append(token.get_covered_text())
                if is_first:
                    f.write(f"{mention}\t{chunk_prefix[is_first]}{result_cat[0]}\n")
                    #tags.append(f"B-{result_cat[0]}")
                    is_first = False
                else:
                    f.write(f"{mention}\t{chunk_prefix[is_first]}{result_cat[0]}\n")
                    #tags.append(f"I-{result_cat[0]}")
            else:
                f.write(f"{mention}\t{chunk_prefix['Default']}\n")
                #tokens.append(token.get_covered_text())
                #tags.append("O")
                is_first = True
        f.write("\n")
"""