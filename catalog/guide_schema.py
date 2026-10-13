"""Validate fixed teaching data without executing any memory skeleton."""


def text_size(value):
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(text_size(item) for item in value)
    if isinstance(value, dict):
        return sum(text_size(item) for item in value.values())
    return 0


def validate_guides(guides, expected_ids):
    if set(guides) != {str(pid) for pid in expected_ids}:
        raise ValueError('Guides must cover the complete catalog exactly')
    for pid, guide in guides.items():
        def text(value):
            if not isinstance(value, str) or not value.strip():
                raise ValueError('Guide #%s has missing text' % pid)

        if guide.get('version') != 2 or text_size(guide) < 1100:
            raise ValueError('Guide #%s must contain a complete authored lesson' % pid)
        text(guide['hook'])
        text(guide['goal'])
        recognition = guide['recognition']
        if len(recognition['signals']) < 2:
            raise ValueError('Guide #%s needs concrete recognition signals' % pid)
        for signal in recognition['signals']:
            text(signal)
        text(recognition['pattern'])
        text(recognition['why'])
        if not 3 <= len(guide['dialogue']) <= 5:
            raise ValueError('Guide #%s needs a progressive dialogue' % pid)
        for item in guide['dialogue']:
            for field in ('question', 'hint', 'answer'):
                text(item[field])
            if item['answer'] == item['hint']:
                raise ValueError('Guide #%s answer must develop the hint' % pid)
        walkthrough = guide['walkthrough']
        text(walkthrough['input'])
        text(walkthrough['conclusion'])
        if not 3 <= len(walkthrough['columns']) <= 4 or not 4 <= len(walkthrough['rows']) <= 8:
            raise ValueError('Guide #%s needs a worked state table' % pid)
        for column in walkthrough['columns']:
            text(column)
        for row in walkthrough['rows']:
            if len(row) != len(walkthrough['columns']):
                raise ValueError('Guide #%s state table has inconsistent columns' % pid)
            for cell in row:
                text(cell)
        for field in ('statement', 'reason'):
            text(guide['invariant'][field])
        recall = guide['recall']
        text(recall['mnemonic'])
        text(recall['skeleton'])
        if not 3 <= len(recall['steps']) <= 5:
            raise ValueError('Guide #%s needs a compact recall sequence' % pid)
        for step in recall['steps']:
            text(step)
        if len(guide['self_check']) < 2:
            raise ValueError('Guide #%s needs retrieval questions' % pid)
        for item in guide['self_check']:
            text(item['question'])
            text(item['answer'])
        for field in ('time', 'space', 'reason', 'optimality'):
            text(guide['complexity'][field])
    return guides
