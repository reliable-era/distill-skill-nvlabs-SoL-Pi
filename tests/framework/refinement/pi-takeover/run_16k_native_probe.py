"""NativeSDK/Unixbroker/threecapacityguardswithnew16Kaccounting,FAKEupstreamonly."""
import pathlib
import run_capacity_native_probe as template
R=pathlib.Path(__file__).resolve().parent;code=template.code
old='from prospective_broker_session import ProspectiveSession';assert code.count(old)==1
code=code.replace(old,"import sys\nsys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'development/pi-takeover-qwen-source-backed-16k/runtime'))\nfrom broker_session import ProspectiveSession")
code=code.replace('from prospective_reasoning_adapter import SOURCE_PINS,SOURCE,MODEL','from reasoning_adapter import SOURCE_PINS,SOURCE,MODEL')
code=code.replace('pi-takeover-qwen-incremental-coverage','pi-takeover-qwen-source-backed-16k')
code=code.replace("'max_output_tokens':8192","'max_output_tokens':16384").replace("'output_tokens':8190","'output_tokens':16382").replace("'total_tokens':16257","'total_tokens':24449").replace("'reasoning_tokens':8193","'reasoning_tokens':16385")
code=code.replace('solpi-native-capacity-v3-','solpi-native-16k-').replace('capacity-native-probe.json','16k-native-probe.json')
needle="report['passed']=report.get('native_exit')==0";assert code.count(needle)==1
code=code.replace(needle,"report['configured_output_cap']=16384;report['forwarded_output_cap']=json.loads(calls[0][2])['max_output_tokens'] if calls else None;report['raw_generation_status_incomplete']=True;report['fake_usage_is_not_model_billing']=True;"+needle)
needle="report['worker_exited'] and report.get('body_crossed_old_cap')";assert code.count(needle)==1;code=code.replace(needle,"report['worker_exited'] and report.get('forwarded_output_cap')==16384 and report.get('body_crossed_old_cap')")
compile(code,'16k-native-generated','exec')
if __name__=='__main__':exec(compile(code,'16k-native-generated','exec'),{'__name__':'__main__','__file__':str(__file__)})
