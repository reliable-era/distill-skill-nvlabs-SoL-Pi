"""Draft prospective publicresource disclosure;not skill or solution guidance."""
NOTICE='''Evaluation resource limits (identical for every comparison arm):
This task has a maximum of 16 forwarded model requests and 600 seconds of actor wall time. Every forwarded request counts toward that limit. Requests beyond the limit are rejected locally. There is no actor retry or follow-up continuation. These limits do not change the task requirements or grading.
'''
def add_notice(instruction,guidance,skills=()):
 if not isinstance(instruction,str) or not isinstance(guidance,str) or any(not isinstance(s,str) for s in skills):raise TypeError('publicpromptinputs mustbe text')
 return instruction+'\n\n'+NOTICE+'\n'+guidance+'\n\nUse supplied skills in /skills. No subagents,compaction,web retrieval or external solutions. Work in /app.\n'+''.join('\n'+s for s in skills)
