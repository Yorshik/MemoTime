class CustomFileUpload {
  constructor(element) {
    this.wrapper = element;
    this.input = element.querySelector('input[type="file"]');
    this.trigger = element.querySelector('.custom-file-upload-trigger');
    this.uploadText = element.querySelector('.upload-text');
    this.fileList = element.querySelector('.file-list');
    this.resetButton = element.querySelector('.clear-selection');
    // Конфигурация
    this.maxFiles = parseInt(this.input.dataset.maxFiles) || Infinity;
    this.maxSize = parseInt(this.input.dataset.maxSize) || Infinity;
    this.acceptedTypes = this.input.dataset.acceptedTypes ? this.input.dataset.acceptedTypes.split(',') : null;
    // Локализованные тексты
    this.texts = {
      select: this.input.dataset.uploadText || 'Выберите файлы или перетащите их сюда',
      selected: this.input.dataset.selectedText || 'Выбрано файлов: {count}',
      maxFiles: this.input.dataset.maxFilesText || 'Максимальное количество файлов: {max_files}',
      maxSize: this.input.dataset.maxSizeText || 'Максимальный размер файла: {max_size}',
      invalidType: this.input.dataset.invalidTypeText || 'Неподдерживаемый тип файла',
      tooLarge: this.input.dataset.tooLargeText || 'Файл слишком большой'
    };
    this.bindEvents();
  }

  bindEvents() {
    this.resetButton.hidden = false;
    this.uploadText.textContent = this.texts.select;
    this.input.addEventListener('change', (e) => this.handleFiles(e.target.files));
    this.trigger.addEventListener('dragover', (e) => {
      e.preventDefault();
      this.trigger.classList.add('dragover');
    });
    this.trigger.addEventListener('dragleave', (e) => {
      e.preventDefault();
      this.trigger.classList.remove('dragover');
    });
    this.trigger.addEventListener('drop', (e) => {
      e.preventDefault();
      this.trigger.classList.remove('dragover');
      this.handleFiles(e.dataTransfer.files);
    });
    this.fileList.addEventListener('click', (e) => {
      if (e.target.closest('.remove-file')) {
        const item = e.target.closest('.file-item');
        const index = Array.from(this.fileList.children).indexOf(item);
        this.removeFile(index);
      }
    });
    this.resetButton.addEventListener('click', () => {
      this.resetFiles();
    });
  }
  handleFiles(fileList) {
    const existingFiles = Array.from(this.input.files);
    const newFiles = Array.from(fileList);
    const files = existingFiles.concat(newFiles).filter((file, index, self) =>
      index === self.findIndex((f) => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified)
    );
    if (files.length > this.maxFiles) {
      this.showError(this.texts.maxFiles.replace('{max_files}', this.maxFiles));
      return;
    }
    const validFiles = files.filter(file => {
      if (file.size > this.maxSize) {
        this.showError(this.texts.tooLarge.replace('{max_size}', this.formatSize(this.maxSize)));
        return false;
      }
      if (this.acceptedTypes && !this.acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return file.name.toLowerCase().endsWith(type.toLowerCase());
        }
        return file.type.match(new RegExp(type.replace('*', '.*')));
      })) {
        this.showError(this.texts.invalidType);
        return false;
      }
      return true;
    });
    const dt = new DataTransfer();
    validFiles.forEach(file => dt.items.add(file));
    this.input.files = dt.files;
    this.updateFileList();
  }
  updateFileList() {
    const files = Array.from(this.input.files);
    this.fileList.innerHTML = '';
    if (files.length > 0) {
      this.uploadText.textContent = this.texts.selected.replace('{count}', files.length);
      this.resetButton.style.display = files.length > 2 ? 'inline-block' : 'none';

      files.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
          <div class="file-info">
            <svg class="file-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
              <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
            <span class="file-name">${file.name}</span>
            <span class="file-size">${this.formatSize(file.size)}</span>
          </div>
          <button type="button" class="remove-file" aria-label="${this.texts.remove}">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        `;
        this.fileList.appendChild(item);
      });
    } else {
      this.uploadText.textContent = this.texts.select;
      this.resetButton.style.display = 'none';
    }
  }
  removeFile(index) {
    const dt = new DataTransfer();
    const files = Array.from(this.input.files);
    files.forEach((file, i) => {
      if (i !== index) dt.items.add(file);
    });
    this.input.files = dt.files;
    this.updateFileList();
  }
  resetFiles() {
    this.input.value = '';
    this.updateFileList();
  }
  formatSize(bytes) {
    if (bytes === 0) return '0 Б';
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  }
  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'file-error';
    errorDiv.textContent = message;
    const existingError = this.wrapper.querySelector('.file-error');
    if (existingError) {
      existingError.remove();
    }
    this.wrapper.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
  }
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.custom-file-upload').forEach(element => {
    new CustomFileUpload(element);
  });
});
