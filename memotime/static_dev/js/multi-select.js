class MultiSelect {
    constructor(element, options = {}) {
        let defaults = {
            placeholder: "Select item(s)",
            max: null,
            search: true,
            selectAll: false, // Изменено на false для одиночного выбора
            listAll: true,
            closeListOnItemSelect: true, // Изменено на true, чтобы закрывать список после выбора
            name: "",
            width: "",
            height: "",
            dropdownWidth: "",
            dropdownHeight: "",
            data: [],
            radio: true, // Изменено на true для радиокнопок (одиночный выбор)
            onChange: function () { },
            onSelect: function () { },
            onUnselect: function () { },
        };
        this.options = Object.assign(defaults, options);
        this.selectElement =
            typeof element === "string"
                ? document.querySelector(element)
                : element;
        for (const prop in this.selectElement.dataset) {
            if (this.options[prop] !== undefined) {
                this.options[prop] = this.selectElement.dataset[prop];
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

        // Создаем обертку для селекта
        this.wrapper = document.createElement("div");
        this.wrapper.classList.add("multi-select-wrapper");
        this.selectElement.parentNode.insertBefore(
            this.wrapper,
            this.selectElement,
        );
        this.wrapper.appendChild(this.selectElement);

        this.element = this._template();
        this.wrapper.appendChild(this.element);
        // Скрываем оригинальный select
        this.selectElement.style.display = "none";

        this._updateSelected();
        this._eventHandlers();
    }

    _template() {
        let optionsHTML = "";
        for (let i = 0; i < this.options.data.length; i++) {
            optionsHTML += `
                  <div class="multi-select-option${this.selectedValues.includes(this.options.data[i].value)
                    ? " multi-select-selected"
                    : ""
                }" data-value="${this.options.data[i].value}">
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
                      ${this.options.search === true ||
                this.options.search === "true"
                ? '<input type="text" class="multi-select-search" placeholder="Search...">'
                : ""
            }
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
        this.element.querySelectorAll(".multi-select-option").forEach((option) => {
            option.onclick = () => {
                // Снимаем выделение со всех опций
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((opt) => {
                        opt.classList.remove("multi-select-selected");
                    });

                let selected = true;
                if (!option.classList.contains("multi-select-selected")) {
                    option.classList.add("multi-select-selected");

                    // Обновляем оригинальный select
                    this.selectElement.value = option.dataset.value;

                    this.options.data.forEach((data) => {
                        data.selected = data.value == option.dataset.value;
                    });
                } else {
                    // Для радиокнопок снятие выделения не требуется, так как всегда выбран только один вариант
                    selected = false;
                }

                // Обновляем заголовок и плейсхолдер
                this._updateHeader();

                if (
                    this.options.search === true ||
                    this.options.search === "true"
                ) {
                    this.element.querySelector(".multi-select-search").value = "";
                }
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((option) => (option.style.display = "flex"));
                if (
                    this.options.closeListOnItemSelect === true ||
                    this.options.closeListOnItemSelect === "true"
                ) {
                    headerElement.classList.remove("multi-select-header-active");
                }
                this.options.onChange(
                    option.dataset.value,
                    option.querySelector(".multi-select-option-text").innerHTML,
                    option,
                );
                if (selected) {
                    this.options.onSelect(
                        option.dataset.value,
                        option.querySelector(".multi-select-option-text").innerHTML,
                        option,
                    );
                } else {
                    this.options.onUnselect(
                        option.dataset.value,
                        option.querySelector(".multi-select-option-text").innerHTML,
                        option,
                    );
                }
            };
        });
        headerElement.onclick = () =>
            headerElement.classList.toggle("multi-select-header-active");
        if (this.options.search === true || this.options.search === "true") {
            let search = this.element.querySelector(".multi-select-search");
            search.oninput = () => {
                this.element
                    .querySelectorAll(".multi-select-option")
                    .forEach((option) => {
                        option.style.display =
                            option
                                .querySelector(".multi-select-option-text")
                                .innerHTML.toLowerCase()
                                .indexOf(search.value.toLowerCase()) > -1
                                ? "flex"
                                : "none";
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
        // Устанавливаем начальное значение
        if (this.selectedValues.length > 0) {
            let selectedValue = this.selectedValues[0];
            let selectedOption = this.element.querySelector(
                `.multi-select-option[data-value="${selectedValue}"]`,
            );
            if (selectedOption) {
                selectedOption.classList.add("multi-select-selected");
                this.selectElement.value = selectedValue; // Устанавливаем значение в оригинальном select
            }
        }
        this._updateHeader();
    }

    _updateHeader() {
        let headerElement = this.element.querySelector(".multi-select-header");
        let selectedOption = this.element.querySelector(
            ".multi-select-option.multi-select-selected",
        );

        // Очищаем заголовок перед обновлением
        headerElement.innerHTML = "";

        if (selectedOption) {
            headerElement.innerHTML = selectedOption.querySelector(
                ".multi-select-option-text",
            ).innerHTML;
        } else {
            headerElement.innerHTML = `<span class="multi-select-header-placeholder">${this.options.placeholder}</span>`;
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

document.querySelectorAll("[data-multi-select]").forEach((select) => new MultiSelect(select));