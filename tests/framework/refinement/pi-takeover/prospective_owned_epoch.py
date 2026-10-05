"""Ownedscope/epoch-boundstop;neveractonstale globals orname-only identity."""
import json
from prospective_completion_drain import drain
from prospective_controller_cell import persist

def stop(session,context,docker,owned):
 if not isinstance(context,dict):raise RuntimeError('no current owned actor context')
 if (session.active,session.deadline)!=(context['arm'],context['deadline']):raise RuntimeError('actor epoch mismatch')
 if not context.get('container_id') or context['name'] not in owned:raise RuntimeError('actor creation/ownership unverified')
 before=json.loads(docker('inspect',context['name']))
 if len(before)!=1 or before[0]['Id']!=context['container_id'] or before[0]['Image']!=context['image']:raise RuntimeError('owned actor identity changed')
 docker('stop','-t','0',context['name']);after=json.loads(docker('inspect',context['name']))
 if len(after)!=1 or after[0]['Id']!=context['container_id'] or after[0]['Image']!=context['image'] or after[0]['State']['Running'] or after[0]['State'].get('Paused'):raise RuntimeError('owned stop not verified')
 return True

def finish_failure(session,context,docker,owned):
 # Withnocurrent/createdissuer don'ttouchANYcontainer;explicitunknown instead.
 if context is None:return {'drained':False,'usage_remains_unavailable':True,'reason':'no_current_context'}
 try:
  stop(session,context,docker,owned);receipt=drain(session)
 except Exception as e:receipt={'drained':False,'usage_remains_unavailable':True,'reason':type(e).__name__,'message':str(e)[:120]}
 context['row']['outer_failure_drain']=receipt;persist(context['path'],context['row']);return receipt
