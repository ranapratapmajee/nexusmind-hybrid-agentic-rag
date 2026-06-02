def semantic_chunk(text, max_chunk_size=1500, hard_cap=2500):
    paragraphs = text.split("\n\n")

    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # split very large paragraph
        if len(para) > hard_cap:
            if current:
                chunks.append(current.strip())
                current = ""

            for i in range(0, len(para), max_chunk_size):
                chunks.append(para[i : i + max_chunk_size])
            continue

        # normal chunking
        if len(current) + len(para) > max_chunk_size and current:
            chunks.append(current.strip())
            current = para
        else:
            current += ("\n\n" + para) if current else para

    if current:
        chunks.append(current.strip())

    return chunks
