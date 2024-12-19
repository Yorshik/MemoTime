__all__ = ()


class BaseForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_form_control_class()

    def add_form_control_class(self):
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"
