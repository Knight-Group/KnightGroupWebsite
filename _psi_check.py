import urllib.request, json

url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://www.knightgroup.com&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req, timeout=90)
    data = json.loads(r.read())
    
    cats = data.get('lighthouseResult', {}).get('categories', {})
    for k, v in cats.items():
        print(f'{k}: {int(v["score"]*100)}')
    
    print('\n--- FAILING/WARNING AUDITS ---')
    audits = data.get('lighthouseResult', {}).get('audits', {})
    for k, v in sorted(audits.items(), key=lambda x: x[1].get('score', 1) if x[1].get('score') is not None else 1):
        score = v.get('score')
        if score is not None and score < 0.9:
            title = v.get('title', '')
            display = v.get('displayValue', '')
            desc = v.get('description', '')[:120]
            print(f'  [{int(score*100) if score else "FAIL"}] {title} | {display}')
            
            # Print item details if available
            details = v.get('details', {})
            items = details.get('items', [])
            for item in items[:3]:
                if isinstance(item, dict):
                    node = item.get('node', {})
                    url_val = item.get('url', item.get('source', ''))
                    label = item.get('label', node.get('snippet', url_val))
                    if label:
                        print(f'       -> {str(label)[:120]}')
    
    print('\n--- OPPORTUNITIES ---')
    for k, v in audits.items():
        score = v.get('score')
        if score is not None and score < 1 and v.get('details', {}).get('type') == 'opportunity':
            savings = v.get('details', {}).get('overallSavingsMs', 0)
            print(f'  Opportunity: {v["title"]} | saves ~{savings:.0f}ms')
            
except Exception as e:
    print(f'Error: {e}')
