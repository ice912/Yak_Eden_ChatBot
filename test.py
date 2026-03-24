import os, json, re

path = 'c:/Users/admin/Desktop/ChatBot/userMedicationData.json'

try:
    content = open(path, encoding='utf-8').read().strip()
    m = re.search(r'\[.*\]', content, re.DOTALL)
    
    if m:
        print('Match found')
        json_str = m.group(0)
        
        # 유효하지 않은 마지막 쉼표 제거 (JSON 문법 오류 방지)
        json_str = re.sub(r',\s*\]', ']', json_str) 
        
        data = json.loads(json_str)
        print('Data loaded, len:', len(data))
    else:
        print('No match')
        
except Exception as e:
    print('Error:', e)
