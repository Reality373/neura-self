import random

def apply_syntax_variance(cmd, stealth_cfg):
    syn_cfg = stealth_cfg.get('syntax_variance', {})
    if not syn_cfg.get('enabled', False):
        return cmd

    cap_rate = syn_cfg.get('capitalization_rate', 20) / 100.0
    space_rate = syn_cfg.get('space_rate', 15) / 100.0
    
    if random.random() < space_rate:
        cmd = cmd.replace(" ", "  ", 1)
        
    if random.random() < cap_rate and len(cmd) > 0:
        chars = list(cmd)
        idx = random.randint(0, min(3, len(chars)-1))
        if chars[idx].islower():
            chars[idx] = chars[idx].upper()
        cmd = "".join(chars)

    return cmd
