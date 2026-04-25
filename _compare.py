files = {
  "general-repairs": r"e:\KnightGroupWebsite\Services\general-repairs.html",
  "plumbing": r"e:\KnightGroupWebsite\Services\plumbing-services.html",
  "electrical": r"e:\KnightGroupWebsite\Services\electrical-work.html",
}
for name, path in files.items():
    raw = open(path,"rb").read()
    bom = raw[:3].hex()
    checkmark_pos = raw.find(b"\xe2\x9c\x93")
    pos2 = raw.find(b"service-list li::before")
    if pos2 > 0:
        cp = raw.find(b"content:", pos2) + 9
        print(name, "BOM:", bom, "checkmark_at:", checkmark_pos, "content bytes:", raw[cp+2:cp+6].hex())
    else:
        print(name, "NO RULE FOUND")
