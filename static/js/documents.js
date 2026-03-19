/**
 * Documents Module - File upload, download, and search
 */
const Documents = {
    documents: [],

    async init() {
        await this.loadDocuments();
    },

    async loadDocuments() {
        try {
            const data = await API.get('/documents');
            if (data) {
                this.documents = data.documents || [];
                this.render();
            }
        } catch (error) {
            Toast.error('Không thể tải danh sách tài liệu');
        }
    },

    render() {
        const container = document.getElementById('documents-list');
        if (!container) return;

        if (this.documents.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-folder-open empty-state-icon"></i><p class="empty-state-text">Chưa có tài liệu nào</p><p class="empty-state-hint">Giảng viên có thể tải lên tài liệu học tập</p></div>`;
            return;
        }

        container.innerHTML = this.documents.map(doc => {
            const iconMap = {
                pdf: 'fas fa-file-pdf',
                doc: 'fas fa-file-word', docx: 'fas fa-file-word',
                xls: 'fas fa-file-excel', xlsx: 'fas fa-file-excel',
                ppt: 'fas fa-file-powerpoint', pptx: 'fas fa-file-powerpoint',
                zip: 'fas fa-file-archive', rar: 'fas fa-file-archive',
                png: 'fas fa-file-image', jpg: 'fas fa-file-image', jpeg: 'fas fa-file-image',
                txt: 'fas fa-file-alt',
            };
            const typeClass = {
                pdf: 'pdf', doc: 'doc', docx: 'doc', xls: 'xls', xlsx: 'xls',
                ppt: 'ppt', pptx: 'ppt',
            };
            const icon = iconMap[doc.file_type] || 'fas fa-file';
            const cls = typeClass[doc.file_type] || 'default';

            return `
                <div class="doc-card fade-in">
                    <div class="doc-icon ${cls}">
                        <i class="${icon}"></i>
                    </div>
                    <div class="doc-info">
                        <div class="doc-title">${doc.title}</div>
                        <div class="doc-meta">
                            <span><i class="fas fa-user"></i> ${doc.uploader_name || ''}</span>
                            <span><i class="fas fa-hdd"></i> ${formatFileSize(doc.file_size)}</span>
                            <span><i class="fas fa-download"></i> ${doc.download_count} lượt tải</span>
                            ${doc.course_name ? `<span><i class="fas fa-book"></i> ${doc.course_name}</span>` : ''}
                        </div>
                    </div>
                    <div class="doc-actions">
                        <button class="btn-primary-custom" style="padding:8px 14px;font-size:0.75rem;" onclick="Documents.download(${doc.id})">
                            <i class="fas fa-download"></i> Tải xuống
                        </button>
                        <button class="btn-danger" style="padding:8px 14px;font-size:0.75rem;" onclick="Documents.deleteDoc(${doc.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    },

    showUploadModal() {
        const modal = document.getElementById('uploadModal');
        document.getElementById('uploadForm').reset();
        bootstrap.Modal.getOrCreateInstance(modal).show();
    },

    async submitUpload(e) {
        e.preventDefault();
        const form = document.getElementById('uploadForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/documents', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${API.getToken()}`,
                },
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);

            Toast.success('Tải tài liệu lên thành công');
            bootstrap.Modal.getOrCreateInstance(document.getElementById('uploadModal')).hide();
            await this.loadDocuments();
        } catch (error) {
            Toast.error(error.message || 'Tải lên thất bại');
        }
    },

    async download(docId) {
        try {
            const token = API.getToken();
            const a = document.createElement('a');
            a.href = `/api/documents/${docId}/download?token=${token}`;

            // Use fetch to download with auth
            const response = await fetch(`/api/documents/${docId}/download`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            a.href = url;

            const disposition = response.headers.get('Content-Disposition');
            const filename = disposition ? disposition.split('filename=')[1]?.replace(/"/g, '') : 'file';
            a.download = filename;

            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            // Reload to update download count
            await this.loadDocuments();
        } catch (error) {
            Toast.error('Không thể tải xuống tài liệu');
        }
    },

    async deleteDoc(docId) {
        if (!confirm('Bạn có chắc muốn xóa tài liệu này?')) return;
        try {
            await API.delete(`/documents/${docId}`);
            Toast.success('Xóa tài liệu thành công');
            await this.loadDocuments();
        } catch (error) {
            Toast.error('Không thể xóa tài liệu');
        }
    },

    async search() {
        const query = document.getElementById('doc-search').value.trim();
        if (!query) {
            await this.loadDocuments();
            return;
        }

        try {
            const data = await API.get(`/documents/search?q=${encodeURIComponent(query)}`);
            if (data) {
                this.documents = data.documents || [];
                this.render();
            }
        } catch (error) {
            Toast.error('Tìm kiếm thất bại');
        }
    },
};
