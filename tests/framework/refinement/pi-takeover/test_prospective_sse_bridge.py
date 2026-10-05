import copy,json,unittest
from prospective_sse_bridge import SSEBridge
from prospective_reasoning_adapter import SOURCE,SOURCE_PINS,MODEL
P={**SOURCE_PINS,'model':MODEL,'output_streamer_sha256':SOURCE,'speculative_algorithm':'DFLASH','speculative_num_draft_tokens':8,'peer':'127.0.0.1:18001'}
# Synthetic receipts:never claim token counts are real model or billing evidence.
END={'type':'response.completed','response':{'model':MODEL,'max_output_tokens':8192,'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},'usage':{'input_tokens':8067,'output_tokens':8190,'total_tokens':16257,'input_tokens_details':{'cached_tokens':0},'output_tokens_details':{'reasoning_tokens':8193}}}}
def frame(event,newline=b'\n'):return b'event: '+event['type'].encode()+newline+b'data: '+json.dumps(event,ensure_ascii=False).encode()+newline+newline
DELTA=frame({'type':'response.output_text.delta','delta':'unchanged \u4e2d\u6587 text'})
class Tests(unittest.TestCase):
 def bridge(self,wire,eof=True,provenance=P,chunk=1,emit=None):
  output=[];b=SSEBridge(emit or output.append)
  for pos in range(0,len(wire),chunk):b.feed(wire[pos:pos+chunk])
  return b,b.finish(eof,provenance),b''.join(output)
 def test_byte_fragmented_metadata_only(self):
  raw=DELTA+frame(END);b,v,client=self.bridge(raw);self.assertTrue(v['correction_applied']);self.assertEqual(v['raw_bytes'],raw);self.assertTrue(client.startswith(DELTA));event=b.parse(client[len(DELTA):]);expected=copy.deepcopy(END);expected['response']['usage']['output_tokens_details']['reasoning_tokens']=8190;self.assertEqual(event,expected);self.assertFalse(v['raw_cost']['protocol_valid']);self.assertFalse(v['derived_cost']['generation_complete']);self.assertEqual(v['derived_cost']['gross_tokens'],16257)
 def test_crlf(self):b,v,c=self.bridge(frame(END,b'\r\n'),chunk=7);self.assertTrue(v['correction_applied']);self.assertTrue(c.endswith(b'\r\n\r\n'))
 def test_terminal_waits_for_eof(self):
  out=[];b=SSEBridge(out.append);b.feed(DELTA);b.feed(frame(END));self.assertEqual(b''.join(out),DELTA);b.finish(True,P);self.assertGreater(len(b''.join(out)),len(DELTA))
 def test_no_eof_no_repair(self):raw=DELTA+frame(END);b,v,c=self.bridge(raw,eof=False);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_duplicate_terminal(self):raw=DELTA+frame(END)*2;b,v,c=self.bridge(raw);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_unknown_backend(self):p=dict(P,peer='127.0.0.1:9999');raw=DELTA+frame(END);b,v,c=self.bridge(raw,provenance=p);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_unsupported_overshoot(self):event=copy.deepcopy(END);event['response']['usage']['output_tokens_details']['reasoning_tokens']=8198;raw=frame(event);b,v,c=self.bridge(raw);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_partial_terminal(self):raw=DELTA+frame(END)[:-1];b,v,c=self.bridge(raw);self.assertFalse(v['correction_applied']);self.assertFalse(v['framing_complete']);self.assertEqual(c,raw)
 def test_malformed_data(self):raw=b'data: {garbage}\n\n'+frame(END);b,v,c=self.bridge(raw);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_multiline_data_unsupported(self):raw=b'data: {}\ndata: {}\n\n'+frame(END);b,v,c=self.bridge(raw);self.assertFalse(v['correction_applied']);self.assertEqual(c,raw)
 def test_disconnect_still_harvests(self):
  def detached(_):raise BrokenPipeError()
  raw=DELTA+frame(END);b,v,c=self.bridge(raw,emit=detached);self.assertTrue(v['consumer_detached']);self.assertTrue(v['correction_applied']);self.assertEqual(v['raw_bytes'],raw);self.assertFalse(v['broker_deployed'])
 def test_cap(self):b=SSEBridge(lambda _:None,max_bytes=3);self.assertRaises(ValueError,b.feed,b'abcd');self.assertEqual(bytes(b.raw),b'')
 def test_no_double_finalization(self):b,v,c=self.bridge(frame(END));self.assertRaises(ValueError,b.finish,True,P);self.assertRaises(ValueError,b.feed,b'')
if __name__=='__main__':unittest.main()
