class MultiSelect {
    constructor(element, options = {}) {
        let defaults = {
            placeholder: "Select item(s)",
            max: null,
            search: false,
            selectAll: false,
            listAll: true,
            closeListOnItemSelect: true,
            name: "",
            width: "",
            height: "",
            dropdownWidth: "",
            dropdownHeight: "",
            data: [],
            radio: false,
            allowUnselectRadio: false,
            onChange: function () { },
            onSelect: function () { },
            onUnselect: function () { },
        };
        this.options = Object.assign(defaults, options);
        this.selectElement =
            typeof element === "string"
                ? document.querySelector(element)
                : element;

        if (!this.selectElement) {
            console.error("Error: select element not found.", element);
            return;
        }

        for (const prop in this.selectElement.dataset) {
            if (this.options[prop] !== undefined) {
                if (this.selectElement.dataset[prop] === "true") {
                    this.options[prop] = true;
                } else if (this.selectElement.dataset[prop] === "false") {
                    this.options[prop] = false;
                } else {
                    this.options[prop] = this.selectElement.dataset[prop];
                }
            }
        }

        this.name = this.selectElement.getAttribute("name")
            ? this.selectElement.getAttribute("name")
            : "multi-select-" + Math.floor(Math.random() * 1000000);

        if (!this.options.data.length) {
            let options = this.selectElement.querySelectorAll("option");
            for (let i = 0; i < options.length; i++) {
                this.options.data.push({
                    value: options[i].value,
                    text: options[i].innerHTML,
                    selected: options[i].selected,
                    html: options[i].getAttribute("data-html"),
                });
            }
        }

        this.wrapper = document.createElement("div");
        this.wrapper.classList.add("multi-select-wrapper");
        this.selectElement.parentNode.insertBefore(
            this.wrapper,
            this.selectElement,
        );
        this.wrapper.appendChild(this.selectElement);

        this.element = this._template();
        this.wrapper.appendChild(this.element);
        this.selectElement.style.display = "none";

        this._updateSelected();
        this._eventHandlers();

        // Скрываем пустой элемент при инициализации
        this._hideEmptyOption();
    }

    _template() {
        let optionsHTML = "";
        for (let i = 0; i < this.options.data.length; i++) {
            optionsHTML += `
                  <div class="multi-select-option${this.selectedValues.includes(this.options.data[i].value)
                    ? " multi-select-selected"
                    : ""
                }" data-value="${this.options.data[i].value}" ${this.options.data[i].value === "" ? 'style="display: none;"' : ''}>
                      <span class="multi-select-option-radio"></span>
                      <span class="multi-select-option-text">${this.options.data[i].html
                    ? this.options.data[i].html
                    : this.options.data[i].text
                }</span>
                  </div>
              `;
        }
        let selectAllHTML = "";
        if (
            this.options.selectAll === true ||
            this.options.selectAll === "true"
        ) {
            selectAllHTML = `<div class="multi-select-all">
                  <span class="multi-select-option-radio"></span>
                  <span class="multi-select-option-text">Select all</span>
              </div>`;
        }
        let searchHTML = this.options.search === true || this.options.search === "true"
            ? '<input type="text" class="multi-select-search" placeholder="Search...">'
            : "";
        let template = `
              <div class="multi-select ${this.name
            }"${this.selectElement.id ? ' id="' + this.selectElement.id + '-ms"' : ""
            } style="${this.options.width ? "width:" + this.options.width + ";" : ""}${this.options.height ? "height:" + this.options.height + ";" : ""
            }">
                  <div class="multi-select-header" style="${this.options.width
                ? "width:" + this.options.width + ";"
                : ""
            }${this.options.height ? "height:" + this.options.height + ";" : ""}">
                      <span class="multi-select-header-placeholder">${this.options.placeholder
            }</span>
                  </div>
                  <div class="multi-select-options" style="${this.options.dropdownWidth
                ? "width:" + this.options.dropdownWidth + ";"
                : ""
            }${this.options.dropdownHeight
                ? "height:" + this.options.dropdownHeight + ";"
                : ""
            }">
                        ${searchHTML}
                        ${selectAllHTML}
                        ${optionsHTML}
                  </div>
              </div>
          `;
        let element = document.createElement("div");
        element.innerHTML = template;
        return element.firstElementChild;
    }

    _eventHandlers() {
        let headerElement = this.element.querySelector(".multi-select-header");
        let optionsContainer = this.element.querySelector(".multi-select-options");

        optionsContainer.onclick = (event) => {
            const clickedOption = event.target.closest(".multi-select-option");

            if (clickedOption) {
                const isSelected = clickedOption.classList.contains("multi-select-selected");
                let optionSelected = false;
                let shouldCloseDropdown = false;

                if (this.options.radio === true || this.options.radio === 'true') {
                    if (this.options.allowUnselectRadio === true || this.options.allowUnselectRadio === 'true') {
                        if (isSelected) {
                            clickedOption.classList.remove("multi-select-selected");
                            this.options.data.find(data => data.value === clickedOption.dataset.value).selected = false;
                            this.selectElement.value = "";
                            this.options.onUnselect(clickedOption.dataset.value, clickedOption.querySelector(".multi-select-option-text").innerHTML, clickedOption);
                            shouldCloseDropdown = true;

                            // Выбираем невидимое поле, если убран селект в radio режиме
                            this._selectEmptyOption();
                        } else {
                            this.element
                                .querySelectorAll(".multi-select-option.multi-select-selected")
                                .forEach(opt => {
                                    opt.classList.remove("multi-select-selected");
                                });
                            this.options.data.forEach(data => data.selected = false);

                            clickedOption.classList.add("multi-select-selected");
                            this.options.data.find(data => data.value === clickedOption.dataset.value).selected = true;
                            this.selectElement.value = clickedOption.dataset.value;
                            this.options.onSelect(clickedOption.dataset.value, clickedOption.querySelector(".multi-select-option-text").innerHTML, clickedOption);
                            optionSelected = true;
                            shouldCloseDropdown = true;
                        }
                    } else {
                        if (!isSelected) {
                            this.element
                                .querySelectorAll(".multi-select-option.multi-select-selected")
                                .forEach(opt => {
                                    opt.classList.remove("multi-select-selected");
                                });
                            this.options.data.forEach(data => data.selected = false);

                            clickedOption.classList.add("multi-select-selected");
                            this.options.data.find(data => data.value === clickedOption.dataset.value).selected = true;
                            this.selectElement.value = clickedOption.dataset.value;
                            this.options.onSelect(clickedOption.dataset.value, clickedOption.querySelector(".multi-select-option-text").innerHTML, clickedOption);
                            optionSelected = true;
                            shouldCloseDropdown = true;
                        }
                    }
                } else {
                    if (isSelected) {
                        clickedOption.classList.remove("multi-select-selected");
                        this.options.data.find(data => data.value === clickedOption.dataset.value).selected = false;
                        this.options.onUnselect(clickedOption.dataset.value, clickedOption.querySelector(".multi-select-option-text").innerHTML, clickedOption);
                        shouldCloseDropdown = true;
                    } else {
                        clickedOption.classList.add("multi-select-selected");
                        this.options.data.find(data => data.value === clickedOption.dataset.value).selected = true;
                        this.options.onSelect(clickedOption.dataset.value, clickedOption.querySelector(".multi-select-option-text").innerHTML, clickedOption);
                        optionSelected = true;
                        shouldCloseDropdown = true;
                    }
                }

                this._updateHeader();

                if (
                    this.options.search === true ||
                    this.options.search === "true"
                ) {
                    this.element.querySelector(".multi-select-search").value = "";
                }
                // Изменения здесь: убираем установку display: flex для всех элементов
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((opt) => {
                        if (opt.dataset.value !== "") {
                            opt.style.display = "flex";
                        }
                    });

                if (this.options.closeListOnItemSelect === true || this.options.closeListOnItemSelect === "true") {
                    if (shouldCloseDropdown) {
                        headerElement.classList.remove("multi-select-header-active");
                    }
                }

                this.options.onChange(
                    clickedOption.dataset.value,
                    clickedOption.querySelector(".multi-select-option-text").innerHTML,
                    clickedOption,
                );
            }
        };

        headerElement.onclick = () =>
            headerElement.classList.toggle("multi-select-header-active");

        if (this.options.search === true || this.options.search === "true") {
            let search = this.element.querySelector(".multi-select-search");
            search.oninput = () => {
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((option) => {
                        // Изменения здесь: не устанавливаем display: flex для пустого элемента
                        if (option.dataset.value !== "") {
                            option.style.display =
                                option
                                    .querySelector(".multi-select-option-text")
                                    .innerHTML.toLowerCase()
                                    .indexOf(search.value.toLowerCase()) > -1
                                    ? "flex"
                                    : "none";
                        }
                    });
            };
        }

        if (
            this.options.selectAll === true ||
            this.options.selectAll === "true"
        ) {
            let selectAllButton = this.element.querySelector(".multi-select-all");
            selectAllButton.onclick = () => {
                let allSelected =
                    selectAllButton.classList.contains("multi-select-selected");
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((option) => {
                        let dataItem = this.options.data.find(
                            (data) => data.value == option.dataset.value,
                        );
                        if (
                            dataItem &&
                            ((allSelected && dataItem.selected) ||
                                (!allSelected && !dataItem.selected))
                        ) {
                            option.click();
                        }
                    });
                selectAllButton.classList.toggle("multi-select-selected");
            };
        }

        if (
            this.selectElement.id &&
            document.querySelector('label[for="' + this.selectElement.id + '"]')
        ) {
            document.querySelector(
                'label[for="' + this.selectElement.id + '"]',
            ).onclick = () => {
                headerElement.classList.toggle("multi-select-header-active");
            };
        }

        document.addEventListener("click", (event) => {
            if (
                !event.target.closest("." + this.name) &&
                !event.target.closest(
                    'label[for="' + this.selectElement.id + '"]',
                )
            ) {
                headerElement.classList.remove("multi-select-header-active");
            }
        });
    }

    _updateSelected() {
        this.options.data.forEach(data => {
            const optionElement = this.selectElement.querySelector(`option[value="${data.value}"]`);
            if (optionElement && optionElement.selected) {
                data.selected = true;
                const displayOption = this.element.querySelector(`.multi-select-option[data-value="${data.value}"]`);
                if (displayOption) {
                    displayOption.classList.add("multi-select-selected");
                }
            }
        });

        if (this.options.radio === true && this.selectElement.value === "") {
            this.element.querySelector(".multi-select-header").innerHTML = `<span class="multi-select-header-placeholder">${this.options.placeholder}</span>`;
        } else {
            this._updateHeader();
        }
    }

    _updateHeader() {
        let headerElement = this.element.querySelector(".multi-select-header");
        let selectedOptions = this.element.querySelectorAll(
            ".multi-select-option.multi-select-selected",
        );

        // Если выбрано невидимое поле, отображаем плейсхолдер
        if (this.options.radio && this.selectedValues.includes("")) {
            headerElement.innerHTML = `<span class="multi-select-header-placeholder">${this.options.placeholder}</span>`;
        } else if (selectedOptions.length > 0) {
            let selectedTexts = [];
            selectedOptions.forEach(option => {
                if (option.dataset.value !== "") {
                    selectedTexts.push(option.querySelector(".multi-select-option-text").innerHTML);
                }
            });
            if (selectedTexts.length === 0) {
                headerElement.innerHTML = `<span class="multi-select-header-placeholder">${this.options.placeholder}</span>`;
            } else {
                headerElement.innerHTML = selectedTexts.join(", ");
            }
        } else {
            headerElement.innerHTML = `<span class="multi-select-header-placeholder">${this.options.placeholder}</span>`;
        }
    }

    // Метод для скрытия пустого поля
    _hideEmptyOption() {
        const emptyOption = this.element.querySelector('.multi-select-option[data-value=""]');
        if (emptyOption) {
            emptyOption.style.display = "none";
        }
    }

    // Метод для выбора пустого поля
    _selectEmptyOption() {
        const emptyOption = this.element.querySelector('.multi-select-option[data-value=""]');
        if (emptyOption) {
            // Снимаем выделение со всех остальных опций
            this.element.querySelectorAll('.multi-select-option.multi-select-selected').forEach(option => {
                option.classList.remove('multi-select-selected');
            });

            // Выбираем пустое поле
            emptyOption.classList.add('multi-select-selected');
            this.options.data.forEach(data => data.selected = false);
            const emptyData = this.options.data.find(data => data.value === "");
            if (emptyData) {
                emptyData.selected = true;
            }
            this.selectElement.value = "";
            this._updateHeader();
        }
    }

    get selectedValues() {
        return this.options.data
            .filter((data) => data.selected)
            .map((data) => data.value);
    }

    get selectedItems() {
        return this.options.data.filter((data) => data.selected);
    }

    set data(value) {
        this.options.data = value;
    }

    get data() {
        return this.options.data;
    }

    set selectElement(value) {
        this.options.selectElement = value;
    }

    get selectElement() {
        return this.options.selectElement;
    }

    set element(value) {
        this.options.element = value;
    }

    get element() {
        return this.options.element;
    }

    set placeholder(value) {
        this.options.placeholder = value;
    }

    get placeholder() {
        return this.options.placeholder;
    }

    set name(value) {
        this.options.name = value;
    }

    get name() {
        return this.options.name;
    }

    set width(value) {
        this.options.width = value;
    }

    get width() {
        return this.options.width;
    }

    set height(value) {
        this.options.height = value;
    }

    get height() {
        return this.options.height;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOMContentLoaded event fired");

    document.querySelectorAll("select.selectpicker").forEach((select) => {
        console.log("Initializing MultiSelect for (selectpicker):", select);

        new MultiSelect(select);
    });
});