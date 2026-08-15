/**
 * Sistem RAB Konstruksi — Logika Frontend
 */

// ── SVG inline untuk dipakai di konten dinamis ──────────────────
const IC = {
  x:        `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
  check:    `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  warn:     `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  info:     `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  trash:    `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>`,
  eye:      `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
  download: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  trending: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  pin:      `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  cal:      `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
};

// ── Utilitas ─────────────────────────────────────────────────────

function formatRupiah(n) {
  if (n === null || n === undefined || isNaN(n)) return '–';
  return 'Rp ' + Number(n).toLocaleString('id-ID', { maximumFractionDigits: 0 });
}

function formatAngka(n, des = 2) {
  if (n === null || n === undefined || isNaN(n)) return '–';
  return Number(n).toLocaleString('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: des });
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function tampilkanLoading(pesan = 'Memproses...') {
  document.getElementById('loading').classList.add('show');
  document.getElementById('loading-teks').textContent = pesan;
}

function sembunyikanLoading() {
  document.getElementById('loading').classList.remove('show');
}

// ── Toast ────────────────────────────────────────────────────────

const TOAST_META = {
  success: { title: 'Berhasil',    icon: IC.check },
  error:   { title: 'Gagal',       icon: IC.warn  },
  warning: { title: 'Perhatian',   icon: IC.warn  },
  info:    { title: 'Informasi',   icon: IC.info  },
};

function tampilkanToast(pesan, tipe = 'info', durasi = 4500) {
  const wrap = document.getElementById('toast-wrap');
  const meta = TOAST_META[tipe] || TOAST_META.info;

  const el = document.createElement('div');
  el.className = `toast toast-${tipe}`;
  el.innerHTML = `
    <div class="toast-icon">${meta.icon}</div>
    <div class="toast-body">
      <div class="toast-title">${meta.title}</div>
      <div class="toast-msg">${esc(pesan)}</div>
    </div>
    <button class="toast-close" onclick="this.closest('.toast').remove()">${IC.x}</button>
  `;
  wrap.appendChild(el);

  setTimeout(() => {
    el.style.animation = 'slide-out 0.2s ease forwards';
    setTimeout(() => el.remove(), 220);
  }, durasi);
}

// ── API Fetch helper ──────────────────────────────────────────────

async function apiFetch(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  }).catch(() => { throw new Error('Tidak dapat terhubung ke server. Pastikan aplikasi berjalan.'); });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.detail || `Error ${res.status}`;
    throw new Error(Array.isArray(msg) ? msg.map(e => e.msg).join(', ') : msg);
  }
  return data;
}

// ── Navigasi ──────────────────────────────────────────────────────

function gantiTab(nama) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('aktif'));
  document.querySelectorAll('.nav-item[data-tab]').forEach(b => b.classList.remove('aktif'));

  const panel = document.getElementById(`tab-${nama}`);
  if (panel) panel.classList.add('aktif');

  const btn = document.querySelector(`.nav-item[data-tab="${nama}"]`);
  if (btn) btn.classList.add('aktif');

  if (nama === 'dashboard') muatDashboard();
  if (nama === 'bankdata')  { muatOpsiFilter(); cariHSP(); }
  if (nama === 'proyek')    muatSemuaProyek();
  if (nama === 'generate')  inisialisasiGenerate();
}

// ── Dashboard ─────────────────────────────────────────────────────

async function muatDashboard() {
  try {
    const s = await apiFetch('/api/proyek/statistik');
    document.getElementById('stat-proyek').textContent = s.total_proyek;
    document.getElementById('stat-hsp').textContent    = s.total_hsp;
    document.getElementById('stat-item').textContent   = s.total_item_boq;
    document.getElementById('stat-nilai').textContent  = formatRupiah(s.total_nilai_rab);

    const lokasiEl = document.getElementById('list-lokasi');
    lokasiEl.innerHTML = s.daftar_lokasi.length
      ? s.daftar_lokasi.map(l => `<span class="badge badge-blue">${esc(l)}</span>`).join('')
      : '<span class="text-muted text-sm">Belum ada data</span>';

    await muatProyekTerbaru();
  } catch (e) {
    tampilkanToast('Gagal memuat dashboard: ' + e.message, 'error');
  }
}

async function muatProyekTerbaru() {
  const el = document.getElementById('list-proyek-terbaru');
  try {
    const data = await apiFetch('/api/proyek');
    if (!data.length) {
      el.innerHTML = `<div class="empty-state">
        <svg class="empty-state-icon"><use href="#ic-folder"/></svg>
        <div class="empty-state-title">Belum ada proyek</div>
        <div class="empty-state-desc">Upload file Excel RAB untuk memulai.</div>
      </div>`;
      return;
    }
    el.innerHTML = data.slice(0, 6).map(p => `
      <div class="recent-item" onclick="tampilkanDetailProyek(${p.id})">
        <div>
          <div class="recent-item-name">${esc(p.nama_proyek)}</div>
          <div class="recent-item-meta">
            ${IC.pin} ${esc(p.lokasi)} &nbsp;${IC.cal} ${p.tahun}
            ${p.is_generated ? ' &nbsp;<span class="badge badge-green">Generated</span>' : ''}
          </div>
        </div>
        <div class="recent-item-total">${formatRupiah(p.total_dengan_ppn)}</div>
      </div>
    `).join('');
  } catch (e) {
    el.innerHTML = '<p class="text-sm" style="color:var(--red);padding:12px">Gagal memuat proyek.</p>';
  }
}

// ── Upload RAB ────────────────────────────────────────────────────

let fileUpload   = null;
let dataPreview  = null;

function handleFileSelect(e) { setFileUpload(e.target.files[0]); }

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('zona-upload').classList.remove('drag-over');
  setFileUpload(e.dataTransfer.files[0]);
}

function setFileUpload(file) {
  if (!file) return;
  const ok = ['.xlsx', '.xls'].some(ext => file.name.toLowerCase().endsWith(ext));
  if (!ok) { tampilkanToast('Format tidak didukung. Gunakan .xlsx atau .xls', 'error'); return; }

  fileUpload = file;
  const info = document.getElementById('info-file-dipilih');
  info.style.display = 'flex';
  document.getElementById('teks-file-dipilih').textContent =
    `File dipilih: ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
  document.getElementById('btn-preview').disabled = false;
}

async function uploadPreview() {
  if (!fileUpload) { tampilkanToast('Pilih file terlebih dahulu.', 'warning'); return; }
  tampilkanLoading('Membaca dan menganalisis file Excel...');
  try {
    const fd = new FormData();
    fd.append('file', fileUpload);
    const res  = await fetch('/api/upload/preview', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Gagal membaca file');
    dataPreview = data;
    tampilkanPreview(data);
    tampilkanToast(data.pesan, 'success');
  } catch (e) {
    tampilkanToast('Gagal membaca file: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

function tampilkanPreview(data) {
  document.getElementById('section-preview').style.display = 'block';

  const m = data.metadata_terdeteksi || {};
  if (m.nama_proyek) document.getElementById('preview-nama').value   = m.nama_proyek;
  if (m.lokasi)      document.getElementById('preview-lokasi').value  = m.lokasi;
  if (m.tahun)       document.getElementById('preview-tahun').value   = m.tahun;

  document.getElementById('stat-preview').innerHTML = `
    <span class="badge badge-blue">${data.total_item_valid} item</span>
    <span class="badge badge-green">${data.total_divisi} kelompok</span>
    <span class="badge badge-slate">${data.total_baris} baris total</span>
  `;

  const tbody = document.getElementById('tbody-preview');
  let no = 0;
  tbody.innerHTML = data.items.map(item => {
    if (item.is_divisi) {
      return `<tr class="tr-group"><td colspan="7">${esc(item.uraian_pekerjaan)}</td></tr>`;
    }
    no++;
    const statusHtml = item.peringatan
      ? `<span class="badge badge-amber" title="${esc(item.peringatan)}">Peringatan</span>`
      : `<span class="badge badge-green">OK</span>`;
    return `<tr>
      <td class="c muted">${esc(item.nomor_urut) || no}</td>
      <td>${esc(item.uraian_pekerjaan)}</td>
      <td class="c">${esc(item.satuan) || '–'}</td>
      <td class="r">${formatAngka(item.volume)}</td>
      <td class="r">${formatRupiah(item.harga_satuan)}</td>
      <td class="r font-bold">${formatRupiah(item.jumlah)}</td>
      <td class="c">${statusHtml}</td>
    </tr>`;
  }).join('');

  document.getElementById('section-preview').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function konfirmasiSimpan() {
  const nama   = document.getElementById('preview-nama').value.trim();
  const lokasi = document.getElementById('preview-lokasi').value.trim();
  const tahun  = parseInt(document.getElementById('preview-tahun').value);
  const ppn    = parseFloat(document.getElementById('preview-ppn').value) || 11;
  const desk   = document.getElementById('preview-deskripsi').value.trim();

  if (!nama)   { tampilkanToast('Nama proyek wajib diisi.', 'error');   return; }
  if (!lokasi) { tampilkanToast('Lokasi wajib diisi.', 'error');        return; }
  if (!tahun || tahun < 2000 || tahun > 2100) {
    tampilkanToast('Tahun tidak valid (2000–2100).', 'error'); return;
  }

  tampilkanLoading('Menyimpan data ke database...');
  try {
    const hasil = await apiFetch('/api/upload/konfirmasi', {
      method: 'POST',
      body: JSON.stringify({
        nama_proyek: nama, lokasi, tahun,
        deskripsi: desk || null, ppn_persen: ppn,
        items: dataPreview.items, nama_file: dataPreview.nama_file,
      }),
    });
    tampilkanToast(hasil.pesan, 'success', 6000);
    resetUpload();
    muatDashboard();
  } catch (e) {
    tampilkanToast('Gagal menyimpan: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

function resetUpload() {
  fileUpload = null; dataPreview = null;
  document.getElementById('input-file').value = '';
  document.getElementById('info-file-dipilih').style.display = 'none';
  document.getElementById('btn-preview').disabled = true;
  document.getElementById('section-preview').style.display = 'none';
  ['preview-nama','preview-lokasi','preview-tahun','preview-deskripsi']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('preview-ppn').value = '11';
}

// ── Bank Data ─────────────────────────────────────────────────────

async function muatOpsiFilter() {
  try {
    const d = await apiFetch('/api/cari/filter-opsi');
    const sl = document.getElementById('cari-lokasi');
    sl.innerHTML = '<option value="">Semua Lokasi</option>' +
      d.lokasi.map(l => `<option value="${esc(l)}">${esc(l)}</option>`).join('');

    const st = document.getElementById('filter-tahun-proyek');
    if (st) st.innerHTML = '<option value="">Semua Tahun</option>' +
      d.tahun.map(t => `<option value="${t}">${t}</option>`).join('');
  } catch (e) { /* silent */ }
}

async function cariHSP() {
  const kw     = document.getElementById('cari-kata-kunci').value.trim();
  const lokasi = document.getElementById('cari-lokasi').value;
  const tDari  = document.getElementById('cari-tahun-dari').value;
  const tSmp   = document.getElementById('cari-tahun-sampai').value;
  const params = new URLSearchParams({ limit: 200 });
  if (kw)     params.set('kata_kunci', kw);
  if (lokasi) params.set('lokasi', lokasi);
  if (tDari)  params.set('tahun_dari', tDari);
  if (tSmp)   params.set('tahun_sampai', tSmp);
  try {
    const data = await apiFetch('/api/cari/hsp?' + params);
    renderTabelHSP(data);
  } catch (e) {
    tampilkanToast('Gagal mencari: ' + e.message, 'error');
  }
}

function renderTabelHSP(data) {
  const tbody  = document.getElementById('tbody-hsp');
  const kosong = document.getElementById('kosong-hsp');
  const info   = document.getElementById('info-hasil-cari');

  info.innerHTML = `<span class="badge badge-blue">${data.total} data ditemukan</span>`;

  if (!data.items.length) {
    tbody.innerHTML = '';
    kosong.style.display = 'block';
    return;
  }
  kosong.style.display = 'none';
  tbody.innerHTML = data.items.map(h => `
    <tr>
      <td>${esc(h.uraian_pekerjaan)}</td>
      <td class="c">${esc(h.satuan) || '–'}</td>
      <td><span class="badge badge-slate">${esc(h.divisi) || '–'}</span></td>
      <td class="r font-bold num">${formatRupiah(h.harga_satuan)}</td>
      <td>${esc(h.lokasi)}</td>
      <td class="c"><span class="badge badge-amber">${h.tahun}</span></td>
      <td class="muted">${esc(h.nama_proyek)}</td>
      <td class="c">
        <div class="flex gap-6 justify-end">
          <button class="btn btn-ghost btn-sm" title="Riwayat harga"
            onclick="lihatRiwayatHarga('${encodeURIComponent(h.uraian_pekerjaan)}')">${IC.trending}</button>
          <button class="btn btn-primary btn-sm" title="Gunakan di Generate RAB"
            onclick="pakaiHargaIni('${esc(h.uraian_pekerjaan)}','${esc(h.satuan)||''}',${h.harga_satuan})">Pakai</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function resetCari() {
  ['cari-kata-kunci','cari-tahun-dari','cari-tahun-sampai'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('cari-lokasi').value = '';
  cariHSP();
}

async function lihatRiwayatHarga(uraianEncoded) {
  const uraian = decodeURIComponent(uraianEncoded);
  try {
    const data = await apiFetch(`/api/cari/riwayat-harga?uraian=${encodeURIComponent(uraian)}`);
    const card = document.getElementById('card-riwayat');
    card.style.display = 'block';
    document.getElementById('judul-riwayat').textContent = uraian;

    const tbody = document.getElementById('tbody-riwayat');
    tbody.innerHTML = data.riwayat.length
      ? data.riwayat.map(r => `
        <tr>
          <td class="c"><span class="badge badge-amber">${r.tahun}</span></td>
          <td>${esc(r.lokasi)}</td>
          <td class="r font-bold num">${formatRupiah(r.harga_satuan)}</td>
          <td class="muted">${esc(r.uraian_pekerjaan)}</td>
          <td class="muted">${esc(r.nama_proyek)}</td>
        </tr>`).join('')
      : `<tr><td colspan="5" class="c muted" style="padding:20px">Tidak ada riwayat data.</td></tr>`;

    card.scrollIntoView({ behavior: 'smooth' });
  } catch (e) {
    tampilkanToast('Gagal memuat riwayat: ' + e.message, 'error');
  }
}

function pakaiHargaIni(uraian, satuan, harga) {
  gantiTab('generate');
  setTimeout(() => tambahItemGenerate(uraian, satuan, harga), 150);
}

// ── Generate RAB ──────────────────────────────────────────────────

let hasilGenerate = null;

function inisialisasiGenerate() {
  if (!document.querySelectorAll('.item-row').length) tambahItemGenerate();
}

function tambahItemGenerate(uraian = '', satuan = '', harga = '') {
  const id = Date.now();
  const wrap = document.getElementById('kontainer-item-generate');
  const div  = document.createElement('div');
  div.className = 'item-row';
  div.id = `item-gen-${id}`;
  div.innerHTML = `
    <button class="item-remove" onclick="hapusItemGenerate(${id})" title="Hapus item">${IC.x}</button>
    <div class="item-row-grid">
      <div class="form-group" style="margin-bottom:0">
        <label class="form-label">Uraian Pekerjaan <span class="req">*</span></label>
        <input type="text" class="form-control" id="gen-uraian-${id}"
               value="${esc(uraian)}" placeholder="Nama item pekerjaan"
               onblur="cariHargaItemOtomatis(${id})">
      </div>
      <div class="form-group" style="margin-bottom:0">
        <label class="form-label">Satuan</label>
        <input type="text" class="form-control" id="gen-satuan-${id}"
               value="${esc(satuan)}" placeholder="m2, m3, unit...">
      </div>
      <div class="form-group" style="margin-bottom:0">
        <label class="form-label">Volume <span class="req">*</span></label>
        <input type="number" class="form-control" id="gen-volume-${id}"
               placeholder="0" min="0" step="any" onchange="hitungJumlahItem(${id})">
      </div>
      <div class="form-group" style="margin-bottom:0">
        <label class="form-label">Harga Satuan (Rp) <span class="req">*</span></label>
        <input type="number" class="form-control" id="gen-harga-${id}"
               value="${harga || ''}" placeholder="0" min="0" step="any"
               onchange="hitungJumlahItem(${id})">
      </div>
    </div>
    <div class="item-row-footer">
      <div class="form-group" style="margin-bottom:0;flex:1">
        <label class="form-label">Kelompok / Divisi (opsional)</label>
        <input type="text" class="form-control" id="gen-divisi-${id}"
               placeholder="Contoh: I. Pekerjaan Persiapan">
      </div>
      <div style="padding-top:18px;text-align:right">
        <div class="item-total-label">Jumlah</div>
        <div class="item-total-value" id="gen-jumlah-${id}">–</div>
      </div>
    </div>
    <div class="price-hint" id="info-harga-${id}"></div>
  `;
  wrap.appendChild(div);
}

function hapusItemGenerate(id) {
  document.getElementById(`item-gen-${id}`)?.remove();
}

function hitungJumlahItem(id) {
  const vol   = parseFloat(document.getElementById(`gen-volume-${id}`)?.value) || 0;
  const harga = parseFloat(document.getElementById(`gen-harga-${id}`)?.value)  || 0;
  const el    = document.getElementById(`gen-jumlah-${id}`);
  if (el) el.textContent = vol > 0 && harga > 0 ? formatRupiah(vol * harga) : '–';
}

async function cariHargaItemOtomatis(id) {
  const uraian   = document.getElementById(`gen-uraian-${id}`)?.value?.trim();
  const satuan   = document.getElementById(`gen-satuan-${id}`)?.value?.trim();
  const lokasi   = document.getElementById('gen-lokasi')?.value?.trim();
  const tahun    = parseInt(document.getElementById('gen-tahun')?.value)   || 2024;
  const eskalasi = parseFloat(document.getElementById('gen-eskalasi')?.value) || 0;
  const infoEl   = document.getElementById(`info-harga-${id}`);
  if (!uraian || !lokasi) return;

  try {
    const h = await apiFetch('/api/generate/cari-harga-otomatis', {
      method: 'POST',
      body: JSON.stringify({ uraian_pekerjaan: uraian, satuan, lokasi, tahun, eskalasi_persen: eskalasi }),
    });
    if (h.ditemukan) {
      const hargaEl = document.getElementById(`gen-harga-${id}`);
      if (hargaEl && (!hargaEl.value || hargaEl.value === '0')) {
        hargaEl.value = Math.round(h.harga_setelah_eskalasi);
        hitungJumlahItem(id);
      }
      infoEl.classList.add('show');
      infoEl.innerHTML =
        `Harga dari bank data &mdash; ${esc(h.nama_proyek_sumber)} (${esc(h.lokasi_sumber)}, ${h.tahun_sumber}). ` +
        `Harga asli: ${formatRupiah(h.harga_asli)}` +
        (h.selisih_tahun > 0
          ? ` &rarr; setelah eskalasi ${eskalasi}%/thn: <strong>${formatRupiah(h.harga_setelah_eskalasi)}</strong>`
          : '');
    } else {
      infoEl.classList.remove('show');
    }
  } catch (_) {
    infoEl.classList.remove('show');
  }
}

async function cariSemuaHargaOtomatis() {
  const items = document.querySelectorAll('.item-row');
  if (!items.length) { tampilkanToast('Tambahkan item pekerjaan terlebih dahulu.', 'warning'); return; }
  tampilkanLoading('Mencari harga dari bank data...');
  try {
    for (const item of items) {
      const id = item.id.replace('item-gen-', '');
      await cariHargaItemOtomatis(id);
    }
    tampilkanToast('Pencarian harga otomatis selesai.', 'success');
  } finally {
    sembunyikanLoading();
  }
}

function kumpulkanItemGenerate() {
  return Array.from(document.querySelectorAll('.item-row')).map(el => {
    const id = el.id.replace('item-gen-', '');
    return {
      uraian_pekerjaan: document.getElementById(`gen-uraian-${id}`)?.value?.trim() || '',
      satuan:  document.getElementById(`gen-satuan-${id}`)?.value?.trim() || 'ls',
      volume:  parseFloat(document.getElementById(`gen-volume-${id}`)?.value)  || 0,
      harga_satuan: parseFloat(document.getElementById(`gen-harga-${id}`)?.value) || 0,
      divisi:  document.getElementById(`gen-divisi-${id}`)?.value?.trim() || null,
    };
  }).filter(i => i.uraian_pekerjaan);
}

function hitungGenerate() {
  const nama   = document.getElementById('gen-nama').value.trim();
  const lokasi = document.getElementById('gen-lokasi').value.trim();
  const tahun  = parseInt(document.getElementById('gen-tahun').value);
  const ppn    = parseFloat(document.getElementById('gen-ppn').value) || 11;

  if (!nama)   { tampilkanToast('Nama proyek wajib diisi.', 'error');  return; }
  if (!lokasi) { tampilkanToast('Lokasi wajib diisi.', 'error');       return; }

  const items = kumpulkanItemGenerate();
  if (!items.length) { tampilkanToast('Tambahkan minimal 1 item pekerjaan.', 'warning'); return; }

  const subtotal   = items.reduce((s, i) => s + i.volume * i.harga_satuan, 0);
  const ppnNominal = subtotal * ppn / 100;
  const total      = subtotal + ppnNominal;

  document.getElementById('rekap-subtotal').textContent  = formatRupiah(subtotal);
  document.getElementById('rekap-ppn-persen').textContent = ppn;
  document.getElementById('rekap-ppn').textContent       = formatRupiah(ppnNominal);
  document.getElementById('rekap-total').textContent     = formatRupiah(total);
  document.getElementById('section-rekap-generate').style.display = 'block';
  document.getElementById('btn-simpan-generate').style.display    = 'inline-flex';
  document.getElementById('btn-export-saja').style.display        = 'inline-flex';

  hasilGenerate = {
    nama, lokasi, tahun, ppn, items, subtotal, ppnNominal, total,
    deskripsi: document.getElementById('gen-deskripsi').value.trim() || null,
  };

  tampilkanToast(`Total RAB: ${formatRupiah(total)}`, 'success');
  document.getElementById('section-rekap-generate').scrollIntoView({ behavior: 'smooth' });
}

async function simpanDanExportGenerate() {
  if (!hasilGenerate) { tampilkanToast('Klik "Hitung" terlebih dahulu.', 'warning'); return; }
  tampilkanLoading('Menyimpan RAB ke database...');
  try {
    const payload = {
      nama_proyek: hasilGenerate.nama, lokasi: hasilGenerate.lokasi,
      tahun: hasilGenerate.tahun, deskripsi: hasilGenerate.deskripsi,
      ppn_persen: hasilGenerate.ppn, items: hasilGenerate.items,
      simpan_ke_database: true,
    };
    const hasil = await apiFetch('/api/generate/rab', { method: 'POST', body: JSON.stringify(payload) });
    tampilkanToast(hasil.pesan, 'success');
    if (hasil.proyek_id) window.location.href = `/api/export/rab/${hasil.proyek_id}`;
    muatDashboard();
  } catch (e) {
    tampilkanToast('Gagal: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

async function exportSajaGenerate() {
  if (!hasilGenerate) { tampilkanToast('Klik "Hitung" terlebih dahulu.', 'warning'); return; }
  tampilkanLoading('Membuat file Excel...');
  try {
    const payload = {
      nama_proyek: hasilGenerate.nama, lokasi: hasilGenerate.lokasi,
      tahun: hasilGenerate.tahun, deskripsi: hasilGenerate.deskripsi,
      ppn_persen: hasilGenerate.ppn, items: hasilGenerate.items,
      subtotal: hasilGenerate.subtotal, ppn_nominal: hasilGenerate.ppnNominal,
      total: hasilGenerate.total,
    };
    const res  = await fetch('/api/export/rab-baru', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
    const blob = await res.blob();
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(blob),
      download: `RAB_${hasilGenerate.nama}_${hasilGenerate.tahun}.xlsx`,
    });
    a.click(); URL.revokeObjectURL(a.href);
    tampilkanToast('File Excel berhasil diunduh.', 'success');
  } catch (e) {
    tampilkanToast('Gagal export: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

// ── Semua Proyek ──────────────────────────────────────────────────

async function muatSemuaProyek() {
  await muatOpsiFilter();
  const nama  = document.getElementById('filter-nama-proyek')?.value?.trim();
  const tahun = document.getElementById('filter-tahun-proyek')?.value;
  const params = new URLSearchParams();
  if (nama)  params.set('kata_kunci', nama);
  if (tahun) params.set('tahun', tahun);

  const grid = document.getElementById('grid-proyek');
  grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
    <div style="font-size:13px;color:var(--t3)">Memuat...</div></div>`;

  try {
    const data = await apiFetch('/api/proyek?' + params);
    if (!data.length) {
      grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
        <svg class="empty-state-icon"><use href="#ic-folder"/></svg>
        <div class="empty-state-title">Tidak ada proyek ditemukan</div>
        <div class="empty-state-desc">Coba ubah filter atau upload file RAB terlebih dahulu.</div>
      </div>`;
      return;
    }
    grid.innerHTML = data.map(p => `
      <div class="project-card" onclick="tampilkanDetailProyek(${p.id})">
        <div class="project-card-name">${esc(p.nama_proyek)}</div>
        <div class="project-card-meta">${IC.pin} ${esc(p.lokasi)}</div>
        <div class="project-card-meta">
          ${IC.cal} ${p.tahun} &nbsp;&middot;&nbsp; ${p.jumlah_item || 0} item pekerjaan
          ${p.is_generated
            ? '&nbsp;<span class="badge badge-green">Generated</span>'
            : '&nbsp;<span class="badge badge-blue">Upload</span>'}
        </div>
        <div class="project-card-total">${formatRupiah(p.total_dengan_ppn)}</div>
        <div class="project-card-actions" onclick="event.stopPropagation()">
          <button class="btn btn-ghost btn-sm" onclick="tampilkanDetailProyek(${p.id})">
            ${IC.eye} Detail
          </button>
          <a class="btn btn-primary btn-sm" href="/api/export/rab/${p.id}">
            ${IC.download} Export
          </a>
          <button class="btn btn-ghost btn-sm" style="color:var(--red)"
            onclick="konfirmasiHapusProyek(${p.id},'${esc(p.nama_proyek)}')">
            ${IC.trash}
          </button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    grid.innerHTML = `<p style="color:var(--red);grid-column:1/-1;padding:20px">Gagal memuat: ${esc(e.message)}</p>`;
  }
}

async function tampilkanDetailProyek(id) {
  tampilkanLoading('Memuat detail proyek...');
  try {
    const data = await apiFetch(`/api/proyek/${id}/boq`);
    const p    = data.proyek;
    let no = 0;

    const rows = data.items.map(item => {
      if (item.is_divisi)
        return `<tr class="tr-group"><td colspan="6">${esc(item.uraian_pekerjaan)}</td></tr>`;
      no++;
      return `<tr>
        <td class="c muted">${esc(item.nomor_urut) || no}</td>
        <td>${esc(item.uraian_pekerjaan)}</td>
        <td class="c">${esc(item.satuan) || '–'}</td>
        <td class="r">${formatAngka(item.volume)}</td>
        <td class="r">${formatRupiah(item.harga_satuan)}</td>
        <td class="r font-bold num">${formatRupiah(item.jumlah)}</td>
      </tr>`;
    }).join('');

    document.getElementById('modal-judul').textContent = p.nama_proyek;
    document.getElementById('modal-konten').innerHTML = `
      <div class="flex gap-8 flex-wrap mb-16">
        <span class="badge badge-blue">${esc(p.lokasi)}</span>
        <span class="badge badge-amber">Tahun ${p.tahun}</span>
        <span class="badge badge-green">${formatRupiah(p.total_dengan_ppn)}</span>
        ${p.is_generated ? '<span class="badge badge-slate">Generated</span>' : ''}
      </div>
      <div class="table-wrap mb-16">
        <table>
          <thead><tr>
            <th style="width:50px">No</th>
            <th>Uraian Pekerjaan</th>
            <th class="c" style="width:80px">Satuan</th>
            <th class="r" style="width:110px">Volume</th>
            <th class="r" style="width:150px">Harga Satuan</th>
            <th class="r" style="width:150px">Jumlah</th>
          </tr></thead>
          <tbody>${rows}</tbody>
          <tfoot>
            <tr class="tr-subtotal">
              <td colspan="5" class="text-right">Subtotal Pekerjaan</td>
              <td class="r font-bold num">${formatRupiah(p.total_sebelum_ppn)}</td>
            </tr>
            <tr>
              <td colspan="5" class="text-right muted">PPN ${p.ppn_persen}%</td>
              <td class="r muted num">${formatRupiah(p.total_ppn)}</td>
            </tr>
            <tr class="tr-total">
              <td colspan="5" class="text-right">Total Biaya</td>
              <td class="r num">${formatRupiah(p.total_dengan_ppn)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div class="flex gap-8">
        <a class="btn btn-success" href="/api/export/rab/${p.id}">
          ${IC.download} Export Excel
        </a>
        <button class="btn btn-ghost" style="color:var(--red)"
          onclick="konfirmasiHapusProyek(${p.id},'${esc(p.nama_proyek)}');tutupModal()">
          ${IC.trash} Hapus
        </button>
        <button class="btn btn-ghost" onclick="tutupModal()">Tutup</button>
      </div>
    `;
    document.getElementById('modal-backdrop').classList.add('show');
  } catch (e) {
    tampilkanToast('Gagal memuat detail: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

function tutupModal() {
  document.getElementById('modal-backdrop').classList.remove('show');
}

async function konfirmasiHapusProyek(id, nama) {
  if (!confirm(`Hapus proyek "${nama}"?\n\nSemua data BOQ dan harga satuan akan ikut terhapus. Tindakan ini tidak bisa dibatalkan.`)) return;
  tampilkanLoading('Menghapus proyek...');
  try {
    const h = await apiFetch(`/api/proyek/${id}`, { method: 'DELETE' });
    tampilkanToast(h.pesan, 'success');
    muatSemuaProyek();
    muatDashboard();
  } catch (e) {
    tampilkanToast('Gagal menghapus: ' + e.message, 'error');
  } finally {
    sembunyikanLoading();
  }
}

// ── Init ──────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  muatDashboard();
  muatOpsiFilter();
});
