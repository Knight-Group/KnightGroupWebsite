import glob, os
svc = r'e:\KnightGroupWebsite\Services'
files = [f for f in glob.glob(svc + r'\*.html') if 'general-repairs' not in f]
bullet = chr(0x2713)
fixed_count = 0
for path in files:
    with open(path,'r',encoding='utf-8') as f:
        c = f.read()
    idx = c.find('service-list li::before')
    if idx >= 0:
        content_start = c.find("content: '", idx) + 10
        content_end = c.find("'", content_start)
        current = c[content_start:content_end]
        if current != bullet:
            c = c[:content_start] + bullet + c[content_end:]
            with open(path,'w',encoding='utf-8') as f:
                f.write(c)
            print('FIXED:', os.path.basename(path), 'was:', repr(current))
            fixed_count += 1
        else:
            print('OK:', os.path.basename(path))
    else:
        print('NO RULE:', os.path.basename(path))
print('Total fixed:', fixed_count)
