import asyncio
import random

QWERTY_MAP = {
    'q': ['w', 'a', 's'], 'w': ['q', 'e', 'a', 's', 'd'], 'e': ['w', 'r', 's', 'd', 'f'],
    'r': ['e', 't', 'd', 'f', 'g'], 't': ['r', 'y', 'f', 'g', 'h'], 'y': ['t', 'u', 'g', 'h', 'j'],
    'u': ['y', 'i', 'h', 'j', 'k'], 'i': ['u', 'o', 'j', 'k', 'l'], 'o': ['i', 'p', 'k', 'l'],
    'p': ['o', 'l'], 'a': ['q', 'w', 's', 'z', 'x'], 's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
    'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'], 'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
    'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'], 'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
    'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm'], 'k': ['u', 'i', 'o', 'j', 'l', 'm'],
    'l': ['i', 'o', 'p', 'k'], 'z': ['a', 's', 'x'], 'x': ['z', 'a', 's', 'd', 'c'],
    'c': ['x', 's', 'd', 'f', 'v'], 'v': ['c', 'd', 'f', 'g', 'b'],
    'b': ['v', 'f', 'g', 'h', 'n'], 'n': ['b', 'g', 'h', 'j', 'm'], 'm': ['n', 'h', 'j', 'k']
}

async def apply_typo_logic(chars, i, mistake_rate, lazy_typo_rate, typo_count):
    calc_mistake = (mistake_rate / 100.0) if isinstance(mistake_rate, (int, float)) else 0.07
    calc_lazy = (lazy_typo_rate / 100.0) if isinstance(lazy_typo_rate, (int, float)) else 0.02
    
    if random.random() < calc_mistake and i < len(chars) - 1:
        target_char = chars[i].lower()
        if target_char in QWERTY_MAP:
            typo_char = random.choice(QWERTY_MAP[target_char])
        else:
            typo_char = random.choice('abcdefghijklmnopqrstuvwxyz')
        
        typo_count += 1
        if random.random() < calc_lazy:
            chars[i] = typo_char  
        else:
            await asyncio.sleep(random.uniform(0.1, 0.2)) 
            await asyncio.sleep(random.uniform(0.2, 0.5)) 
            await asyncio.sleep(random.uniform(0.1, 0.2)) 
            
    return typo_count
