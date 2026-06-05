import React, { useState, useRef } from 'react';

/* ─── Step indicators ─── */
const STEPS = ['Tải lên CV', 'Xem & Chỉnh sửa', 'Xem trước & Xuất'];

/* ─── Helpers ─── */
function StepBar({ current }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 28 }}>
      {STEPS.map((label, i) => (
        <React.Fragment key={i}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: i <= current ? 'var(--color-primary, #6c63ff)' : '#e0e0e0',
              color: i <= current ? '#fff' : '#999',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 700, fontSize: 13, transition: 'background 0.3s'
            }}>{i < current ? '✓' : i + 1}</div>
            <span style={{ fontSize: 11, color: i === current ? 'var(--color-primary, #6c63ff)' : '#888', fontWeight: i === current ? 600 : 400, whiteSpace: 'nowrap' }}>{label}</span>
          </div>
          {i < STEPS.length - 1 && (
            <div style={{ flex: 1, height: 2, background: i < current ? 'var(--color-primary, #6c63ff)' : '#e0e0e0', margin: '0 8px', marginBottom: 16, transition: 'background 0.3s' }} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

/* ─── Editable field ─── */
function Field({ label, value, onChange, multiline }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: '#888', marginBottom: 3, textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</label>
      {multiline ? (
        <textarea
          value={value || ''}
          onChange={e => onChange(e.target.value)}
          rows={3}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #dde', fontSize: 13, resize: 'vertical', fontFamily: 'inherit' }}
        />
      ) : (
        <input
          type="text"
          value={value || ''}
          onChange={e => onChange(e.target.value)}
          style={{ width: '100%', padding: '7px 10px', borderRadius: 6, border: '1px solid #dde', fontSize: 13 }}
        />
      )}
    </div>
  );
}

function SectionTitle({ children }) {
  return (
    <div style={{ fontSize: 13, fontWeight: 700, color: '#3d3d6b', borderBottom: '2px solid #ededff', paddingBottom: 6, marginBottom: 12, marginTop: 20 }}>
      {children}
    </div>
  );
}

/* ─── Main Component ─── */
export default function CVProcessor() {
  const [step, setStep] = useState(0);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [previewHtml, setPreviewHtml] = useState(null);
  const fileInputRef = useRef();
  const iframeRef = useRef();
  const dropRef = useRef();

  /* ── STEP 0: Upload ── */
  const handleFileDrop = (e) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.type === 'application/pdf') setFile(dropped);
    else setError('Chỉ chấp nhận file PDF.');
  };

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch('/api/cv/extract', { method: 'POST', body: form });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || 'Lỗi trích xuất');
      setCvData(json.data);
      setStep(1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* ── STEP 2: Render preview ── */
  const handleRender = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/cv/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cv_data: cvData }),
      });
      if (!res.ok) {
        const json = await res.json();
        throw new Error(json.detail || 'Lỗi render');
      }
      const html = await res.text();
      setPreviewHtml(html);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* ── Deep setter helpers ── */
  const setField = (path, value) => {
    setCvData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split('.');
      let cur = next;
      for (let i = 0; i < keys.length - 1; i++) cur = cur[keys[i]];
      cur[keys[keys.length - 1]] = value;
      return next;
    });
  };

  const setArrayItem = (arrayPath, index, field, value) => {
    setCvData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const arr = arrayPath.split('.').reduce((o, k) => o[k], next);
      arr[index][field] = value;
      return next;
    });
  };

  const setArrayItemBullet = (arrayPath, index, bulletIndex, value) => {
    setCvData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const arr = arrayPath.split('.').reduce((o, k) => o[k], next);
      arr[index].description[bulletIndex] = value;
      return next;
    });
  };

  const addArrayItem = (arrayPath, template) => {
    setCvData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = arrayPath.split('.');
      let cur = next;
      for (let i = 0; i < keys.length - 1; i++) cur = cur[keys[i]];
      if (!cur[keys[keys.length - 1]]) cur[keys[keys.length - 1]] = [];
      cur[keys[keys.length - 1]].push({ ...template });
      return next;
    });
  };

  const removeArrayItem = (arrayPath, index) => {
    setCvData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const arr = arrayPath.split('.').reduce((o, k) => o[k], next);
      arr.splice(index, 1);
      return next;
    });
  };

  /* ────────────────────────────────
     RENDER
  ──────────────────────────────── */
  return (
    <div style={{ padding: '28px 32px', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#1a1a2e', marginBottom: 4 }}>
          <i className="fa-solid fa-file-circle-check" style={{ marginRight: 10, color: '#6c63ff' }}></i>
          CV Processor
        </h1>
        <p style={{ color: '#888', fontSize: 13 }}>Tải lên CV dạng PDF, AI sẽ trích xuất thông tin và điền vào mẫu CV chuyên nghiệp.</p>
      </div>

      <StepBar current={step} />

      {error && (
        <div style={{ background: '#fff0f0', border: '1px solid #ffb3b3', borderRadius: 8, padding: '10px 14px', marginBottom: 16, color: '#c0392b', fontSize: 13 }}>
          <b>Lỗi:</b> {error}
        </div>
      )}

      {/* ══ STEP 0: Upload ══ */}
      {step === 0 && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 28, boxShadow: '0 2px 12px rgba(0,0,0,0.07)' }}>
          <div
            ref={dropRef}
            onDragOver={e => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current.click()}
            style={{
              border: '2px dashed ' + (file ? '#6c63ff' : '#ccc'),
              borderRadius: 10,
              padding: '40px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              background: file ? '#f5f3ff' : '#fafafa',
              transition: 'all 0.2s',
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={e => { setFile(e.target.files[0]); setError(null); }}
            />
            <div style={{ fontSize: 40, marginBottom: 12 }}>{file ? '📄' : '📂'}</div>
            {file ? (
              <>
                <div style={{ fontWeight: 700, fontSize: 15, color: '#6c63ff' }}>{file.name}</div>
                <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>{(file.size / 1024).toFixed(1)} KB — Nhấn để đổi file</div>
              </>
            ) : (
              <>
                <div style={{ fontWeight: 600, fontSize: 14, color: '#555' }}>Kéo thả file PDF vào đây</div>
                <div style={{ color: '#aaa', fontSize: 12, marginTop: 4 }}>hoặc nhấn để chọn file (tối đa 10MB)</div>
              </>
            )}
          </div>

          <button
            onClick={handleExtract}
            disabled={!file || loading}
            style={{
              marginTop: 20, width: '100%', padding: '12px',
              background: file && !loading ? '#6c63ff' : '#ccc',
              color: '#fff', border: 'none', borderRadius: 8,
              fontSize: 14, fontWeight: 600, cursor: file && !loading ? 'pointer' : 'not-allowed',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8
            }}
          >
            {loading ? (
              <><span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⏳</span> Đang phân tích CV...</>
            ) : (
              <><i className="fa-solid fa-wand-magic-sparkles"></i> Phân tích CV bằng AI</>
            )}
          </button>
        </div>
      )}

      {/* ══ STEP 1: Edit data ══ */}
      {step === 1 && cvData && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 28, boxShadow: '0 2px 12px rgba(0,0,0,0.07)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1a1a2e' }}>Kiểm tra & Chỉnh sửa thông tin</h2>
            <button onClick={() => setStep(0)} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: 12 }}>← Tải lại</button>
          </div>
          <p style={{ color: '#aaa', fontSize: 12, marginBottom: 20 }}>AI đã trích xuất thông tin bên dưới. Bạn có thể chỉnh sửa trước khi tạo CV.</p>

          {/* Personal Info */}
          <SectionTitle>Thông tin cá nhân</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
            <Field label="Họ tên" value={cvData.personal_info?.full_name} onChange={v => setField('personal_info.full_name', v)} />
            <Field label="Email" value={cvData.personal_info?.email} onChange={v => setField('personal_info.email', v)} />
            <Field label="Điện thoại" value={cvData.personal_info?.phone} onChange={v => setField('personal_info.phone', v)} />
            <Field label="Địa chỉ" value={cvData.personal_info?.address} onChange={v => setField('personal_info.address', v)} />
            <Field label="LinkedIn" value={cvData.personal_info?.linkedin} onChange={v => setField('personal_info.linkedin', v)} />
            <Field label="Website" value={cvData.personal_info?.website} onChange={v => setField('personal_info.website', v)} />
            <Field label="Ngày sinh" value={cvData.personal_info?.date_of_birth} onChange={v => setField('personal_info.date_of_birth', v)} />
            <Field label="Giới tính" value={cvData.personal_info?.gender} onChange={v => setField('personal_info.gender', v)} />
          </div>

          {/* Summary */}
          <SectionTitle>Giới thiệu bản thân</SectionTitle>
          <Field label="Tóm tắt" value={cvData.summary} onChange={v => setField('summary', v)} multiline />

          {/* Experience */}
          <SectionTitle>Kinh nghiệm làm việc</SectionTitle>
          {(cvData.experience || []).map((exp, i) => (
            <div key={i} style={{ background: '#f9f9ff', borderRadius: 8, padding: '14px 16px', marginBottom: 12, position: 'relative' }}>
              <button onClick={() => removeArrayItem('experience', i)} style={{ position: 'absolute', top: 10, right: 10, background: '#ffe0e0', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', color: '#c0392b', fontSize: 11 }}>Xóa</button>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
                <Field label="Công ty" value={exp.company} onChange={v => setArrayItem('experience', i, 'company', v)} />
                <Field label="Vị trí" value={exp.position} onChange={v => setArrayItem('experience', i, 'position', v)} />
                <Field label="Bắt đầu" value={exp.start_date} onChange={v => setArrayItem('experience', i, 'start_date', v)} />
                <Field label="Kết thúc" value={exp.end_date} onChange={v => setArrayItem('experience', i, 'end_date', v)} />
              </div>
              <label style={{ fontSize: 11, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>Mô tả công việc</label>
              {(exp.description || []).map((bullet, bi) => (
                <div key={bi} style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                  <span style={{ color: '#6c63ff', marginTop: 8, fontSize: 10 }}>▸</span>
                  <input
                    value={bullet}
                    onChange={e => setArrayItemBullet('experience', i, bi, e.target.value)}
                    style={{ flex: 1, padding: '6px 9px', borderRadius: 5, border: '1px solid #dde', fontSize: 12 }}
                  />
                  <button onClick={() => {
                    setCvData(prev => {
                      const next = JSON.parse(JSON.stringify(prev));
                      next.experience[i].description.splice(bi, 1);
                      return next;
                    });
                  }} style={{ background: 'none', border: 'none', color: '#ccc', cursor: 'pointer', fontSize: 14 }}>✕</button>
                </div>
              ))}
              <button onClick={() => {
                setCvData(prev => {
                  const next = JSON.parse(JSON.stringify(prev));
                  if (!next.experience[i].description) next.experience[i].description = [];
                  next.experience[i].description.push('');
                  return next;
                });
              }} style={{ marginTop: 8, fontSize: 11, color: '#6c63ff', background: 'none', border: '1px dashed #c5c0ff', borderRadius: 4, padding: '3px 10px', cursor: 'pointer' }}>+ Thêm bullet</button>
            </div>
          ))}
          <button onClick={() => addArrayItem('experience', { company: '', position: '', start_date: '', end_date: '', description: [] })}
            style={{ fontSize: 12, color: '#6c63ff', background: 'none', border: '1px dashed #c5c0ff', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', marginBottom: 4 }}>
            + Thêm kinh nghiệm
          </button>

          {/* Education */}
          <SectionTitle>Học vấn</SectionTitle>
          {(cvData.education || []).map((edu, i) => (
            <div key={i} style={{ background: '#f9f9ff', borderRadius: 8, padding: '14px 16px', marginBottom: 12, position: 'relative' }}>
              <button onClick={() => removeArrayItem('education', i)} style={{ position: 'absolute', top: 10, right: 10, background: '#ffe0e0', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', color: '#c0392b', fontSize: 11 }}>Xóa</button>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
                <Field label="Trường" value={edu.institution} onChange={v => setArrayItem('education', i, 'institution', v)} />
                <Field label="Bằng cấp" value={edu.degree} onChange={v => setArrayItem('education', i, 'degree', v)} />
                <Field label="Chuyên ngành" value={edu.field} onChange={v => setArrayItem('education', i, 'field', v)} />
                <Field label="GPA" value={edu.gpa} onChange={v => setArrayItem('education', i, 'gpa', v)} />
                <Field label="Bắt đầu" value={edu.start_date} onChange={v => setArrayItem('education', i, 'start_date', v)} />
                <Field label="Kết thúc" value={edu.end_date} onChange={v => setArrayItem('education', i, 'end_date', v)} />
              </div>
            </div>
          ))}
          <button onClick={() => addArrayItem('education', { institution: '', degree: '', field: '', start_date: '', end_date: '', gpa: '' })}
            style={{ fontSize: 12, color: '#6c63ff', background: 'none', border: '1px dashed #c5c0ff', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', marginBottom: 4 }}>
            + Thêm học vấn
          </button>

          {/* Skills */}
          <SectionTitle>Kỹ năng</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: 11, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>Kỹ năng kỹ thuật</label>
              <textarea
                value={(cvData.skills?.technical || []).join('\n')}
                onChange={e => setField('skills.technical', e.target.value.split('\n').map(s => s.trim()).filter(Boolean))}
                rows={5}
                placeholder="Mỗi kỹ năng 1 dòng"
                style={{ width: '100%', marginTop: 4, padding: '7px 10px', borderRadius: 6, border: '1px solid #dde', fontSize: 13, resize: 'vertical', fontFamily: 'inherit' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 11, fontWeight: 600, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>Kỹ năng mềm</label>
              <textarea
                value={(cvData.skills?.soft || []).join('\n')}
                onChange={e => setField('skills.soft', e.target.value.split('\n').map(s => s.trim()).filter(Boolean))}
                rows={5}
                placeholder="Mỗi kỹ năng 1 dòng"
                style={{ width: '100%', marginTop: 4, padding: '7px 10px', borderRadius: 6, border: '1px solid #dde', fontSize: 13, resize: 'vertical', fontFamily: 'inherit' }}
              />
            </div>
          </div>

          {/* Languages */}
          <SectionTitle>Ngôn ngữ</SectionTitle>
          {(cvData.languages || []).map((lang, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
              <input value={lang.language} onChange={e => setArrayItem('languages', i, 'language', e.target.value)}
                placeholder="Ngôn ngữ" style={{ flex: 1, padding: '6px 9px', borderRadius: 5, border: '1px solid #dde', fontSize: 13 }} />
              <input value={lang.level} onChange={e => setArrayItem('languages', i, 'level', e.target.value)}
                placeholder="Trình độ (B2, Native...)" style={{ flex: 1, padding: '6px 9px', borderRadius: 5, border: '1px solid #dde', fontSize: 13 }} />
              <button onClick={() => removeArrayItem('languages', i)} style={{ background: 'none', border: 'none', color: '#ccc', cursor: 'pointer', fontSize: 16 }}>✕</button>
            </div>
          ))}
          <button onClick={() => addArrayItem('languages', { language: '', level: '' })}
            style={{ fontSize: 12, color: '#6c63ff', background: 'none', border: '1px dashed #c5c0ff', borderRadius: 6, padding: '6px 14px', cursor: 'pointer' }}>
            + Thêm ngôn ngữ
          </button>

          {/* Projects */}
          <SectionTitle>Dự án nổi bật</SectionTitle>
          {(cvData.projects || []).map((proj, i) => (
            <div key={i} style={{ background: '#f9f9ff', borderRadius: 8, padding: '14px 16px', marginBottom: 12, position: 'relative' }}>
              <button onClick={() => removeArrayItem('projects', i)} style={{ position: 'absolute', top: 10, right: 10, background: '#ffe0e0', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', color: '#c0392b', fontSize: 11 }}>Xóa</button>
              <Field label="Tên dự án" value={proj.name} onChange={v => setArrayItem('projects', i, 'name', v)} />
              <Field label="Công nghệ sử dụng" value={proj.technologies} onChange={v => setArrayItem('projects', i, 'technologies', v)} />
              <Field label="Mô tả" value={proj.description} onChange={v => setArrayItem('projects', i, 'description', v)} multiline />
            </div>
          ))}
          <button onClick={() => addArrayItem('projects', { name: '', description: '', technologies: '' })}
            style={{ fontSize: 12, color: '#6c63ff', background: 'none', border: '1px dashed #c5c0ff', borderRadius: 6, padding: '6px 14px', cursor: 'pointer' }}>
            + Thêm dự án
          </button>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 12, marginTop: 28 }}>
            <button onClick={handleRender} disabled={loading}
              style={{ flex: 1, padding: '12px', background: loading ? '#ccc' : '#6c63ff', color: '#fff', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              {loading ? '⏳ Đang tạo...' : <><i className="fa-solid fa-eye"></i> Xem trước CV</>}
            </button>
          </div>
        </div>
      )}

      {/* ══ STEP 2: Preview ══ */}
      {step === 2 && previewHtml && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,0.07)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1a1a2e' }}>Xem trước CV</h2>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => setStep(1)}
                style={{ padding: '8px 16px', background: '#f0f0f8', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, color: '#555' }}>
                ← Chỉnh sửa lại
              </button>
              <button
                onClick={() => {
                  const win = window.open('', '_blank');
                  win.document.write(previewHtml);
                  win.document.close();
                  setTimeout(() => win.print(), 500);
                }}
                style={{ padding: '8px 20px', background: '#6c63ff', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <i className="fa-solid fa-file-pdf"></i> In / Xuất PDF
              </button>
            </div>
          </div>

          <iframe
            ref={iframeRef}
            srcDoc={previewHtml}
            style={{ width: '100%', height: '80vh', border: '1px solid #eee', borderRadius: 8, background: '#f5f5f5' }}
            title="CV Preview"
          />
        </div>
      )}
    </div>
  );
}
