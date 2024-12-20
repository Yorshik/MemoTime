__all__ = ()


class BaseForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_form_control_class()

    def add_form_control_class(self):
        for field in self.visible_fields():
            existing_class = field.field.widget.attrs.get("class", "")
            if "form-control" not in existing_class:
                field.field.widget.attrs["class"] = (
                    f"{existing_class} form-control".strip()
                )
