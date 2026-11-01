"""Editorial constraints shared by planning and verification of episode 002."""
def archive_allowed(history,source,start):
    return source not in history or start-history[source]>60.0

def check_archive_spacing(scenes):
    history={}
    for scene in scenes:
        if scene['kind']!='archive':continue
        source=scene['asset_id']
        if not archive_allowed(history,source,scene['start']):
            raise ValueError(f"Archive continuation/reuse less than 60 seconds apart: {scene['id']} {source}")
        history[source]=scene['end']
    return True

def entrance_time(local,settle=1.2):
    """Clamp scene animation to its settled state; no modulo or restarts."""
    return min(max(0,local),settle)
