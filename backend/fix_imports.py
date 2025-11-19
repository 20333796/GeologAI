#!/usr/bin/env python3
import glob
import re
import os

os.chdir(r'D:\GeologAI\backend')

# Find all Python files in api/endpoints
for filepath in glob.glob('app/api/endpoints/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix imports
    content = re.sub(
        r'from app\.core\.security import SecurityUtility(?!.*get_current_user)',
        'from app.core.security import get_current_user, get_current_admin, SecurityUtility',
        content
    )
    content = re.sub(
        r'from app\.core\.security import get_current_user(?!.*get_current_admin)',
        'from app.core.security import get_current_user, get_current_admin',
        content
    )
    
    # Fix dependencies - get_current_user
    content = re.sub(
        r'Depends\(SecurityUtility\.get_current_user\)',
        'Depends(get_current_user)',
        content
    )
    
    # Fix dependencies - get_current_admin
    content = re.sub(
        r'Depends\(SecurityUtility\.get_current_admin\)',
        'Depends(get_current_admin)',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filepath}')
    else:
        print(f'No changes needed in {filepath}')

print('Done!')
