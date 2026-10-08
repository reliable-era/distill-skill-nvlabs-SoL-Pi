"""Candidate 2 uses the identical matched-screen implementation and resources."""
import pathlib,sys
import run_candidate_screen as S
G=S.G
S.PLAN=G/'mechanisms/candidate-2-screen-plan.json'
S.wave=int(sys.argv[1]) if __name__=='__main__' else 1
S.E=G/('screen-candidate-2-wave-'+str(S.wave))

def window_end():
    import datetime,json,subprocess
    marker='candidate-2-wave-'+str(S.wave)+'-window.md'
    value=subprocess.check_output(['git','log','-1','--format=%H|%cI','--',marker],cwd=G,text=True,timeout=20).strip()
    if not value:raise RuntimeError('Candidate 2 window not committed')
    commit,stamp=value.split('|',1);start=datetime.datetime.fromisoformat(stamp);end=start+datetime.timedelta(hours=4)
    record={'window_commit':commit,'window_start':start.isoformat(),'window_end':end.isoformat(),'latest_start':(end-datetime.timedelta(hours=2)).isoformat(),'wave':S.wave,'candidate_index':2}
    path=S.E/'screen-window.json'
    if path.exists() and json.loads(path.read_text())!=record:raise RuntimeError('No implicit window renewal')
    path.write_text(json.dumps(record,indent=2)+'\n');return end.timestamp()

S.window_end=window_end

def controller():
    base=S.controller();base.driver_entries.append(pathlib.Path(__file__).resolve());return base

if __name__=='__main__':controller().main()
