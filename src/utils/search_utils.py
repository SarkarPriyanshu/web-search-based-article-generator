def rearrange_docs(documents,scores,top):
    urls_docs = list()
    top_docs = list()

    # Pair each document with its score
    doc_score_pairs = list(zip(documents, scores))

    # Sort pairs by score in descending order
    sorted_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

    # Select the top 4 documents
    for doc, score in sorted_pairs[:top]:
        top_docs.append(doc)
        urls_docs.append(doc.metadata['source'])

    return top_docs,urls_docs