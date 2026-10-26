import {useEffect, useMemo, useState} from 'react'

const fmt = n => n == null ? '—' : new Intl.NumberFormat('vi-VN',{maximumFractionDigits:2}).format(n)
function label(b) {
  if(b===32)return '␣ (trắng)'
  if(b===10)return '↵ (xuống dòng)'
  if(b===13)return 'CR'
  if(b===9)return 'Tab'
  return b>=33 && b<=126 ? String.fromCharCode(b) : `0x${b.toString(16).padStart(2,'0').toUpperCase()}`
}
async function checked(response) {
  if(!response.ok){
    const text=await response.text()
    let message=`HTTP ${response.status}. Kiểm tra Flask và proxy /api.`
    try {message=JSON.parse(text).error || message} catch { /* HTML error */ }
    throw new Error(message)
  }
  return response
}
function save(blob, name) {
  const url=URL.createObjectURL(blob), a=document.createElement('a')
  a.href=url; a.download=name; document.body.appendChild(a); a.click();a.remove()
  setTimeout(()=>URL.revokeObjectURL(url),1000)
}
function FilePicker({id, accept, disabled, file, onChange}) {
  return <div className="file-picker">
    <input id={id} type="file" accept={accept} disabled={disabled} onChange={onChange} aria-describedby={id+'-name'}/>
    <span className="file-picker-button" aria-hidden="true">Chọn tệp</span>
    <span className="file-picker-name" id={id+'-name'} title={file?.name}>{file?.name || 'không có tệp'}</span>
  </div>
}

function Forest({data,step}) {
  const layout=useMemo(()=>{
    if(!data || data.root===null)return null
    const nodes=new Map(data.nodes.map(n=>[n.id,n]))
    const roots=step===0 ? data.nodes.filter(n=>n.symbol!==null).sort((a,b)=>a.freq-b.freq||a.id-b.id).map(n=>n.id) : data.steps[step-1].queue_after
    const points=[],edges=[];let cursor=0,depthMax=0
    function visit(id,depth){
      const n=nodes.get(id);depthMax=Math.max(depthMax,depth)
      let x
      if(n.symbol!==null){x=60+cursor*104;cursor++}
      else{
        const lx=visit(n.left,depth+1),rx=visit(n.right,depth+1)
        x=(lx+rx)/2
        edges.push({from:id,to:n.left,bit:0},{from:id,to:n.right,bit:1})
      }
      points.push({...n,x,y:60+depth*104});return x
    }
    for(const id of roots){visit(id,0);cursor+=0.4}
    return {points,edges,width:Math.max(640,cursor*104+50),height:Math.max(210,(depthMax+1)*104+40)}
  },[data,step])
  if(!layout)return <div className="empty">Dữ liệu rỗng không có cây Huffman.</div>
  const map=new Map(layout.points.map(n=>[n.id,n]))
  const merge=step>0?data.steps[step-1]:null
  return <div className="tree-scroll"><svg width={layout.width} height={layout.height} role="img" aria-label={`Cây Huffman sau ${step} lần gộp`}>
    {layout.edges.map(e=>{const a=map.get(e.from),b=map.get(e.to);return <g key={`${e.from}-${e.to}`}>
      <line x1={a.x} y1={a.y+22} x2={b.x} y2={b.y-22}/>
      <text className="edge-label" x={(a.x+b.x)/2+(e.bit?9:-9)} y={(a.y+b.y)/2}>{e.bit}</text>
    </g>})}
    {layout.points.map(n=><g key={n.id} transform={`translate(${n.x},${n.y})`} className={merge?.parent===n.id?'node new':merge&&(merge.left===n.id||merge.right===n.id)?'node chosen':'node'}>
      <title>{n.symbol===null?`Nút ${n.id}`:`${label(n.symbol)}: ${n.symbol}`} · Tần suất {n.freq}</title>
      <rect x="-38" y="-24" width="76" height="48" rx="14"/>
      <text y="5">{fmt(n.freq)}</text>
      <text className="node-caption" y="40">{n.symbol===null?`#${n.id}`:label(n.symbol)}</text>
    </g>)}
  </svg></div>
}

export default function App(){
  const [mode,setMode]=useState('text'),[text,setText]=useState(''),[file,setFile]=useState(null)
  const [data,setData]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[note,setNote]=useState('')
  const [step,setStep]=useState(0),[playing,setPlaying]=useState(false)
  const [packed,setPacked]=useState(null),[outName,setOutName]=useState('khoi-phuc.txt')
  const total=data?.steps.length??0
  useEffect(()=>{
    if(!playing)return
    if(step>=total){setPlaying(false);return}
    const timer=setTimeout(()=>setStep(s=>s+1),850)
    return ()=>clearTimeout(timer)
  },[playing,step,total])
  function reset(){setData(null);setError('');setNote('');setStep(0);setPlaying(false)}
  function inputBody(){
    if(mode==='text')return {headers:{'Content-Type':'application/json'},body:JSON.stringify({text})}
    if(!file)throw new Error('Hãy chọn tập tin trước.')
    if(file.size>16*1024*1024)throw new Error('Tập tin vượt giới hạn 16 MiB.')
    const form=new FormData();form.append('file',file);return {body:form}
  }
  async function run(action){
    setBusy(true);setError('');setNote('');setPlaying(false)
    try{
      const response=await checked(await fetch(`/api/${action}`,{method:'POST',...inputBody()}))
      if(action==='analyze'){
        const result=await response.json();setData(result);setStep(0)
      }else{
        save(await response.blob(),(mode==='text'?'vanban.txt':file.name)+'.huff')
        setNote('Đã tạo tập tin .huff. Bạn có thể mở lại và giải nén ở mục bên dưới.')
      }
    }catch(e){setError(e.message)}finally{setBusy(false)}
  }
  async function unpack(){
    setBusy(true);setError('');setNote('');setPlaying(false)
    try{
      if(!packed)throw new Error('Hãy chọn tập tin .huff.')
      const form=new FormData();form.append('file',packed);form.append('output_name',outName||'khoi-phuc.bin')
      const response=await checked(await fetch('/api/decompress',{method:'POST',body:form}))
      save(await response.blob(),outName||'khoi-phuc.bin')
      setNote('Giải nén thành công. Kích thước, tần suất và CRC đều đã được kiểm tra.')
    }catch(e){setError(e.message)}finally{setBusy(false)}
  }
  const stats=data?.stats
  const merge=step>0?data?.steps[step-1]:null
  const node=id=>data?.nodes.find(n=>n.id===id)
  return <div className="app-shell">
    <header><a className="brand" href="#"><strong>Huffman</strong><span>visualization</span></a></header>
    <main>
      <div className="intro"><div><h1>Mô Phỏng Thuật Toán<br/>Huffman.</h1></div><div className="intro-card"><span>VÍ DỤ BANANA</span><strong>48 <small>bit gốc</small> <b>→</b> 9 <small>bit mã</small></strong><p>Phần mã hóa · chưa tính header và bit đệm</p><div className="bit-ribbon">10 <i>0</i> 11 <i>0</i> 11 <i>0</i></div></div></div>
      <div className="workspace">
        <aside>
          <section className="panel input-panel"><div className="section-title"><span className="number">01</span><h2>Dữ liệu đầu vào</h2></div>
            <div className="tabs"><button disabled={busy} className={mode==='text'?'active':''} onClick={()=>{setMode('text');reset()}}>Văn bản</button><button disabled={busy} className={mode==='file'?'active':''} onClick={()=>{setMode('file');reset()}}>Tập tin</button></div>
            {mode==='text'?<><label htmlFor="text">Văn bản cần phân tích</label><textarea placeholder="nhập văn bản" id="text" value={text} disabled={busy} onChange={e=>{setText(e.target.value);reset()}} rows={6}/><button className="text-button" disabled={busy} onClick={()=>{setText('BANANA');reset()}}>Dùng ví dụ BANANA ↗</button></>:<div className="file-zone"><label htmlFor="source-file">Chọn tập tin bất kỳ</label><FilePicker id="source-file" disabled={busy} file={file} onChange={e=>{setFile(e.target.files?.[0]??null);reset()}}/>{file&&<p>{file.name}<br/>{fmt(file.size)} byte</p>}</div>}
            <div className="actions"><button className="primary" disabled={busy} onClick={()=>run('analyze')}>{busy?'Đang xử lý…':'Phân tích Huffman'}</button><button className="secondary" disabled={busy} onClick={()=>run('compress')}>Nén .huff</button></div>
          </section>
          <section className="panel decode-panel"><div className="section-title"><h2>Khôi phục tập tin</h2></div><p className="hint">Mở lại tập tin .huff</p>
            <label htmlFor="packed">Tập tin đã nén</label><FilePicker id="packed" accept=".huff" disabled={busy} file={packed} onChange={e=>{const f=e.target.files?.[0]??null;setPacked(f);if(f)setOutName(f.name.replace(/\.huff$/i,'')||'khoi-phuc.bin');setNote('');setError('')}}/>
            <label htmlFor="out-name">Tên tập tin khôi phục (kèm đuôi)</label><input id="out-name" value={outName} disabled={busy} onChange={e=>setOutName(e.target.value)}/>
            <button className="secondary wide" disabled={busy||!packed} onClick={unpack}>Giải nén</button>
          </section>
        </aside>
        <div className="results">
          {error&&<div role="alert" className="alert error">{error}</div>}{note&&<div role="status" className="alert success">{note}</div>}
          <section className="panel tree-panel"><div className="panel-heading"><div className="section-title"><span className="number">02</span><h2>Dựng cây Huffman</h2></div><span className="badge">TRÁI 0 · PHẢI 1</span></div>
            {!data?<div className="empty initial"><span className="simulation-placeholder">MÔ PHỎNG</span></div>:<>
              <div className="controls"><button disabled={step===0} onClick={()=>{setStep(0);setPlaying(false)}} title="Làm lại">↺</button><button disabled={step===0} onClick={()=>{setStep(s=>s-1);setPlaying(false)}}>← Trước</button><button className="play" disabled={!total} onClick={()=>{if(step===total)setStep(0);setPlaying(p=>!p)}}>{playing?'Ⅱ Dừng':'▶ Tự chạy'}</button><button disabled={step===total} onClick={()=>{setStep(s=>s+1);setPlaying(false)}}>Tiếp →</button><button disabled={step===total} onClick={()=>{setStep(total);setPlaying(false)}}>Cây cuối</button><span>{step} / {total}</span></div>
              <p className="step-note">{merge?`Gộp #${merge.left} (${node(merge.left).freq}) + #${merge.right} (${node(merge.right).freq}) → #${merge.parent} (${node(merge.parent).freq}).`:data.root===null?'Không có ký hiệu để gộp.':total===0?'Chỉ một byte khác nhau: quy ước mã là 0.':'Bắt đầu: các lá được sắp theo tần suất, sau đó theo ID.'}</p>
              <Forest data={data} step={step}/><div className="legend"><span>● Nút thường</span><span className="chosen-key">● Hai nút được chọn</span><span className="new-key">● Nút mới</span><small>Kéo ngang để xem cây lớn.</small></div>
            </>}
          </section>
          {data&&<>
            <section className="comparison" aria-labelledby="comparison-title"><h2 id="comparison-title">So sánh</h2><div className="stats-grid"><div><span>DỮ LIỆU GỐC</span><strong>{fmt(stats.original_bytes)} <small>byte</small></strong></div><div><span>PHẦN MÃ HÓA</span><strong>{fmt(stats.encoded_bits)} <small>bit</small></strong></div><div><span>TẬP TIN .HUFF</span><strong>{fmt(stats.compressed_bytes)} <small>byte</small></strong></div><div><span>{stats.saving_percent<0?'TĂNG DUNG LƯỢNG':'TIẾT KIỆM THỰC TẾ'}</span><strong className={stats.saving_percent<0?'negative':'positive'}>{stats.saving_percent==null?'—':`${fmt(Math.abs(stats.saving_percent))}%`}</strong></div></div></section>
            <section className="panel"><div className="section-title"><span className="number">03</span><h2>Bảng mã & dữ liệu</h2></div>
              <div className="table-scroll"><table><thead><tr><th>Ký hiệu : byte</th><th>Tần suất</th><th>Tỷ lệ</th><th>Mã Huffman</th><th>Số bit</th></tr></thead><tbody>{data.codes.map(c=><tr key={c.symbol}><td><strong>{label(c.symbol)}</strong> : {c.symbol}</td><td>{fmt(data.frequencies[c.symbol])}</td><td>{fmt(data.frequencies[c.symbol]/data.original_size*100)}%</td><td className="mono code-cell">{c.bits}</td><td>{c.bits.length}</td></tr>)}</tbody></table>{!data.codes.length&&<p>Dữ liệu rỗng: không có bảng mã.</p>}</div>
              <details><summary>Xem byte đầu vào ({data.preview_bytes.length} byte đầu)</summary><pre>{data.preview_bytes.map(b=>`${label(b)}: ${b} → ${b.toString(2).padStart(8,'0')}`).join('\n')||'(Rỗng)'}</pre><p className="hint">Nhị phân 8 bit ở đây là byte gốc, chưa phải mã Huffman.</p></details>
              <div className="encoded"><label>Chuỗi mã hóa {data.encoded_preview_truncated?'· 256 bit đầu':''}</label><p className="mono">{data.encoded_preview||'(Rỗng)'}</p></div>
            </section>
          </>}
        </div>
      </div>
    </main>
  </div>
}
