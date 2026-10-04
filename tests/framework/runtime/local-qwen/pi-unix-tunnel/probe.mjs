// Exact pinned Pi-bundled SDK transport, dummy key, owned HTTP400 mock only.
import { OpenAI } from '/usr/local/lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/chunks/chunk-H3QXYIF7.js';
const client = new OpenAI({baseURL:'http://provider.example:8000/v1',apiKey:'dummy-not-a-real-secret',maxRetries:0,timeout:3000});
try { await client.chat.completions.create({model:'transport-mock-only',messages:[{role:'user',content:'owned mock routing diagnostic'}],stream:false}); process.exitCode=2; }
catch (error) { console.log(JSON.stringify({status:error.status??null,expectedMock400:error.status===400,errorType:error.name??null,errorMessage:String(error.message??'').slice(0,2048),causeType:error.cause?.name??null,causeMessage:String(error.cause?.message??'').slice(0,2048)})); if(error.status!==400) process.exitCode=3; }
