#!/usr/bin/env python3
"""
Streaming parser for trufflehog-report.json that redacts potential secrets
and produces a concise categorized summary.
Outputs:
 - trufflehog-summary.json  (structured summary)
 - trufflehog-summary.txt   (human-readable report)

Behavior:
 - Tries to parse the report as JSON array; if that fails, treats file as newline-delimited JSON.
 - Redacts strings by keeping first/last 6 chars and masking the middle.
 - Groups findings by 'reason' and collects counts + samples.
"""
import json
import os
import sys
from collections import defaultdict

INFILE = os.path.abspath('trufflehog-report.json')
OUT_JSON = 'trufflehog-summary.json'
OUT_TXT = 'trufflehog-summary.txt'
MAX_SAMPLES_PER_REASON = 10


def redact(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    if len(s) <= 12:
        return '<REDACTED>'
    return s[:6] + '...' + s[-6:]


def process_obj(obj, stats, samples):
    # trufflehog's keys vary; common ones: 'reason', 'stringsFound', 'path', 'entropy', 'detector'
    reason = obj.get('reason') or obj.get('detector') or 'unknown'
    stats[reason] += 1
    entry = {}
    # capture path/filename if present
    path = obj.get('path') or obj.get('pathOnDisk') or obj.get('file') or obj.get('stringsFoundPath')
    if path:
        entry['path'] = path
    # stringsFound can be list or single
    sf = obj.get('stringsFound') or obj.get('string') or obj.get('stringsFoundData') or []
    if isinstance(sf, list):
        redacted = [redact(s) for s in sf[:5]]
    else:
        redacted = [redact(sf)]
    entry['sample_strings'] = redacted
    # other helpful fields
    if 'entropy' in obj:
        entry['entropy'] = obj.get('entropy')
    if 'verified' in obj:
        entry['verified'] = obj.get('verified')
    if len(samples[reason]) < MAX_SAMPLES_PER_REASON:
        samples[reason].append(entry)


def main():
    if not os.path.exists(INFILE):
        print('trufflehog-report.json not found in cwd:', os.getcwd())
        sys.exit(2)

    stats = defaultdict(int)
    samples = defaultdict(list)
    total = 0

    # First try to load as a JSON array (may OOM for very large files)
    try:
        with open(INFILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            for obj in data:
                process_obj(obj, stats, samples)
                total += 1
    except Exception:
        # fallback to NDJSON parsing (line-by-line)
        with open(INFILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # try to find JSON object in line
                try:
                    obj = json.loads(line)
                    process_obj(obj, stats, samples)
                    total += 1
                    continue
                except Exception:
                    # attempt to find first '{' and last '}' and parse
                    start = line.find('{')
                    end = line.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        try:
                            obj = json.loads(line[start:end+1])
                            process_obj(obj, stats, samples)
                            total += 1
                            continue
                        except Exception:
                            pass
                    # otherwise skip line
                    continue

    # Build summary
    summary = {
        'total_findings': int(total),
        'by_reason': [],
    }
    for reason, count in sorted(stats.items(), key=lambda x: -x[1]):
        summary['by_reason'].append({
            'reason': reason,
            'count': int(count),
            'samples': samples.get(reason, [])
        })

    with open(OUT_JSON, 'w', encoding='utf-8') as outj:
        json.dump(summary, outj, indent=2)

    # Human-readable report
    with open(OUT_TXT, 'w', encoding='utf-8') as out:
        out.write('TruffleHog concise summary\n')
        out.write('='*60 + '\n')
        out.write(f"Total findings parsed: {summary['total_findings']}\n\n")
        for group in summary['by_reason']:
            out.write(f"Reason: {group['reason']}  —  Count: {group['count']}\n")
            out.write('-'*40 + '\n')
            for s in group['samples']:
                out.write(f"Path: {s.get('path','<unknown>')}\n")
                out.write(f"Sample strings: {s.get('sample_strings')}\n")
                if 'entropy' in s:
                    out.write(f"Entropy: {s['entropy']}\n")
                if 'verified' in s:
                    out.write(f"Verified: {s['verified']}\n")
                out.write('\n')
            out.write('\n')

    print('Summary written to', OUT_JSON, 'and', OUT_TXT)


if __name__ == '__main__':
    main()
