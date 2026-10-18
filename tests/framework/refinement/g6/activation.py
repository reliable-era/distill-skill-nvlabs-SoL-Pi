"""Explicit-v2 prompt and observed-context guards;no outcome-based filtering."""
import hashlib,json
PREFIX=b'/distill-sol-pi:efficient-coding '
def digest(data):return hashlib.sha256(data).hexdigest()
def prompt_bytes(task,arm):return (PREFIX if arm=='ours' else b'')+task
def input_bytes(task,arm):
    return (json.dumps(dict(type='user',message=dict(role='user',content=prompt_bytes(task,arm).decode())))+'\n').encode()
def plugin_guard(metadata,arm,amendment):
    expected=[dict(x) for x in amendment['builtin_plugins']]
    if arm=='ours':expected.append(dict(name='distill-sol-pi',path='/opt/g6/marketplace',source='distill-sol-pi@sol-pi-skills',version='1.0.0'))
    def normalize(p):return {k:p.get(k) for k in ('name','path','source','version')}
    actual=[normalize(p) for p in metadata['plugins']]
    if sorted(actual,key=lambda p:p['name'])!=sorted(expected,key=lambda p:p['name']):raise RuntimeError('Unapproved plugin set/source/version')
    skills=list(metadata['loaded_skills']);stock=set(amendment['stock_skills']);wanted=stock|({'distill-sol-pi:efficient-coding'} if arm=='ours' else set())
    if len(skills)!=len(set(skills)) or set(skills)!=wanted:raise RuntimeError('Stock skill availability drift')
    return actual

def expansion_evidence(path,task,skill,arm):
    body=skill.decode().split('---',2)[2].strip() if skill.startswith(b'---') else skill.decode().strip()
    texts=[];indices=[];first_assistant=None
    for n,line in enumerate(path.read_text(errors='replace').splitlines()):
        try:e=json.loads(line)
        except ValueError:continue
        if e.get('type')=='assistant' and first_assistant is None:first_assistant=n
        if e.get('type')!='user' or first_assistant is not None:continue
        message=e.get('message',{});content=message.get('content',[])
        if isinstance(content,str):content=[dict(type='text',text=content)]
        for b in content:
            if isinstance(b,dict) and b.get('type')=='text':texts.append(b.get('text',''));indices.append(n)
    context='\n'.join(texts);full=task.decode();task_exact=full in context;task_content=full.strip('\r\n') in context
    loaded=body in context
    return dict(activation_mode='explicit-v2',submitted_task_sha256=digest(task),submitted_prompt_sha256=digest(prompt_bytes(task,arm)),skill_body_sha256=digest(body.encode()),pre_assistant_user_event_indices=indices,full_task_content_observed=task_content,full_task_bytes_observed=task_exact,outer_newline_trimming_only=task_content and not task_exact,full_skill_body_observed=loaded,command_expansion_verified=(loaded and task_content) if arm=='ours' else task_content,task_evidence_scope='native root conversation JSONL user-context stream before first assistant;not SDK replay alone,init advertisement or model self-report')
